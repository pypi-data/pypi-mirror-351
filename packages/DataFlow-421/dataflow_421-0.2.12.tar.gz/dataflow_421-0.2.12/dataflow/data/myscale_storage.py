from dataclasses import dataclass
from typing import Optional
from clickhouse_driver import Client
import json
from functools import wraps
from abc import ABC
from dataflow.utils.utils import get_logger
from dataflow.data.storage import DataFlowStorage
import re

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
            self._client = Client(
                host=self.config.host,
                port=self.config.port,
                user=self.config.username,
                password=self.config.password,
                database=self.config.db_name,
                settings={'allow_experimental_object_type': 1}
            )

        return self._client
    
    def read_by_id(self, id_list):
        self.logger.info(f"Reading data from {self.config.db_name}.{self.config.table_name} with id_list = {id_list}")
        read_sql = f'SELECT * FROM {self.config.db_name}.{self.config.table_name} WHERE id IN %(ids)s'
        rows, column_info= self.client.execute(read_sql, {'ids': tuple(id_list)}, with_column_types=True)
        column_names = [col[0] for col in column_info]
        value_list = [dict(zip(column_names, row)) for row in rows]

        return value_list

    def read_json(self, key_list, **kwargs):
        key_list.append('id')
        self.logger.info(f"Reading json data from {self.config.db_name}.{self.config.table_name} where category == {kwargs['category']}, \
                stage = {kwargs['stage']}, key_list = {key_list}, pipeline_id = {kwargs['pipeline_id']}, \
                eval_stage = {kwargs['eval_stage']}")
        if 'maxmin_scores' in kwargs.keys():
            score_sql = ' and '.join([f"eval_score_{i+1} BETWEEN {_['min_score']} AND {_['max_score']}" for i, _ in enumerate(kwargs['maxmin_scores'])])
            read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name} WHERE category == '{kwargs['category']}' and \
                stage == {kwargs['stage']} and format == '{kwargs['format']}' and Synthetic == '{kwargs['syn']}' and pipeline_id == '{kwargs['pipeline_id']}' and \
                eval_stage == {kwargs['eval_stage']} and {score_sql}"
        else:
            read_sql = f"SELECT {', '.join(key_list)} FROM {self.config.db_name}.{self.config.table_name} WHERE category == '{kwargs['category']}' and \
                stage == {kwargs['stage']} and format == '{kwargs['format']}' and Synthetic == '{kwargs['syn']}' and pipeline_id == '{kwargs['pipeline_id']}' and \
                eval_stage == {kwargs['eval_stage']}"
        rows = self.client.execute(read_sql)
        value_list = [dict(zip(key_list, row)) for row in rows]
        for item in value_list:
            print(item['data'])
            item['data'] = json.loads(item['data'])
        # self.logger.debug(f"Returning {value_list}")

        return value_list

    def write_json(self, data: list, **kwargs):
        # + sft data
        rows = [{"data": _['data'], "raw_data_id": _['id'], "category": kwargs['category'], "pipeline_id": kwargs['pipeline_id'], "stage": kwargs['stage'], "format": kwargs['format'], "Synthetic": kwargs['syn']} for _ in data]
        for item in rows:
            item['data'] = json.dumps(item['data'])
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} (data, raw_data_id, category, pipeline_id, stage, format, Synthetic) VALUES"
        self.logger.info(f"Writing json data to {self.config.db_name}.{self.config.table_name} where format = {kwargs['format']} and syn = {kwargs['syn']} and pipeline_id = {kwargs['pipeline_id']} and stage = {kwargs['stage']}")
        self.client.execute(write_sql, rows)

    def write_data(self, data, **kwargs):
        values = self.read_by_id([_['id'] for _ in data])
        assert len(data) == len(values), f'Len Not Equal!'
        
        for i in range(len(data)):
            data_copy = dict(data[i])
            del data_copy['id']
            values[i]['data'] = json.dumps(data_copy)
            values[i]['stage'] = kwargs['stage']
            for k, v in kwargs.items():
                values[i][k] = v
            del values[i]['id']
        keys = values[0].keys()
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} ({', '.join(keys)}) VALUES"
        # self.logger.info(f"Writing Eval data to {self.db_name}.{self.table_name} where algo = {kwargs['algo_name']} and score_key = {kwargs['score_key']}")
        delete_sql = f"DELETE FROM {self.config.db_name}.{self.config.table_name} WHERE id IN ({[_['id'] for _ in data]})"
        self.client.execute(delete_sql)
        self.client.execute(write_sql, values)
        
    def write_eval(self, data, **kwargs): ## must have name and score_key
        values = self.read_by_id([_['id'] for _ in data])
        
        assert len(data) == len(values), f'Len Not Equal!'
        for i in range(len(data)):
            values[i]['stage'] = kwargs['stage']
            values[i]['eval_stage'] += 1
            values[i][f"eval_algorithm_{values[i]['eval_stage']}"] = kwargs['algo_name']
            values[i][f"eval_score_{values[i]['eval_stage']}"] = data[i][kwargs['score_key']]
            if 'info_key' in kwargs:
                values[i][f"eval_info_{values[i]['eval_stage']}"] = data[i][kwargs['info_key']]
            del values[i]['id']
        keys = values[0].keys()
        write_sql = f"INSERT INTO {self.config.db_name}.{self.config.table_name} ({', '.join(keys)}) VALUES"
        self.logger.info(f"Writing Eval data to {self.config.db_name}.{self.config.table_name} where algo = {kwargs['algo_name']} and score_key = {kwargs['score_key']}")
        self.client.execute(write_sql, values)
        delete_sql = f"DELETE FROM {self.config.db_name}.{self.config.table_name} WHERE id IN ({[_['id'] for _ in data]})"
        self.client.execute(delete_sql)

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
