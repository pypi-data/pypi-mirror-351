# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import pandas as pd
import os
import logging
from mdbq.log import mylogger
from typing import Union, List, Dict, Optional, Any, Tuple, Set
from dbutils.pooled_db import PooledDB
import json
from collections import OrderedDict

warnings.filterwarnings('ignore')
logger = mylogger.MyLogger(
    name='uploader',
    logging_mode='none',
    log_level='error',
    log_file='uploader.log',
    log_format='json',
    max_log_size=50,
    backup_count=5,
    enable_async=False,  # 是否启用异步日志
    sample_rate=0.5,  # 采样50%的DEBUG/INFO日志
    sensitive_fields=[],  #  敏感字段列表
)


def count_decimal_places(num_str):
    """ 计算小数位数, 允许科学计数法 """
    match = re.match(r'^[-+]?\d+(\.\d+)?([eE][-+]?\d+)?$', str(num_str))
    if match:
        # 如果是科学计数法
        match = re.findall(r'(\d+)\.(\d+)[eE][-+]?(\d+)$', str(num_str))
        if match:
            if len(match[0]) == 3:
                if int(match[0][2]) < len(match[0][1]):
                    # count_int 清除整数部分开头的 0 并计算整数位数
                    count_int = len(re.sub('^0+', '', str(match[0][0]))) + int(match[0][2])
                    # 计算小数位数
                    count_float = len(match[0][1]) - int(match[0][2])
                    return count_int, count_float
        # 如果是普通小数
        match = re.findall(r'(\d+)\.(\d+)$', str(num_str))
        if match:
            count_int = len(re.sub('^0+', '', str(match[0][0])))
            count_float = len(match[0][1])
            return count_int, count_float  # 计算小数位数
    return 0, 0


class StatementCache(OrderedDict):
    """LRU缓存策略"""
    def __init__(self, maxsize=100):
        super().__init__()
        self.maxsize = maxsize

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        if len(self) > self.maxsize:
            self.popitem(last=False)


