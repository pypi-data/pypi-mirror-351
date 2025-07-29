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

def safe_json_loads(s):
    # 1. 先尝试原始 json.loads
    try:
        return json.loads(s)
    except Exception as e:
        print(f"json.loads 失败: {e}，尝试修复…")

    # 2. 去除非法控制字符（除了常规的 \n \r \t）
    s_fixed = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)

    # 3. 尝试 json.loads
    try:
        return json.loads(s_fixed)
    except Exception as e:
        print(f"去除控制字符后依然失败: {e}，尝试修复裸换行和未转义引号…")

    # 4. 修复所有字符串字段中的裸换行、回车、tab、未转义的双引号
    def fix_multiline_and_quotes(m):
        key = m.group(1)
        val = m.group(2)
        # 先把裸换行、回车、tab替换为\\n、\\r、\\t
        val = val.replace('\n', '\\n').replace('\r', '\\r').replace('\t', '\\t')
        # 再把未转义的 " 替换为 \"
        val = re.sub(r'(?<!\\)"', r'\\"', val)
        return f'"{key}": "{val}"'
    # 只修复字符串字段
    s_fixed2 = re.sub(r'"([^"]+)":\s*"((?:[^"\\]|\\.)*)"', fix_multiline_and_quotes, s_fixed, flags=re.DOTALL)

    # 5. 再尝试 json.loads
    try:
        return json.loads(s_fixed2)
    except Exception as e:
        print(f"修复裸换行和未转义引号后依然失败: {e}，尝试反斜杠全转义…")

    # 6. 反斜杠全转义
    s_fixed3 = s_fixed2.replace('\\', '\\\\')
    try:
        return json.loads(s_fixed3)
    except Exception as e:
        print(f"反斜杠全转义后依然失败: {e}，尝试 ast.literal_eval…")

    # 7. 最后兜底：用 ast.literal_eval
    try:
        return ast.literal_eval(s_fixed2)
    except Exception as e:
        print(f"ast.literal_eval 也失败: {e}")
        raise ValueError("safe_json_loads: 无法解析该字符串为合法对象")

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

