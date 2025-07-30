from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Union
from clickhouse_connect import get_client
from contextlib import contextmanager
import json
import time
from functools import wraps
from abc import ABC, abstractmethod
from dataflow.utils.utils import get_logger
from dataflow.data.storage import DataFlowStorage
import re
import ast

def singleton(cls):
    """单例模式装饰器"""
    _instances = {}
    
    @wraps(cls)
    def get_instance(*args, **kwargs):
        if cls not in _instances:
            _instances[cls] = cls(*args, **kwargs)
        return _instances[cls]
    
    return get_instance

@dataclass
class DatabaseConfig:
    host: str = 'localhost'
    port: int = 9000
    db_name: str = ''
    table_name: str = ''
    username: Optional[str] = None
    password: Optional[str] = None


class DatabaseError(Exception):
    """数据库操作异常"""
    pass

@singleton
class MyScaleStorage(DataFlowStorage, ABC):
    def __init__(self, config: DatabaseConfig):
        """初始化存储实例
        
        Args:
            config: 数据库配置
        """
        if not hasattr(self, '_initialized'):
            self.config = config
            self._client = None
            self.logger = get_logger()
            self._initialized = True
        
    @property
    def client(self):
        """懒加载数据库连接"""
        if self._client is None:
            self._client = get_client(
                host=self.config.host,
                port=self.config.port,
                username=self.config.username,
                password=self.config.password,
                database=self.config.db_name,
                settings={'allow_experimental_object_type': 1}
            )
        return self._client

    def read(self, key_list: list, type=None):
        # 读一整列 / 读n列
        # TODO Try Except
        read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name}"

        rows = self.client.query(read_sql)
        value_list = [dict(zip(key_list, row)) for row in rows.result_rows]
        return value_list
    
    def read_by_id(self, id_list):
        self.logger.info(f"Reading data from {self.config.db_name}.{self.config.table_name} with id_list = {id_list}")
        read_sql = f'SELECT * FROM {self.config.db_name}.{self.config.table_name} WHERE id IN %(ids)s'
        rows, column_info= self.client.query(read_sql, {'ids': tuple(id_list)}, with_column_types=True)
        column_names = [col[0] for col in column_info]
        value_list = [dict(zip(column_names, row)) for row in rows.result_rows]
        return value_list

    def read_code(self, key_list, **kwargs):
        
        key_list.append('id')
        self.logger.info(f"Reading Code data from {self.config.db_name}.{self.config.table_name} where stage = {kwargs['stage']}, key_list = {key_list}")
        
        read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name} WHERE category == 'reasoning' and stage == {kwargs['stage']} and format == '{kwargs['format']}' and Synthetic == '{kwargs['syn']}'"
        
        rows = self.client.query(read_sql)
        value_list = [dict(zip(key_list, row)) for row in rows.result_rows]
        self.logger.info(f"Returning {value_list}")
        return value_list

    def read_code_json(self, key_list, **kwargs):
        
        key_list.append('id')
        self.logger.info(f"Reading Code data from {self.config.db_name}.{self.config.table_name} where stage = {kwargs['stage']}, key_list = {key_list}")
        if 'maxmin_scores' in kwargs.keys():
            score_sql = ' and '.join([f"eval_score_{i+1} BETWEEN {_['min_score']} AND {_['max_score']}" for i, _ in enumerate(kwargs['maxmin_scores'])])
            read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name} WHERE category == 'reasoning' and stage == {kwargs['stage']} and format == '{kwargs['format']}' and Synthetic == '{kwargs['syn']}' and {score_sql}"
        else:
            read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name} WHERE category == 'reasoning' and stage == {kwargs['stage']} and format == '{kwargs['format']}' and Synthetic == '{kwargs['syn']}'"
        rows = self.client.query(read_sql)
        value_list = [dict(zip(key_list, row)) for row in rows.result_rows]
        for item in value_list:
            print(item['data'])
            item['data'] = json.loads(item['data'])
        # self.logger.debug(f"Returning {value_list}")
        return value_list

    def write_data(self, data, **kwargs):
        values = self.read_by_id([_['id'] for _ in data])
        assert len(data) == len(values), f'Len Not Equal!'
        
        for i in range(len(data)):
            values[i]['data'] = json.dumps(data[i])
            for k, v in kwargs.items():
                values[i][k] = v
            del values[i]['id']
        keys = values[0].keys()
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} ({', '.join(keys)}) VALUES"
        # self.logger.info(f"Writing Eval data to {self.db_name}.{self.table_name} where algo = {kwargs['algo_name']} and score_key = {kwargs['score_key']}")
        self.client.command(write_sql, values)
        delete_sql = f"ALTER TABLE {self.config.db_name}.{self.config.table_name} DELETE WHERE id IN ({[_['id'] for _ in data]})"
        self.client.command(delete_sql)
        
    def write_eval(self, data, **kwargs): ## must have name and score_key
        values = self.read_by_id([_['id'] for _ in data])
        
        assert len(data) == len(values), f'Len Not Equal!'
        for i in range(len(data)):
            values[i]['stage'] += 1
            values[i][f"eval_algorithm_{values[i]['stage']}"] = kwargs['algo_name']
            values[i][f"eval_score_{values[i]['stage']}"] = data[i][kwargs['score_key']]
            if 'info_key' in kwargs:
                values[i][f"eval_info_{values[i]['stage']}"] = data[i][kwargs['info_key']]
            del values[i]['id']
        keys = values[0].keys()
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} ({', '.join(keys)}) VALUES"
        self.logger.info(f"Writing Eval data to {self.config.db_name}.{self.config.table_name} where algo = {kwargs['algo_name']} and score_key = {kwargs['score_key']}")
        self.client.command(write_sql, values)
        delete_sql = f"ALTER TABLE {self.config.db_name}.{self.config.table_name} DELETE WHERE id IN ({[_['id'] for _ in data]})"
        self.client.command(delete_sql)
        
    def write_code(self, data: list, **kwargs): 
        # + pt data
        rows = [{"data": _, "category": "reasoning", "format": kwargs['format'], "Synthetic": kwargs['syn']} for _ in data]
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} (data, category, format, Synthetic) VALUES"
        self.logger.info(f"Writing Code data to {self.config.db_name}.{self.config.table_name} where format = {kwargs['format']} and syn = {kwargs['syn']}")
        self.client.command(write_sql, rows)
        
    def write_code_json(self, data: list, **kwargs):
        # + sft data
        rows = [{"data": _['data'], "raw_data_id": _['id'], "category": "reasoning", "format": kwargs['format'], "Synthetic": kwargs['syn']} for _ in data]
        for item in rows:
            item['data'] = json.dumps(item['data'])
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} (data, raw_data_id, category, format, Synthetic) VALUES"
        self.logger.info(f"Writing Code data to {self.config.db_name}.{self.config.table_name} where format = {kwargs['format']} and syn = {kwargs['syn']}")
        self.client.command(write_sql, rows)

    def write(self, key: str, type, data: list):
        
        # 往一整列写
        # 写一个数据 
        self.logger.info(f"Writing {len(data)} to {key} column...")
        
        self.logger.debug(f"Reading data from {self.config.db_name}.{self.config.table_name}...")

        read_sql = f"""
        SELECT * 
        FROM {self.config.db_name}.{self.config.table_name}
        """

        rows, columns = self.client.query(read_sql, with_column_types=True)

        col_names = [col[0] for col in columns]
        old_data = [dict(zip(col_names, row)) for row in rows.result_rows]
        new_data = []
        for item, new_value in zip(old_data, data):
            item[key] = new_value
            new_data.append(item)

        updated_rows = [tuple(d[col] for col in col_names) for d in new_data]

        delete_sql = f"""
        ALTER TABLE {self.config.db_name}.{self.config.table_name}
        DELETE WHERE 1=1
        """

        self.logger.debug(f"deleting data from {self.config.db_name}.{self.config.table_name}...")

        self.client.command(delete_sql)

        self.logger.debug(f"Inserting new data into {self.config.db_name}.{self.config.table_name}...")

        self.client.command(f"INSERT INTO {self.config.db_name}.{self.config.table_name} ({', '.join(col_names)}) VALUES", updated_rows)

        self.logger.info(f"Successfully insert {len(data)} into {key} column")
        """获取所有列名"""
        schema_query = f"DESCRIBE {self.config.db_name}.{self.config.table_name}"
        result = self.client.query(schema_query)
        return [row[0] for row in result.result_rows]

    def close(self):
        """关闭数据库连接"""
        if self._client:
            self._client.disconnect()
            self._client = None

    def __del__(self):
        """析构时确保关闭连接"""
        self.close()

    def clean_json_str(self, s):
        # 去除非法控制字符（除了常规的 \n \r \t）
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
        return s