class MySQLUploader:
    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            collation: str = 'utf8mb4_0900_ai_ci',  # utf8mb4_0900_ai_ci: 该排序规则对大小写不敏感, utf8mb4_0900_as_cs/utf8mb4_bin: 对大小写敏感
            max_retries: int = 10,
            retry_interval: int = 10,
            pool_size: int = 5,
            connect_timeout: int = 10,
            read_timeout: int = 30,
            write_timeout: int = 30,
            ssl: Optional[Dict] = None
    ):
        """
        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机地址，默认为localhost
        :param port: 数据库端口，默认为3306
        :param charset: 字符集，默认为utf8mb4
        :param collation: 排序规则，默认为utf8mb4_0900_ai_ci

        :param max_retries: 最大重试次数，默认为10
        :param retry_interval: 重试间隔(秒)，默认为10
        :param pool_size: 连接池大小，默认为5
        :param connect_timeout: 连接超时(秒)，默认为10
        :param read_timeout: 读取超时(秒)，默认为30
        :param write_timeout: 写入超时(秒)，默认为30
        :param ssl: SSL配置字典，默认为None
        """
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.charset = charset
        self.collation = collation
        self.max_retries = max(max_retries, 1)
        self.retry_interval = max(retry_interval, 1)
        self.pool_size = max(pool_size, 1)
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.ssl = ssl
        self._prepared_statements = StatementCache(maxsize=100)
        self._max_cached_statements = 100
        self._table_metadata_cache = {}
        self.metadata_cache_ttl = 300  # 5分钟缓存时间

        # 创建连接池
        self.pool = self._create_connection_pool()

    def _create_connection_pool(self) -> PooledDB:
        """创建数据库连接池"""
        if hasattr(self, 'pool') and self.pool is not None and self._check_pool_health():
            return self.pool

        start_time = time.time()
        self.pool = None

        pool_params = {
            'creator': pymysql,
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,
            'cursorclass': pymysql.cursors.DictCursor,
            'maxconnections': self.pool_size,
            'ping': 7,
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'autocommit': False
        }

        if self.ssl:
            required_keys = {'ca', 'cert', 'key'}
            if not all(k in self.ssl for k in required_keys):
                error_msg = "SSL配置必须包含ca、cert和key"
                logger.error(error_msg)
                raise ValueError(error_msg)
            pool_params['ssl'] = {
                'ca': self.ssl['ca'],
                'cert': self.ssl['cert'],
                'key': self.ssl['key'],
                'check_hostname': self.ssl.get('check_hostname', False)
            }

        try:
            pool = PooledDB(**pool_params)
            elapsed = time.time() - start_time
            logger.info("连接池创建成功", {
                'pool_size': self.pool_size,
                'time_elapsed': elapsed
            })
            return pool
        except Exception as e:
            elapsed = time.time() - start_time
            self.pool = None
            logger.error("连接池创建失败", {
                'error': str(e),
                'time_elapsed': elapsed
            })
            raise ConnectionError(f"连接池创建失败: {str(e)}")

    def _execute_with_retry(self, func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            start_time = time.time()
            operation = func.__name__

            logger.debug(f"开始执行操作: {operation}", {
                'attempt': 1,
                'max_retries': self.max_retries
            })

            for attempt in range(self.max_retries):
                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time

                    if attempt > 0:
                        logger.info("操作成功(重试后)", {
                            'operation': operation,
                            'attempts': attempt + 1,
                            'time_elapsed': elapsed
                        })
                    else:
                        logger.debug("操作成功", {
                            'operation': operation,
                            'time_elapsed': elapsed
                        })

                    return result

                except (pymysql.OperationalError, pymysql.err.MySQLError) as e:
                    last_exception = e

                    # 记录详细的MySQL错误信息
                    error_details = {
                        'operation': operation,
                        'error_code': e.args[0] if e.args else None,
                        'error_message': e.args[1] if len(e.args) > 1 else None,
                        'attempt': attempt + 1,
                        'max_retries': self.max_retries
                    }

                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_interval * (attempt + 1)
                        error_details['wait_time'] = wait_time
                        logger.warning(f"数据库操作失败，准备重试 {error_details}", )
                        time.sleep(wait_time)

                        # 尝试重新连接
                        try:
                            self.pool = self._create_connection_pool()
                            logger.info("成功重新建立数据库连接")
                        except Exception as reconnect_error:
                            logger.error("重连失败", {
                                'error': str(reconnect_error)
                            })
                    else:
                        elapsed = time.time() - start_time
                        error_details['time_elapsed'] = elapsed
                        logger.error(f"操作最终失败 {error_details}")

                except pymysql.IntegrityError as e:
                    elapsed = time.time() - start_time
                    logger.error("完整性约束错误", {
                        'operation': operation,
                        'time_elapsed': elapsed,
                        'error_code': e.args[0] if e.args else None,
                        'error_message': e.args[1] if len(e.args) > 1 else None
                    })
                    raise e

                except Exception as e:
                    last_exception = e
                    elapsed = time.time() - start_time
                    logger.error("发生意外错误", {
                        'operation': operation,
                        'time_elapsed': elapsed,
                        'error_type': type(e).__name__,
                        'error_message': str(e),
                        'error_args': e.args if hasattr(e, 'args') else None
                    })
                    break

            raise last_exception if last_exception else Exception("发生未知错误")

        return wrapper

    def _get_connection(self):
        """从连接池获取连接"""
        try:
            conn = self.pool.connection()
            logger.debug("获取数据库连接")
            return conn
        except Exception as e:
            logger.error(f'{e}')
            raise ConnectionError(f"连接数据库失败: {str(e)}")

    def _check_database_exists(self, db_name: str) -> bool:
        """检查数据库是否存在"""
        db_name = self._validate_identifier(db_name)
        sql = "SELECT SCHEMA_NAME FROM INFORMATION_SCHEMA.SCHEMATA WHERE SCHEMA_NAME = %s"

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name,))
                    exists = bool(cursor.fetchone())
                    logger.debug(f"{db_name} 数据库已存在: {exists}")
                    return exists
        except Exception as e:
            logger.error(f"检查数据库是否存在时出错: {str(e)}")
            raise

    def _create_database(self, db_name: str):
        """创建数据库"""
        db_name = self._validate_identifier(db_name)
        sql = f"CREATE DATABASE IF NOT EXISTS `{db_name}` CHARACTER SET {self.charset} COLLATE {self.collation}"

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                conn.commit()
                logger.info(f"{db_name} 数据库已创建")
        except Exception as e:
            logger.error(f"{db_name}: 无法创建数据库 {str(e)}")
            conn.rollback()
            raise

    def _get_partition_table_name(self, table_name: str, date_value: str, partition_by: str) -> str:
        """
        获取分表名称

        :param table_name: 基础表名
        :param date_value: 日期值
        :param partition_by: 分表方式 ('year' 或 'month')
        :return: 分表名称
        :raises ValueError: 如果日期格式无效或分表方式无效
        """
        try:
            # date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
            date_obj = self._validate_datetime(date_value, True)
        except ValueError:
            try:
                # date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d')
                date_obj = self._validate_datetime(date_value, True)
            except ValueError:
                error_msg = f"无效的日期格式1: {date_value}"
                logger.error(error_msg)
                raise ValueError(error_msg)

        if partition_by == 'year':
            return f"{table_name}_{date_obj.year}"
        elif partition_by == 'month':
            return f"{table_name}_{date_obj.year}_{date_obj.month:02d}"
        else:
            error_msg = "partition_by must be 'year' or 'month'"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _validate_identifier(self, identifier: str) -> str:
        """
        验证并清理数据库标识符(数据库名、表名、列名)
        防止SQL注入和非法字符

        :param identifier: 要验证的标识符
        :return: 清理后的安全标识符
        :raises ValueError: 如果标识符无效
        """
        if not identifier or not isinstance(identifier, str):
            error_msg = f"无效的标识符: {identifier}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 移除非法字符，只保留字母、数字、下划线和美元符号
        cleaned = re.sub(r'[^\w\u4e00-\u9fff$]', '', identifier)
        if not cleaned:
            error_msg = f"无法清理异常标识符: {identifier}"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查是否为MySQL保留字
        mysql_keywords = {
            'select', 'insert', 'update', 'delete', 'from', 'where', 'and', 'or',
            'not', 'like', 'in', 'is', 'null', 'true', 'false', 'between'
        }
        if cleaned.lower() in mysql_keywords:
            logger.debug(f"存在MySQL保留字: {cleaned}")
            return f"`{cleaned}`"

        return cleaned

    def _check_table_exists(self, db_name: str, table_name: str) -> bool:
        """检查表是否存在"""
        cache_key = f"{db_name}.{table_name}"
        if cache_key in self._table_metadata_cache:
            cached_time, result = self._table_metadata_cache[cache_key]
            if time.time() - cached_time < self.metadata_cache_ttl:
                return result

        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)
        sql = """
                SELECT TABLE_NAME 
                FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
                """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    result = bool(cursor.fetchone())
        except Exception as e:
            logger.error(f"检查数据表是否存在时发生未知错误: {e}", )
            raise

        # 执行查询并缓存结果
        self._table_metadata_cache[cache_key] = (time.time(), result)
        return result

    def _create_table(
            self,
            db_name: str,
            table_name: str,
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            date_column: Optional[str] = None,
            indexes: Optional[List[str]] = None,
            allow_null: bool = False
    ):
        """
        创建数据表

        :param db_name: 数据库名
        :param table_name: 表名
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param primary_keys: 主键列列表
        :param date_column: 日期列名，如果存在将设置为索引
        :param indexes: 需要创建索引的列列表
        """
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)

        if not set_typ:
            error_msg = "No columns specified for table creation"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 构建列定义SQL
        column_defs = ["`id` INT NOT NULL AUTO_INCREMENT"]

        # 添加其他列定义
        for col_name, col_type in set_typ.items():
            # 跳过id列，因为已经在前面添加了
            if col_name.lower() == 'id':
                continue
            safe_col_name = self._validate_identifier(col_name)
            col_def = f"`{safe_col_name}` {col_type}"

            # 根据allow_null决定是否添加NOT NULL约束
            if not allow_null and not col_type.lower().startswith('json'):
                col_def += " NOT NULL"

            column_defs.append(col_def)

        # 添加主键定义
        if primary_keys:
            # 确保id在主键中
            if 'id' not in [pk.lower() for pk in primary_keys]:
                primary_keys = ['id'] + primary_keys
        else:
            # 如果没有指定主键，则使用id作为主键
            primary_keys = ['id']

        # 添加主键定义
        safe_primary_keys = [self._validate_identifier(pk) for pk in primary_keys]
        primary_key_sql = f", PRIMARY KEY (`{'`,`'.join(safe_primary_keys)}`)"

        # 构建完整SQL
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}` (
            {','.join(column_defs)}
            {primary_key_sql}
        ) ENGINE=InnoDB DEFAULT CHARSET={self.charset} COLLATE={self.collation}
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    logger.info(f"{db_name}.{table_name}: 数据表已创建")

                # 添加普通索引
                index_statements = []

                # 日期列索引
                if date_column and date_column in set_typ:
                    safe_date_col = self._validate_identifier(date_column)
                    index_statements.append(
                        f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_date_col}` (`{safe_date_col}`)"
                    )

                # 其他索引
                if indexes:
                    for idx_col in indexes:
                        if idx_col in set_typ:
                            safe_idx_col = self._validate_identifier(idx_col)
                            index_statements.append(
                                f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_idx_col}` (`{safe_idx_col}`)"
                            )

                # 执行所有索引创建语句
                if index_statements:
                    with conn.cursor() as cursor:
                        for stmt in index_statements:
                            cursor.execute(stmt)
                            logger.debug(f"Executed index statement: {stmt}", )

                conn.commit()
                logger.info(f"{db_name}.{table_name}: 索引已添加")

        except Exception as e:
            logger.error(f"{db_name}.{table_name}: 建表失败: {str(e)}")
            conn.rollback()
            raise

    def _validate_datetime(self, value, date_type=False):
        """date_type: 返回字符串类型或者日期类型"""
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',
            '%Y-%m-%d %H:%M:%S.%f',
            '%Y/%-m/%-d',  # 2023/1/8
            '%Y-%m-%-d',  # 2023-01-8
            '%Y-%-m-%-d'  # 2023-1-8
        ]
        for fmt in formats:
            try:
                if date_type:
                    return pd.to_datetime(datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d'))
                else:
                    return datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        raise ValueError(f"无效的日期格式2: {value}")

    def _validate_value(self, value: Any, column_type: str) -> Any:
        """
        验证并清理数据值，根据列类型进行适当转换

        :param value: 要验证的值
        :param column_type: 列的数据类型
        :return: 清理后的值
        :raises ValueError: 如果值转换失败
        """
        if value is None:
            return None

        try:
            column_type_lower = column_type.lower()

            if 'int' in column_type_lower:
                if isinstance(value, (str, bytes)) and not value.strip().isdigit():
                    raise ValueError("非数字字符串无法转换为整数")
                return int(value)
            elif any(t in column_type_lower for t in ['float', 'double', 'decimal']):
                return float(value) if value is not None else None
            elif '日期' in column_type_lower or 'time' in column_type_lower:
                if isinstance(value, (datetime.datetime, pd.Timestamp)):
                    return value.strftime('%Y-%m-%d %H:%M:%S')
                elif isinstance(value, str):
                    try:
                        return self._validate_datetime(value)  # 使用专门的日期验证方法
                    except ValueError as e:
                        raise ValueError(f"无效日期格式: {value} - {str(e)}")
                return str(value)
            elif 'char' in column_type_lower or 'text' in column_type_lower:
                # 防止SQL注入
                if isinstance(value, str):
                    return value.replace('\\', '\\\\').replace("'", "\\'")
                return str(value)
            elif 'json' in column_type_lower:
                import json
                return json.dumps(value) if value is not None else None
            else:
                return value
        except (ValueError, TypeError) as e:
            error_msg = f"数据类型转换异常 {value} to type {column_type}: {str(e)}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    def _get_table_columns(self, db_name: str, table_name: str) -> Dict[str, str]:
        """获取表的列名和数据类型"""
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)
        sql = """
        SELECT COLUMN_NAME, DATA_TYPE 
        FROM INFORMATION_SCHEMA.COLUMNS 
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s
        ORDER BY ORDINAL_POSITION
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql, (db_name, table_name))
                    set_typ = {row['COLUMN_NAME']: row['DATA_TYPE'] for row in cursor.fetchall()}
                    logger.debug(f"{db_name}.{table_name}: 获取表的列信息: {set_typ}")
                    return set_typ
        except Exception as e:
            logger.error(f"无法获取表列信息: {str(e)}")
            raise

    def _upload_to_table(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            allow_null: bool,
            auto_create: bool,
            date_column: Optional[str],
            indexes: Optional[List[str]],
            batch_id: Optional[str] = None
    ):
        """实际执行表上传的方法"""
        # 检查表是否存在
        if not self._check_table_exists(db_name, table_name):
            if auto_create:
                self._create_table(db_name, table_name, set_typ, primary_keys, date_column, indexes,
                                   allow_null=allow_null)
            else:
                error_msg = f"数据表不存在: '{db_name}.{table_name}'"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 获取表结构并验证
        table_columns = self._get_table_columns(db_name, table_name)
        if not table_columns:
            error_msg = f"获取列失败 '{db_name}.{table_name}'"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 验证数据列与表列匹配
        for col in set_typ:
            if col not in table_columns:
                error_msg = f"列不存在: '{col}' -> '{db_name}.{table_name}'"
                logger.error(error_msg)
                raise ValueError(error_msg)

        # 插入数据
        self._insert_data(
            db_name, table_name, data, set_typ,
            check_duplicate, duplicate_columns
        )

    def _infer_data_type(self, value: Any) -> str:
        """
        根据值推断合适的数据类型

        :param value: 要推断的值
        :return: MySQL数据类型字符串
        """
        if value is None:
            return 'VARCHAR(255)'  # 默认字符串类型

        if isinstance(value, bool):
            return 'TINYINT(1)'
        elif isinstance(value, int):
            # if -128 <= value <= 127:
            #     return 'TINYINT'
            # elif -32768 <= value <= 32767:
            #     return 'SMALLINT'
            # elif -8388608 <= value <= 8388607:
            #     return 'MEDIUMINT'
            if -2147483648 <= value <= 2147483647:
                return 'INT'
            else:
                return 'BIGINT'
        elif isinstance(value, float):
            return 'DECIMAL(10,2)'
        elif isinstance(value, (datetime.datetime, pd.Timestamp)):
            return 'DATETIME'
        elif isinstance(value, datetime.date):
            return 'DATE'
        elif isinstance(value, (list, dict)):
            return 'JSON'
        elif isinstance(value, str):
            # 尝试判断是否是日期时间
            try:
                self._validate_datetime(value)
                return 'DATETIME'
            except ValueError:
                pass

            # 根据字符串长度选择合适类型
            length = len(value)
            if length <= 255:
                return 'VARCHAR(255)'
            elif length <= 65535:
                return 'TEXT'
            elif length <= 16777215:
                return 'MEDIUMTEXT'
            else:
                return 'LONGTEXT'
        else:
            return 'VARCHAR(255)'

    def _prepare_data(
            self,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            allow_null: bool = False
    ) -> List[Dict]:
        """
        准备要上传的数据，验证并转换数据类型

        :param data: 输入数据
        :param set_typ: 列名和数据类型字典 {列名: 数据类型}
        :param allow_null: 是否允许空值
        :return: 待上传的数据列表和对应的数据类型
        :raises ValueError: 如果数据验证失败
        """
        # 统一数据格式为字典列表
        if isinstance(data, pd.DataFrame):
            try:
                # 将列名转为小写
                data.columns = [col.lower() for col in data.columns]
                data = data.replace({pd.NA: None}).to_dict('records')
            except Exception as e:
                logger.error(f"数据转字典时发生错误: {e}", )
                raise ValueError(f"数据转字典时发生错误: {e}")
        elif isinstance(data, dict):
            data = [{k.lower(): v for k, v in data.items()}]
        elif isinstance(data, list) and all(isinstance(item, dict) for item in data):
            # 将列表中的每个字典键转为小写
            data = [{k.lower(): v for k, v in item.items()} for item in data]
        else:
            error_msg = "数据结构必须是字典、列表、字典列表或dataframe"
            logger.error(error_msg)
            raise ValueError(error_msg)

        # 将set_typ的键转为小写
        set_typ = {k.lower(): v for k, v in set_typ.items()}

        # 获取数据中实际存在的列名
        data_columns = set()
        if data:
            data_columns = set(data[0].keys())

        # 过滤set_typ，只保留数据中存在的列
        filtered_set_typ = {}
        for col in data_columns:
            if col in set_typ:
                filtered_set_typ[col] = set_typ[col]
            else:
                # 如果列不在set_typ中，尝试推断类型
                sample_values = [row[col] for row in data if col in row and row[col] is not None][:10]
                if sample_values:
                    inferred_type = self._infer_data_type(sample_values[0])
                    filtered_set_typ[col] = inferred_type
                    logger.debug(f"自动推断列'{col}'的数据类型为: {inferred_type}")
                else:
                    # 没有样本值，使用默认类型
                    filtered_set_typ[col] = 'VARCHAR(255)'
                    logger.debug(f"为列'{col}'使用默认数据类型: VARCHAR(255)")

        prepared_data = []
        for row_idx, row in enumerate(data, 1):
            prepared_row = {}
            for col_name in filtered_set_typ:
                # 跳过id列，不允许外部传入id
                if col_name.lower() == 'id':
                    continue

                if col_name not in row:
                    if not allow_null:
                        error_msg = f"Row {row_idx}: Missing required column '{col_name}' in data"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
                    prepared_row[col_name] = None
                else:
                    try:
                        prepared_row[col_name] = self._validate_value(row[col_name], filtered_set_typ[col_name])
                    except ValueError as e:
                        error_msg = f"Row {row_idx}, column '{col_name}': {str(e)}"
                        logger.error(error_msg)
                        raise ValueError(error_msg)
            prepared_data.append(prepared_row)

        logger.debug(f"已准备 {len(prepared_data)} 行数据")
        return prepared_data, filtered_set_typ

    def upload_data(
            self,
            db_name: str,
            table_name: str,
            data: Union[Dict, List[Dict], pd.DataFrame],
            set_typ: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            allow_null: bool = False,
            partition_by: Optional[str] = None,
            partition_date_column: str = '日期',
            auto_create: bool = True,
            indexes: Optional[List[str]] = None
    ):
        """
        上传数据到数据库
        """
        upload_start = time.time()
        initial_row_count = len(data) if hasattr(data, '__len__') else 1

        batch_id = f"batch_{int(time.time() * 1000)}"
        success_flag = False

        logger.info("开始上传数据", {
            'batch_id': batch_id,
            'database': db_name,
            'table': table_name,
            'partition_by': partition_by,
            'check_duplicate': check_duplicate,
            'row_count': len(data) if hasattr(data, '__len__') else 1,
            'auto_create': auto_create
        })

        try:
            # 验证参数
            if not set_typ:
                error_msg = "列的数据类型缺失"
                logger.error(error_msg)
                raise ValueError(error_msg)

            if partition_by and partition_by not in ['year', 'month']:
                error_msg = "分表方式必须是 'year' 或 'month'"
                logger.error(error_msg)
                raise ValueError(error_msg)

            # 准备数据
            prepared_data, set_typ = self._prepare_data(data, set_typ, allow_null)

            # 检查数据库是否存在
            if not self._check_database_exists(db_name):
                if auto_create:
                    self._create_database(db_name)
                else:
                    error_msg = f"数据库不存在: '{db_name}'"
                    logger.error(error_msg)
                    raise ValueError(error_msg)

            # 处理分表逻辑
            if partition_by:
                partitioned_data = {}
                for row in prepared_data:
                    try:
                        if partition_date_column not in row:
                            error_msg = f"异常缺失列 '{partition_date_column}'"
                            logger.error(error_msg)
                            continue  # 跳过当前行

                        part_table = self._get_partition_table_name(
                            table_name,
                            str(row[partition_date_column]),
                            partition_by
                        )
                        if part_table not in partitioned_data:
                            partitioned_data[part_table] = []
                        partitioned_data[part_table].append(row)
                    except Exception as e:
                        logger.error("分表处理失败", {
                            'row_data': row,
                            'error': str(e)
                        })
                        continue  # 跳过当前行

                # 对每个分表执行上传
                for part_table, part_data in partitioned_data.items():
                    try:
                        self._upload_to_table(
                            db_name, part_table, part_data, set_typ,
                            primary_keys, check_duplicate, duplicate_columns,
                            allow_null, auto_create, partition_date_column,
                            indexes, batch_id
                        )
                    except Exception as e:
                        logger.error("分表上传失败", {
                            'partition_table': part_table,
                            'error': str(e)
                        })
                        continue  # 跳过当前分表，继续处理其他分表
            else:
                # 不分表，直接上传
                self._upload_to_table(
                    db_name, table_name, prepared_data, set_typ,
                    primary_keys, check_duplicate, duplicate_columns,
                    allow_null, auto_create, partition_date_column,
                    indexes, batch_id
                )

            success_flag = True

        except Exception as e:
            logger.error("上传过程中发生全局错误", {
                'error': str(e),
                'error_type': type(e).__name__
            })
        finally:
            elapsed = time.time() - upload_start
            logger.info("上传处理完成", {
                'batch_id': batch_id,
                'success': success_flag,
                'time_elapsed': elapsed,
                'initial_row_count': initial_row_count
            })

    def _insert_data(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            set_typ: Dict[str, str],
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            batch_size: int = 1000,
            batch_id: Optional[str] = None
    ):
        """
        插入数据到表中

        参数:
        db_name: 数据库名
        table_name: 表名
        data: 要插入的数据列表
        set_typ: 列名和数据类型字典 {列名: 数据类型}
        check_duplicate: 是否检查重复
        duplicate_columns: 用于检查重复的列(为空时检查所有列)
        batch_size: 批量插入大小
        batch_id: 批次ID用于日志追踪
        """
        if not data:
            return

        # 获取所有列名（排除id列）
        all_columns = [col for col in set_typ.keys() if col.lower() != 'id']
        safe_columns = [self._validate_identifier(col) for col in all_columns]
        placeholders = ','.join(['%s'] * len(safe_columns))

        # 构建基础SQL语句
        if check_duplicate:
            if not duplicate_columns:
                duplicate_columns = all_columns
            else:
                duplicate_columns = [col for col in duplicate_columns if col != 'id']

            conditions = []
            for col in duplicate_columns:
                col_type = set_typ.get(col, '').lower()

                # 处理DECIMAL类型，使用ROUND确保精度一致
                if col_type.startswith('decimal'):
                    # 提取小数位数，如DECIMAL(10,2)提取2
                    scale_match = re.search(r'decimal\(\d+,(\d+)\)', col_type)
                    scale = int(scale_match.group(1)) if scale_match else 2
                    conditions.append(f"ROUND(`{self._validate_identifier(col)}`, {scale}) = ROUND(%s, {scale})")
                else:
                    conditions.append(f"`{self._validate_identifier(col)}` = %s")

            where_clause = " AND ".join(conditions)

            sql = f"""
                    INSERT INTO `{db_name}`.`{table_name}` 
                    (`{'`,`'.join(safe_columns)}`) 
                    SELECT {placeholders}
                    FROM DUAL
                    WHERE NOT EXISTS (
                        SELECT 1 FROM `{db_name}`.`{table_name}`
                        WHERE {where_clause}
                    )
                    """
        else:
            sql = f"""
                INSERT INTO `{db_name}`.`{table_name}` 
                (`{'`,`'.join(safe_columns)}`) 
                VALUES ({placeholders})
                """

        total_inserted = 0
        total_skipped = 0
        total_failed = 0  # 失败计数器

        # 分批插入数据
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(data), batch_size):
                    batch_start = time.time()
                    batch = data[i:i + batch_size]
                    successful_rows = 0  # 当前批次成功数

                    for row in batch:
                        try:
                            # 准备参数
                            row_values = [row.get(col) for col in all_columns]
                            # 如果是排重检查，添加排重列值
                            if check_duplicate:
                                row_values += [row.get(col) for col in duplicate_columns]

                            cursor.execute(sql, row_values)
                            successful_rows += 1
                            conn.commit()  # 每次成功插入后提交

                        except Exception as e:
                            conn.rollback()  # 回滚当前行的事务
                            total_failed += 1

                            # 记录失败行详细信息
                            error_details = {
                                'batch_id': batch_id,
                                'database': db_name,
                                'table': table_name,
                                'error_type': type(e).__name__,
                                'error_message': str(e),
                                'column_types': set_typ,
                                'duplicate_check': check_duplicate,
                                'duplicate_columns': duplicate_columns
                            }
                            logger.error(f"单行插入失败: {error_details}")
                            continue  # 跳过当前行，继续处理下一行

                    # 更新统计信息
                    if check_duplicate:
                        cursor.execute("SELECT ROW_COUNT()")
                        affected_rows = cursor.rowcount
                        total_inserted += affected_rows
                        total_skipped += len(batch) - affected_rows - (len(batch) - successful_rows)
                    else:
                        total_inserted += successful_rows

                    batch_elapsed = time.time() - batch_start
                    batch_info = {
                        'batch_id': batch_id,
                        'batch_index': i // batch_size + 1,
                        'total_batches': (len(data) + batch_size - 1) // batch_size,
                        'batch_size': len(batch),
                        'successful_rows': successful_rows,
                        'failed_rows': len(batch) - successful_rows,
                        'time_elapsed': batch_elapsed,
                        'rows_per_second': successful_rows / batch_elapsed if batch_elapsed > 0 else 0
                    }
                    logger.debug(f"批次处理完成 {batch_info}")

        logger.info("数据插入完成", {
            'total_rows': len(data),
            'inserted_rows': total_inserted,
            'skipped_rows': total_skipped,
            'failed_rows': total_failed
        })

    def close(self):
        """关闭连接池并记录最终指标"""
        close_start = time.time()

        try:
            if hasattr(self, 'pool') and self.pool is not None:
                # 更安全的关闭方式
                try:
                    self.pool.close()
                except Exception as e:
                    logger.warning("关闭连接池时出错", {
                        'error': str(e)
                    })

                self.pool = None

                elapsed = round(time.time() - close_start, 2)
                logger.info("连接池已关闭", {
                    'close_time_elapsed': elapsed
                })
        except Exception as e:
            elapsed = round(time.time() - close_start, 2)
            logger.error("关闭连接池失败", {
                'error': str(e),
                'close_time_elapsed': elapsed
            })
            raise

    def _check_pool_health(self):
        """定期检查连接池健康状态"""
        try:
            conn = self.pool.connection()
            conn.ping(reconnect=True)
            conn.close()
            return True
        except Exception as e:
            logger.warning("连接池健康检查失败", {
                'error': str(e)
            })
            return False

    def retry_on_failure(max_retries=3, delay=1):
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                last_exception = None
                for attempt in range(max_retries):
                    try:
                        return func(*args, **kwargs)
                    except (pymysql.OperationalError, pymysql.InterfaceError) as e:
                        last_exception = e
                        if attempt < max_retries - 1:
                            time.sleep(delay * (attempt + 1))
                            continue
                        raise MySQLUploaderError(f"操作重试{max_retries}次后失败") from e
                    except Exception as e:
                        raise MySQLUploaderError(f"操作失败: {str(e)}") from e
                raise last_exception if last_exception else MySQLUploaderError("未知错误")

            return wrapper

        return decorator


def main():
    uploader = MySQLUploader(
        username='root',
        password='pw',
        host='localhost',
        port=3306,
    )

    # 定义列和数据类型
    set_typ = {
        'name': 'VARCHAR(255)',
        'age': 'INT',
        'salary': 'DECIMAL(10,2)',
        '日期': 'DATE',
        'shop': None,
    }

    # 准备数据
    data = [
        {'日期': '2023-01-8', 'name': 'JACk', 'AGE': '24', 'salary': 555.1545},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 35, 'salary': 100},
        {'日期': '2023-01-15', 'name': 'Alice', 'AGE': 30, 'salary': 0.0},
        {'日期': '2023-02-20', 'name': 'Bob', 'AGE': 25, 'salary': 45000.75}
    ]

    # 上传数据
    uploader.upload_data(
        db_name='测试库',
        table_name='测试表',
        data=data,
        set_typ=set_typ,  # 定义列和数据类型
        primary_keys=[],  # 创建唯一主键
        check_duplicate=False,  # 检查重复数据
        duplicate_columns=[],  # 指定排重的组合键
        allow_null=False,  # 允许插入空值
        partition_by='year',  # 按月分表
        partition_date_column='日期',  # 用于分表的日期列名，默认为'日期'
        auto_create=True,  # 表不存在时自动创建, 默认参数不要更改
        indexes=[],  # 指定索引列
    )

    uploader.close()


if __name__ == '__main__':
    main()