def monitor_execution_time(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        start = time.time()
        try:
            result = func(self, *args, **kwargs)
            duration = time.time() - start
            self.logger.info(f"{func.__name__} executed in {duration:.2f}s")
            return result
        except Exception as e:
            duration = time.time() - start
            self.logger.error(f"{func.__name__} failed after {duration:.2f}s: {str(e)}")
            raise
    return wrapper

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

    @contextmanager
    def _db_operation(self):
        """数据库操作上下文管理"""
        try:
            yield
        except Exception as e:
            self.logger.error(f"Database operation failed: {e}")
            raise DatabaseError(f"Operation failed: {str(e)}")

    def _build_select_query(
        self,
        columns: List[str],
        conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> tuple[str, dict]:
        """构建优化的 SELECT 查询
        
        Args:
            columns: 需要查询的列
            conditions: WHERE 条件
            limit: 返回数量
        """
        query = f"SELECT {', '.join(columns)} FROM {self.config.db_name}.{self.config.table_name}"
        params = {}
        
         # 增加 WHERE条件
        if conditions:
            where_conditions = []
            for k, v in conditions.items():
                if k == 'score_range_condition':
                    # Handle specific raw SQL condition string key
                    where_conditions.append(v)
                elif isinstance(v, (list, tuple)):
                    # Handle IN clause
                    where_conditions.append(f"{k} IN %({k})s")
                    params[k] = tuple(v)
                else:
                    # Handle equality (for other types including strings)
                    where_conditions.append(f"{k} = %({k})s")
                    params[k] = v
            query += " WHERE " + " AND ".join(where_conditions)

        # 支持limit            
        if limit:
            query += f" LIMIT {limit}"
            
        return query, params

    @monitor_execution_time
    def read_columns(
        self,
        columns: List[str],
        conditions: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """类似之前的read_by_ids，支持where条件和limit
        
        Args:
            columns: 需要读取的列名列表
            conditions: where 条件
            limit: limit
        """
        with self._db_operation():
            query, params = self._build_select_query(columns, conditions, limit)
            self.logger.debug(f"Executing query: {query} with params: {params}")
            
            result = self.client.query(query, params)
            rows = result.result_rows
            self.logger.info(f"Executing results: rows = {rows}")
            
            xx = [dict(zip(columns, row)) for row in rows]
            self.logger.info(f"Executing results: xx = {xx}")
            # self.logger.info(f"=====Executing results: xx[0]['data'] = {xx[0]['data']}")
            
            # try:
            #     aa = safe_json_loads(xx[0]['data'])
            #     self.logger.info(f"+++++最终解析json成功了 aa = {aa}")
            # except Exception as e:
            #     print(f"最终解析失败: {e}")
            
            return [dict(zip(columns, row)) for row in rows]

    def get_all_columns(self) -> List[str]:
        """获取所有列名"""
        schema_query = f"DESCRIBE {self.config.db_name}.{self.config.table_name}"
        result = self.client.query(schema_query)
        return [row[0] for row in result.result_rows]


    @monitor_execution_time
    def batch_write(
        self,
        data: List[Dict[str, Any]],
        batch_size: int = 10000
    ) -> None:
        """批量写入数据
        
        Args:
            data: 要写入的数据列表，比如  {'eval_stage': 1, 'data': '{"instructions": xxx, "input": "xxx"}', 'eval_score': 0.9},
            batch_size: 批次大小
        """
        if not data:
            return
            
        # 获取要插入的列名列表,比如eval_stage,data,eval_score等
        columns = list(data[0].keys())
        
        with self._db_operation():
            # 批量处理
            for i in range(0, len(data), batch_size):
                batch = data[i:i + batch_size]
                # 构建 VALUES 子句
                values_clause = []
                for row in batch:
                    row_values = []
                    for col in columns:
                        value = row[col]
                        self.logger.info(f"+++++batch_write+++++col = {col}, value = {value}")
                        if isinstance(value, str):
                            # 对字符串进行转义
                            self.logger.info(f"+++++batch_write+++++value is a str, value = {value}")
                            value = value.replace("'", "''")
                            if col == 'data':
                                bb = json.loads(value)
                                self.logger.info(f"+++++batch_write+++++value is a str, ====bb = {bb}")
                                value = json.dumps(bb, ensure_ascii=False)
                            row_values.append(f"'{value}'")
                        elif value is None:
                            self.logger.info(f"+++++batch_write+++++value is None, value = {value}")
                            row_values.append('NULL')
                        else:
                            self.logger.info(f"+++++batch_write+++++value is not a str, value = {value}")
                            row_values.append(str(value))
                    values_clause.append(f"({', '.join(row_values)})")
                
                insert_sql = f"""
                INSERT INTO {self.config.db_name}.{self.config.table_name}
                ({', '.join(columns)}) VALUES
                {', '.join(values_clause)}
                """
                
                self.client.command(insert_sql)
                self.logger.debug(f"Inserted batch of {len(batch)} rows")

    @monitor_execution_time
    def read_code_json(self, key_list, **kwargs):
        """读取代码数据
        Args:
            key_list: 需要读取的列名
            kwargs: 
                - stage: 阶段
                - format: 格式类型
                - syn: 是否合成
                - maxmin_scores: 评分范围列表
        """
        # 1. 保持原有行为：强制添加 id 列
        if 'id' not in key_list:
            key_list.append('id')
        
        # 2. 构建查询条件
        conditions = {
            'category': 'reasoning',
            'stage': kwargs['stage'],
            'format': kwargs['format'],
            'Synthetic': kwargs['syn']
        }
        
        # 3. 处理评分范围
        if 'maxmin_scores' in kwargs:
            score_conditions = []
            for i, score_range in enumerate(kwargs['maxmin_scores']):
                score_conditions.extend([
                    f"eval_score_{i+1} >= {score_range['min_score']}",
                    f"eval_score_{i+1} <= {score_range['max_score']}"
                ])
            # Add the combined score condition string to the conditions dictionary
            conditions['score_range_condition'] = ' AND '.join(score_conditions)
        
        # 4. 使用优化后的 read_columns 方法
        self.logger.info(f"Reading Code data from {self.config.db_name}.{self.config.table_name} with conditions: {conditions}, key_list = {key_list}")
        
        # 5. 执行查询
        rows = self.read_columns(
            columns=key_list,
            conditions=conditions
        )
        
        # 6. 处理 JSON 数据并展开列表
        expanded_rows = []
        for item in rows:
            if 'data' in item:
                try:
                    data_str = item['data']
                    self.logger.info(f"+++++清理前read_code_json+++++data_str = {data_str}")
                    data = safe_json_loads(data_str)
                    # data_str = self.clean_json_str(data_str)
                    # self.logger.info(f"+++++清理后read_code_json+++++data_str = {data_str}")
                    # data = json.loads(data_str)
                    self.logger.info(f"+++++json.loads后read_code_json+++++data = {data}")
                    if isinstance(data, list):
                        # 如果 data 是列表，展开为多条记录
                        for data_item in data:
                            new_item = item.copy() # 复制原有 item
                            new_item['data'] = data_item # 设置新的 data 字段为列表中的字典
                            expanded_rows.append(new_item)
                    else:
                        # 如果 data 不是列表，直接使用反序列化后的数据
                        item['data'] = data
                        expanded_rows.append(item)
                except json.JSONDecodeError as e:
                    self.logger.error(f"Failed to decode JSON data for item id {item.get('id', 'N/A')}: {e}")
                    # 可选：跳过此项或记录错误并包含原始数据
                    # For now, we will append the item with the raw data string
                    expanded_rows.append(item)
            else:
                # 如果没有 data 字段，直接添加 item
                expanded_rows.append(item)

        return expanded_rows

    @monitor_execution_time
    def write_data(self, data: list, **kwargs) -> None:
        """Write data to MyScale database with additional fields
        
        Args:
            data: List of data items to write, each item must contain an 'id' field
            **kwargs: Additional fields to update in the data
        
        Raises:
            DatabaseError: If database operation fails
            ValueError: If data length mismatch or required fields missing
        """
        if not data:
            self.logger.warning("Empty data list provided, skipping write operation")
            return

        with self._db_operation():
            try:
                # 1. 读取原数据
                ids = list(set([item['id'] for item in data]))  # Deduplicate IDs
                self.logger.debug(f"Reading data for unique ids: {ids}")
                values = self.read_columns(
                    columns=self.get_all_columns(),
                    conditions={'id': ids}
                )

                # 2. 验证数据长度
                if len(ids) != len(values):
                    error_msg = f"Data length mismatch: unique input ids={len(ids)}, found={len(values)}"
                    self.logger.error(error_msg)
                    raise ValueError(error_msg)

                # 3. 更新数据
                updated_values = []
                for item, new_value in zip(values, data):
                    # 创建新的字典而不是修改原字典
                    updated_item = item.copy()
                    # 序列化数据
                    updated_item['data'] = json.dumps(new_value)
                    # 更新额外字段
                    updated_item.update(kwargs)
                    # 删除id字段避免重复
                    del updated_item['id']
                    updated_values.append(updated_item)

                # 4. 准备删除语句 - 使用参数化查询更安全
                delete_sql = f"""
                ALTER TABLE {self.config.db_name}.{self.config.table_name}
                DELETE WHERE id IN %(ids)s
                """

                # 5. 执行数据库操作
                self.logger.info(f"Writing {len(updated_values)} items to database")
                self.batch_write(updated_values)  # 先插入新数据
                self.client.command(delete_sql, {'ids': tuple(ids)})  # 再删除旧数据
                self.logger.info(f"Successfully wrote and deleted {len(data)} items")

            except ValueError as e:
                # 业务逻辑错误直接抛出
                raise
            except json.JSONDecodeError as e:
                error_msg = f"Failed to serialize data: {str(e)}"
                self.logger.error(error_msg)
                raise DatabaseError(error_msg)
            except Exception as e:
                error_msg = f"Database operation failed: {str(e)}"
                self.logger.error(error_msg)
                raise DatabaseError(error_msg)

    @monitor_execution_time
    def write_eval(
        self,
        eval_data: List[Dict[str, Any]],
        algo_name: str,
        score_key: str,
        info_key: Optional[str] = None
    ) -> None:
        self.logger.info(f"write_eval------>eval_data = {eval_data}")
        """写入评估数据"""
        # 1. 读取所有现有数据
        ids = [d['id'] for d in eval_data]
        existing_data = self.read_columns(
            columns=self.get_all_columns(),
            conditions={'id': ids}
        )
        
        # 2. 准备更新数据
        updates = []
        for curr, orig in zip(eval_data, existing_data):
            new_stage = orig['stage'] + 1
            update = orig.copy()
            # 保留原有的 id
            update.update({
                'id': curr['id'],  # 保留 id
                'stage': new_stage,
                f'eval_algorithm_{new_stage}': algo_name,
                f'eval_score_{new_stage}': curr[score_key]
            })
            if info_key and info_key in curr:
                update[f'eval_info_{new_stage}'] = curr[info_key]
            updates.append(update)
        
        self.logger.info(f"write_eval------> updates = {updates}")
        # 3. 先删除后插入
        with self._db_operation():
            # 1. 先删除旧数据
            delete_query = f"""
            ALTER TABLE {self.config.db_name}.{self.config.table_name}
            DELETE WHERE id IN %(ids)s
            """
            self.client.command(delete_query, {'ids': tuple(ids)})
            
            # 2. 再插入新数据（包含 id）
            for update in updates:
                self.logger.info(f"+++++write_eval+++++update['data'] = {update['data']}")
                # 1. 先保证是 Python 对象
                if isinstance(update['data'], str):
                    try:
                        update['data'] = safe_json_loads(update['data'])
                    except Exception:
                        # 如果本来就是 dict/list，忽略异常
                        pass
                self.logger.info(f"+++++write_eval+++++aa = {update['data']}")
                # 2. 转成 JSON 字符串
                if isinstance(update['data'], (dict, list)):
                    self.logger.info(f"+++++write_eval+++++update['data'] is a dict or list")
                    update['data'] = json.dumps(update['data'], ensure_ascii=False)
                # 3. 二次反斜杠转义，保证 ClickHouse 能安全写入
                update['data'] = update['data'].replace('\\', '\\\\')
            self.batch_write(updates)
            
    @monitor_execution_time
    def write_code_json(self, data: list, **kwargs) -> None:
        """Write code data to MyScale with JSON format
        
        Args:
            data: List of code data items to write
            **kwargs: Must include:
                - format: Data format
                - syn: Synthetic flag
        
        Raises:
            DatabaseError: If database operation fails
            ValueError: If required kwargs are missing
        """
        if not data:
            self.logger.warning("Empty data list provided, skipping write operation")
            return

        # 验证必需的参数
        required_kwargs = {'format', 'syn'}
        if not all(k in kwargs for k in required_kwargs):
            error_msg = f"Missing required kwargs: {required_kwargs - set(kwargs.keys())}"
            self.logger.error(error_msg)
            raise ValueError(error_msg)

        with self._db_operation():
            try:
                # 1. 准备数据
                rows = []
                for item in data:
                    row = {
                        "data": json.dumps(item['data']),
                        "raw_data_id": item['id'],
                        "category": "reasoning",
                        "format": kwargs['format'],
                        "Synthetic": kwargs['syn']
                    }
                    rows.append(row)

                # 2. 执行批量写入
                self.logger.info(
                    f"Writing Code data to {self.config.db_name}.{self.config.table_name} "
                    f"where format = {kwargs['format']} and syn = {kwargs['syn']}"
                )
                self.batch_write(rows)
                self.logger.info(f"Successfully wrote {len(data)} code items")

            except json.JSONDecodeError as e:
                error_msg = f"Failed to serialize data: {str(e)}"
                self.logger.error(error_msg)
                raise DatabaseError(error_msg)
            except Exception as e:
                error_msg = f"Failed to write code data: {str(e)}"
                self.logger.error(error_msg)
                raise DatabaseError(error_msg)

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

