# -*- coding:utf-8 -*-
import datetime
import re
import time
from functools import wraps
import warnings
import pymysql
import numpy as np
import pandas as pd
from sqlalchemy import create_engine
import os
import logging
from mdbq.other import otk
from dbutils.pooled_db import PooledDB
from typing import Union, List, Dict, Optional, Any, Tuple
warnings.filterwarnings('ignore')
"""
建表流程:
建表规范:
"""
logger = logging.getLogger(__name__)


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


class MySQLUploader:
    def __init__(
            self,
            username: str,
            password: str,
            host: str = 'localhost',
            port: int = 3306,
            charset: str = 'utf8mb4',
            collation: str = 'utf8mb4_0900_ai_ci',
            enable_logging: bool = False,
            log_level: str = 'ERROR',
            max_retries: int = 10,
            retry_interval: int = 10,
            pool_size: int = 5,
            connect_timeout: int = 10,
            read_timeout: int = 30,
            write_timeout: int = 30,
            ssl: Optional[Dict] = None
    ):
        """
        初始化MySQL上传工具

        :param username: 数据库用户名
        :param password: 数据库密码
        :param host: 数据库主机地址，默认为localhost
        :param port: 数据库端口，默认为3306
        :param charset: 字符集，默认为utf8mb4
        :param collation: 排序规则，默认为utf8mb4_0900_ai_ci
        :param enable_logging: 是否启用日志，默认为False
        :param log_level: 日志级别，默认为ERROR
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
        self.max_retries = max(max_retries, 1)  # 至少重试1次
        self.retry_interval = max(retry_interval, 1)  # 至少间隔1秒
        self.pool_size = max(pool_size, 1)  # 至少1个连接
        self.connect_timeout = connect_timeout
        self.read_timeout = read_timeout
        self.write_timeout = write_timeout
        self.ssl = ssl
        self._prepared_statements = {}  # 预处理语句缓存
        self._max_cached_statements = 100  # 最大缓存语句数

        # 初始化日志
        if enable_logging:
            self._init_logging(log_level)
        else:
            self.logger = None

        # 创建连接池
        self.pool = self._create_connection_pool()

    def _init_logging(self, log_level: str):
        """初始化日志配置"""
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        level = log_level.upper() if log_level.upper() in valid_levels else 'ERROR'

        logging.basicConfig(
            level=getattr(logging, level),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[logging.StreamHandler()]
        )
        self.logger = logging.getLogger('MySQLUploader')

    def _create_connection_pool(self) -> PooledDB:
        """创建数据库连接池"""
        pool_params = {
            'creator': pymysql,
            'host': self.host,
            'port': self.port,
            'user': self.username,
            'password': self.password,
            'charset': self.charset,
            'cursorclass': pymysql.cursors.DictCursor,
            'maxconnections': self.pool_size,
            'ping': 7,  # 连接检查
            'connect_timeout': self.connect_timeout,
            'read_timeout': self.read_timeout,
            'write_timeout': self.write_timeout,
            'autocommit': False
        }

        if self.ssl:
            required_keys = {'ca', 'cert', 'key'}
            if not all(k in self.ssl for k in required_keys):
                raise ValueError("SSL配置必须包含ca、cert和key")
            pool_params['ssl'] = {
                'ca': self.ssl['ca'],
                'cert': self.ssl['cert'],
                'key': self.ssl['key'],
                'check_hostname': self.ssl.get('check_hostname', False)
            }

        try:
            pool = PooledDB(**pool_params)
            return pool
        except Exception as e:
            if self.logger:
                self.logger.error("连接池创建失败: %s", str(e))
            raise ConnectionError(f"连接池创建失败: {str(e)}")

    def _validate_datetime(self, value):
        formats = [
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%d',
            '%Y/%m/%d %H:%M:%S',
            '%Y/%m/%d',
            '%Y%m%d',
            '%Y-%m-%dT%H:%M:%S',  # ISO格式
            '%Y-%m-%d %H:%M:%S.%f'  # 带毫秒
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(value, fmt).strftime('%Y-%m-%d %H:%M:%S')
            except ValueError:
                continue
        raise ValueError(f"无效的日期格式: {value}")

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
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 移除可能有害的字符，只保留字母、数字、下划线和美元符号
        cleaned = re.sub(r'[^\w\u4e00-\u9fff$]', '', identifier)
        if not cleaned:
            error_msg = f"无法清理异常标识符: {identifier}"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 检查是否为MySQL保留字
        mysql_keywords = {
            'select', 'insert', 'update', 'delete', 'from', 'where', 'and', 'or',
            'not', 'like', 'in', 'is', 'null', 'true', 'false', 'between'
        }
        if cleaned.lower() in mysql_keywords:
            if self.logger:
                self.logger.warning("存在MySQL保留字: %s", cleaned)
            return f"`{cleaned}`"

        return cleaned

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
                return int(value) if value is not None else None
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
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _execute_with_retry(self, func, *args, **kwargs):
        """
        带重试机制的SQL执行装饰器

        :param func: 要执行的函数
        :param args: 位置参数
        :param kwargs: 关键字参数
        :return: 函数执行结果
        :raises Exception: 如果所有重试都失败
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(self.max_retries):
                try:
                    result = func(*args, **kwargs)
                    if attempt > 0 and self.logger:
                        self.logger.info("Operation succeeded after %d retries", attempt)
                    return result
                except (pymysql.OperationalError, pymysql.err.MySQLError) as e:
                    last_exception = e
                    if attempt < self.max_retries - 1:
                        wait_time = self.retry_interval * (attempt + 1)
                        if self.logger:
                            self.logger.warning(
                                "尝试 %d/%d 失败: %s. %d秒后重试...",
                                attempt + 1, self.max_retries, str(e), wait_time
                            )
                        time.sleep(wait_time)
                        # 尝试重新连接
                        try:
                            self.pool = self._create_connection_pool()
                        except Exception as reconnect_error:
                            if self.logger:
                                self.logger.error("重连失败: %s", str(reconnect_error))
                        continue
                    else:
                        if self.logger:
                            self.logger.error(
                                "Operation failed after %d attempts. Last error: %s",
                                self.max_retries, str(e)
                            )
                except pymysql.IntegrityError as e:
                    # 完整性错误通常不需要重试
                    if self.logger:
                        self.logger.error("完整性约束错误: %s", str(e))
                    raise e
                except Exception as e:
                    last_exception = e
                    if self.logger:
                        self.logger.error("发生意外错误: %s", str(e))
                    break

            raise last_exception if last_exception else Exception("发生未知错误")

        return wrapper(*args, **kwargs)

    def _get_connection(self):
        """从连接池获取连接"""
        try:
            conn = self.pool.connection()
            if self.logger:
                self.logger.debug("成功获取数据库连接")
            return conn
        except Exception as e:
            if self.logger:
                self.logger.error("连接数据库失败: %s", str(e))
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
                    if self.logger:
                        self.logger.debug("数据库 %s 已存在: %s", db_name, exists)
                    return exists
        except Exception as e:
            if self.logger:
                self.logger.error("检查数据库是否存在时出错: %s", str(e))
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
                if self.logger:
                    self.logger.info("数据库 %s 创建成功", db_name)
        except Exception as e:
            if self.logger:
                self.logger.error("无法创建数据库 %s: %s", db_name, str(e))
            conn.rollback()
            raise

    def _check_table_exists(self, db_name: str, table_name: str) -> bool:
        """检查表是否存在"""
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
                    exists = bool(cursor.fetchone())
                    return exists
        except Exception as e:
            if self.logger:
                self.logger.error("检查数据表是否存在时发生未知错误: %s", str(e))
            raise

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
                    columns = {row['COLUMN_NAME']: row['DATA_TYPE'] for row in cursor.fetchall()}
                    if self.logger:
                        self.logger.debug("获取表 %s.%s 的列信息: %s", db_name, table_name, columns)
                    return columns
        except Exception as e:
            if self.logger:
                self.logger.error("无法获取表列信息: %s", str(e))
            raise

    def _prepare_data(
            self,
            data: Union[Dict, List[Dict], pd.DataFrame],
            columns: Dict[str, str],
            allow_null: bool = False
    ) -> List[Dict]:
        """
        准备要上传的数据，验证并转换数据类型

        :param data: 输入数据
        :param columns: 列名和数据类型字典 {列名: 数据类型}
        :param allow_null: 是否允许空值
        :return: 准备好的数据列表
        :raises ValueError: 如果数据验证失败
        """
        # 统一数据格式为字典列表
        if isinstance(data, pd.DataFrame):
            try:
                data = data.replace({pd.NA: None}).to_dict('records')
            except Exception as e:
                if self.logger:
                    self.logger.error("Failed to convert DataFrame to dict: %s", str(e))
                raise ValueError(f"Failed to convert DataFrame to dict: {str(e)}")
        elif isinstance(data, dict):
            data = [data]
        elif not isinstance(data, list) or not all(isinstance(item, dict) for item in data):
            error_msg = "Data must be a dict, list of dicts, or DataFrame"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        prepared_data = []
        for row_idx, row in enumerate(data, 1):
            prepared_row = {}
            for col_name, col_type in columns.items():
                # 跳过id列，不允许外部传入id
                if col_name.lower() == 'id':
                    continue

                if col_name not in row:
                    if not allow_null:
                        error_msg = f"Row {row_idx}: Missing required column '{col_name}' in data"
                        if self.logger:
                            self.logger.error(error_msg)
                        raise ValueError(error_msg)
                    prepared_row[col_name] = None
                else:
                    try:
                        prepared_row[col_name] = self._validate_value(row[col_name], col_type)
                    except ValueError as e:
                        error_msg = f"Row {row_idx}, column '{col_name}': {str(e)}"
                        if self.logger:
                            self.logger.error(error_msg)
                        raise ValueError(error_msg)
            prepared_data.append(prepared_row)

        if self.logger:
            self.logger.debug("已准备 %d 行数据", len(prepared_data))
        return prepared_data

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
            date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d %H:%M:%S')
        except ValueError:
            try:
                date_obj = datetime.datetime.strptime(date_value, '%Y-%m-%d')
            except ValueError:
                error_msg = f"无效的日期格式: {date_value}"
                if self.logger:
                    self.logger.error("无效的日期格式: %s", date_value)
                raise ValueError(error_msg)

        if partition_by == 'year':
            return f"{table_name}_{date_obj.year}"
        elif partition_by == 'month':
            return f"{table_name}_{date_obj.year}_{date_obj.month:02d}"
        else:
            error_msg = "partition_by must be 'year' or 'month'"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

    def _create_table(
            self,
            db_name: str,
            table_name: str,
            columns: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            date_column: Optional[str] = None,
            indexes: Optional[List[str]] = None,
            unique_columns: Optional[List[str]] = None
    ):
        """
        创建数据表

        :param db_name: 数据库名
        :param table_name: 表名
        :param columns: 列名和数据类型字典 {列名: 数据类型}
        :param primary_keys: 主键列列表
        :param date_column: 日期列名，如果存在将设置为索引
        :param indexes: 需要创建索引的列列表
        :param unique_columns: 需要创建唯一索引的列列表
        """
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)

        if not columns:
            error_msg = "No columns specified for table creation"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 构建列定义SQL
        column_defs = ["`id` INT NOT NULL AUTO_INCREMENT"]

        # 添加其他列定义
        for col_name, col_type in columns.items():
            # 跳过id列，因为已经在前面添加了
            if col_name.lower() == 'id':
                continue
            safe_col_name = self._validate_identifier(col_name)
            col_def = f"`{safe_col_name}` {col_type}"

            # 添加NOT NULL约束
            if not col_type.lower().startswith('json'):
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

        # 添加唯一索引定义
        unique_index_sql = ""
        if unique_columns:
            for col in unique_columns:
                if col.lower() != 'id' and col in columns:
                    safe_col = self._validate_identifier(col)
                    unique_index_sql += f", UNIQUE KEY `uk_{safe_col}` (`{safe_col}`)"

        # 构建完整SQL
        sql = f"""
        CREATE TABLE IF NOT EXISTS `{db_name}`.`{table_name}` (
            {','.join(column_defs)}
            {primary_key_sql}
            {unique_index_sql}
        ) ENGINE=InnoDB DEFAULT CHARSET={self.charset} COLLATE={self.collation}
        """

        try:
            with self._get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(sql)
                    if self.logger:
                        self.logger.info("表 %s.%s 创建成功", db_name, table_name)

                # 添加普通索引
                index_statements = []

                # 日期列索引
                if date_column and date_column in columns:
                    safe_date_col = self._validate_identifier(date_column)
                    index_statements.append(
                        f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_date_col}` (`{safe_date_col}`)"
                    )

                # 其他索引
                if indexes:
                    for idx_col in indexes:
                        if idx_col in columns:
                            safe_idx_col = self._validate_identifier(idx_col)
                            index_statements.append(
                                f"ALTER TABLE `{db_name}`.`{table_name}` ADD INDEX `idx_{safe_idx_col}` (`{safe_idx_col}`)"
                            )

                # 执行所有索引创建语句
                if index_statements:
                    with conn.cursor() as cursor:
                        for stmt in index_statements:
                            cursor.execute(stmt)
                            if self.logger:
                                self.logger.debug("Executed index statement: %s", stmt)

                conn.commit()
                if self.logger:
                    self.logger.info("All indexes created successfully for %s.%s", db_name, table_name)

        except Exception as e:
            if self.logger:
                self.logger.error("创建表 %s.%s 失败: %s", db_name, table_name, str(e))
            conn.rollback()
            raise

    def upload_data(
            self,
            db_name: str,
            table_name: str,
            data: Union[Dict, List[Dict], pd.DataFrame],
            columns: Dict[str, str],
            primary_keys: Optional[List[str]] = None,
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            allow_null: bool = False,
            partition_by: Optional[str] = None,
            partition_date_column: str = '日期',
            auto_create: bool = True,
            replace: bool = False,
            indexes: Optional[List[str]] = None
    ):
        """
        上传数据到数据库

        :param db_name: 数据库名
        :param table_name: 表名
        :param data: 要上传的数据
        :param columns: 列名和数据类型字典 {列名: 数据类型}
        :param primary_keys: 主键列列表
        :param check_duplicate: 是否检查重复，默认为False
        :param duplicate_columns: 用于检查重复的列列表，如果不指定则使用所有列
        :param allow_null: 是否允许空值，默认为False
        :param partition_by: 分表方式 ('year' 或 'month')，默认为None不分表
        :param partition_date_column: 用于分表的日期列名，默认为'date'
        :param auto_create: 是否自动创建不存在的数据库或表，默认为True
        :param replace: 是否使用REPLACE代替INSERT，默认为False
        :param indexes: 需要创建索引的列列表
        :raises ValueError: 如果参数无效或操作失败
        """
        if self.logger:
            self.logger.info(
                "开始上传数据到 %s.%s (分表方式=%s, 替换模式=%s)",
                db_name, table_name, partition_by, replace
            )

        # 验证参数
        if not columns:
            error_msg = "Columns specification is required"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        if partition_by and partition_by not in ['year', 'month']:
            error_msg = "分表方式必须是 'year' 或 'month'"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 准备数据
        prepared_data = self._prepare_data(data, columns, allow_null)

        # 检查数据库是否存在
        if not self._check_database_exists(db_name):
            if auto_create:
                self._create_database(db_name)
            else:
                error_msg = f"Database '{db_name}' does not exist"
                if self.logger:
                    self.logger.error(error_msg)
                raise ValueError(error_msg)

        # 确定唯一索引列
        unique_columns = None
        if check_duplicate:
            unique_columns = duplicate_columns if duplicate_columns else [col for col in columns.keys() if
                                                                          col.lower() != 'id']

        # 处理分表逻辑
        if partition_by:
            # 分组数据按分表
            partitioned_data = {}
            for row in prepared_data:
                if partition_date_column not in row:
                    error_msg = f"异常缺失列 '{partition_date_column}'"
                    if self.logger:
                        self.logger.error(error_msg)
                    raise ValueError(error_msg)
                part_table = self._get_partition_table_name(table_name, str(row[partition_date_column]), partition_by)
                if part_table not in partitioned_data:
                    partitioned_data[part_table] = []
                partitioned_data[part_table].append(row)

            # 对每个分表执行上传
            for part_table, part_data in partitioned_data.items():
                self._upload_to_table(
                    db_name, part_table, part_data, columns,
                    primary_keys, check_duplicate, duplicate_columns,
                    allow_null, auto_create, partition_date_column,
                    replace, indexes, unique_columns
                )
        else:
            # 不分表，直接上传
            self._upload_to_table(
                db_name, table_name, prepared_data, columns,
                primary_keys, check_duplicate, duplicate_columns,
                allow_null, auto_create, partition_date_column,
                replace, indexes, unique_columns
            )

        if self.logger:
            self.logger.info(
                "成功上传 %d 行数据到 %s.%s",
                len(prepared_data), db_name, table_name
            )

    def _upload_to_table(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            columns: Dict[str, str],
            primary_keys: Optional[List[str]],
            check_duplicate: bool,
            duplicate_columns: Optional[List[str]],
            allow_null: bool,
            auto_create: bool,
            date_column: Optional[str],
            replace: bool,
            indexes: Optional[List[str]],
            unique_columns: Optional[List[str]] = None
    ):
        """实际执行表上传的内部方法"""
        # 检查表是否存在
        if not self._check_table_exists(db_name, table_name):
            if auto_create:
                self._create_table(db_name, table_name, columns, primary_keys, date_column, indexes, unique_columns)
            else:
                error_msg = f"Table '{db_name}.{table_name}' does not exist"
                if self.logger:
                    self.logger.error(error_msg)
                raise ValueError(error_msg)

        # 获取表结构并验证
        table_columns = self._get_table_columns(db_name, table_name)
        if not table_columns:
            error_msg = f"Failed to get columns for table '{db_name}.{table_name}'"
            if self.logger:
                self.logger.error(error_msg)
            raise ValueError(error_msg)

        # 验证数据列与表列匹配
        for col in columns:
            if col not in table_columns:
                error_msg = f"Column '{col}' not found in table '{db_name}.{table_name}'"
                if self.logger:
                    self.logger.error(error_msg)
                raise ValueError(error_msg)

        # 插入数据
        self._insert_data(
            db_name, table_name, data, columns,
            check_duplicate, duplicate_columns,
            replace=replace
        )

    def _insert_data(
            self,
            db_name: str,
            table_name: str,
            data: List[Dict],
            columns: Dict[str, str],
            check_duplicate: bool = False,
            duplicate_columns: Optional[List[str]] = None,
            batch_size: int = 1000,
            replace: bool = False
    ):
        """
        插入数据到表中

        :param db_name: 数据库名
        :param table_name: 表名
        :param data: 要插入的数据
        :param columns: 列名和数据类型字典
        :param check_duplicate: 是否检查重复
        :param duplicate_columns: 用于检查重复的列列表
        :param batch_size: 批量插入的大小
        :param replace: 是否使用REPLACE代替INSERT
        :raises Exception: 如果插入失败
        """
        db_name = self._validate_identifier(db_name)
        table_name = self._validate_identifier(table_name)

        if not data:
            if self.logger:
                self.logger.warning("No data to insert into %s.%s", db_name, table_name)
            return

        # 获取所有列名
        all_columns = [col for col in columns.keys() if col.lower() != 'id']
        safe_columns = [self._validate_identifier(col) for col in all_columns]
        placeholders = ','.join(['%s'] * len(safe_columns))

        # 构建SQL语句
        operation = "REPLACE" if replace else "INSERT IGNORE" if check_duplicate else "INSERT"

        if check_duplicate and not replace:
            # 当check_duplicate=True时，使用INSERT IGNORE来跳过重复记录
            sql = f"""
            {operation} INTO `{db_name}`.`{table_name}` 
            (`{'`,`'.join(safe_columns)}`) 
            VALUES ({placeholders})
            """
        else:
            sql = f"""
            {operation} INTO `{db_name}`.`{table_name}` 
            (`{'`,`'.join(safe_columns)}`) 
            VALUES ({placeholders})
            """

        if len(self._prepared_statements) >= self._max_cached_statements:
            # 移除最旧的缓存
            oldest_key = next(iter(self._prepared_statements))
            del self._prepared_statements[oldest_key]

        # 缓存预处理语句
        cache_key = f"{db_name}.{table_name}.{operation}.{check_duplicate}"
        if cache_key not in self._prepared_statements:
            self._prepared_statements[cache_key] = sql
            if self.logger:
                self.logger.debug("已缓存预处理语句: %s", cache_key)

        # 分批插入数据
        with self._get_connection() as conn:
            with conn.cursor() as cursor:
                for i in range(0, len(data), batch_size):
                    batch = data[i:i + batch_size]
                    # 准备批量数据
                    values = []
                    for row in batch:
                        row_values = []
                        for col in all_columns:
                            row_values.append(row.get(col))
                        values.append(row_values)

                    # 执行批量插入
                    try:
                        start_time = time.time()
                        cursor.executemany(sql, values)
                        conn.commit()  # 每个批次提交一次
                        if self.logger:
                            self.logger.debug(
                                "成功插入批次 %d-%d/%d 到 %s.%s, 耗时 %.2f 秒",
                                i + 1, min(i + batch_size, len(data)), len(data),
                                db_name, table_name, time.time() - start_time
                            )
                    except Exception as e:
                        conn.rollback()
                        error_msg = f"Failed to insert batch {i + 1}-{min(i + batch_size, len(data))}/{len(data)} into {db_name}.{table_name}: {str(e)}"
                        if self.logger:
                            self.logger.error(error_msg)
                        raise Exception(error_msg)

    def close(self):
        """关闭连接池"""
        if hasattr(self, 'pool') and self.pool:
            try:
                # 先关闭所有连接
                while True:
                    conn = getattr(self.pool, '_connections', None)
                    if not conn or not conn.queue:
                        break
                    try:
                        conn = self.pool.connection()
                        conn.close()
                    except:
                        pass

                # 然后关闭连接池
                self.pool.close()
                if self.logger:
                    self.logger.info("连接池已成功关闭")
            except Exception as e:
                if self.logger:
                    self.logger.error("关闭连接池失败: %s", str(e))
                raise
        self.pool = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type is not None and self.logger:
            self.logger.error(
                "Exception occurred: %s: %s",
                exc_type.__name__, str(exc_val),
                exc_info=(exc_type, exc_val, exc_tb)
            )


class MysqlUpload:
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        if username == '' or password == '' or host == '' or port == 0:
            self.config = None
        else:
            self.config = {
                'host': self.host,
                'port': int(self.port),
                'user': self.username,
                'password': self.password,
                'charset': charset,  # utf8mb4 支持存储四字节的UTF-8字符集
                'cursorclass': pymysql.cursors.DictCursor,
            }
        self.filename = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def keep_connect(self, _db_name, _config, max_try: int=10):
        attempts = 1
        while attempts <= max_try:
            try:
                connection = pymysql.connect(**_config)  # 连接数据库
                return connection
            except Exception as e:
                logger.error(f'{_db_name}: 连接失败，正在重试: {self.host}:{self.port}  {attempts}/{max_try} {e}')
                attempts += 1
                time.sleep(30)
        logger.error(f'{_db_name}: 连接失败，重试次数超限，当前设定次数: {max_try}')
        return None

    def cover_doc_dtypes(self, dict_data):
        """ 清理字典键值 并转换数据类型  """
        if not dict_data:
            logger.info(f'mysql.py -> MysqlUpload -> cover_dict_dtypes -> 传入的字典不能为空')
            return
        __res_dict = {}
        new_dict_data = {}
        for k, v in dict_data.items():
            k = str(k).lower()
            k = re.sub(r'[()\-，,$&~^、 （）\"\'“”=·/。》《><！!`]', '_', k, re.IGNORECASE)
            k = k.replace('）', '')
            k = re.sub(r'_{2,}', '_', k)
            k = re.sub(r'_+$', '', k)
            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            date_type = otk.is_valid_date(v)  # 判断日期时间
            int_num = otk.is_integer(v)  # 判断整数
            count_int, count_float = count_decimal_places(v)  # 判断小数，返回小数位数
            if result1:  # 京东sku/spu商品信息
                __res_dict.update({k: 'varchar(100)'})
            elif k == '日期':
                __res_dict.update({k: 'DATE'})
            elif k == '更新时间':
                __res_dict.update({k: 'TIMESTAMP'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif date_type == 1:  # 纯日期
                __res_dict.update({k: 'DATE'})
            elif date_type == 2:  # 日期+时间
                __res_dict.update({k: 'DATETIME'})
            elif int_num:
                __res_dict.update({k: 'INT'})
            elif count_float > 0:
                if count_int + count_float > 10:
                    if count_float >= 6:
                        __res_dict.update({k: 'decimal(14,6)'})
                    else:
                        __res_dict.update({k: 'decimal(14,4)'})
                elif count_float >= 6:
                    __res_dict.update({k: 'decimal(14,6)'})
                elif count_float >= 4:
                    __res_dict.update({k: 'decimal(12,4)'})
                else:
                    __res_dict.update({k: 'decimal(10,2)'})
            else:
                __res_dict.update({k: 'varchar(255)'})
            new_dict_data.update({k: v})
        __res_dict.update({'数据主体': 'longblob'})
        return __res_dict, new_dict_data

    @try_except
    def insert_many_dict(self, db_name, table_name, dict_data_list, icm_update=None, index_length=100, set_typ=None, allow_not_null=False, cut_data=None):
        """
        插入字典数据
        dict_data： 字典
        index_length: 索引长度
        icm_update: 增量更正
        set_typ: {}
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return

        if not dict_data_list:
            logger.info(f'dict_data_list 不能为空 ')
            return
        dict_data = dict_data_list[0]
        if cut_data:
            if '日期' in dict_data.keys():
                try:
                    __y = pd.to_datetime(dict_data['日期']).strftime('%Y')
                    __y_m = pd.to_datetime(dict_data['日期']).strftime('%Y-%m')
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{__y}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{__y_m}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY);"
                cursor.execute(sql)
                logger.info(f'创建 mysql 表: {table_name}')

            # 根据 dict_data 的值添加指定的数据类型
            dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
            if set_typ:
                # 更新自定义的列数据类型
                for k, v in dtypes.copy().items():
                    # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                    [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

            # 检查列
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]  # 已存在的所有列
            col_not_exist = [col for col in dict_data.keys() if col not in col_exist]  # 不存在的列
            # 不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    if allow_not_null:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]};"
                    else:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]} NOT NULL;"

                    cursor.execute(sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    if col == '日期':
                        sql = f"CREATE INDEX index_name ON `{table_name}`(`{col}`);"
                        logger.info(f"设置为索引: {col}({dtypes[col]})")
                        cursor.execute(sql)

            connection.commit()  # 提交事务
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 处理插入的数据
            for dict_data in dict_data_list:
                dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
                if icm_update:
                    """ 使用增量更新: 需确保 icm_update['主键'] 传进来的列组合是数据表中唯一，值不会发生变化且不会重复，否则可能产生覆盖 """
                    sql = 'SELECT COLUMN_NAME FROM information_schema.columns WHERE table_schema = %s AND table_name = %s'
                    cursor.execute(sql, (db_name, table_name))
                    columns = cursor.fetchall()
                    cols_exist = [col['COLUMN_NAME'] for col in columns]  # 数据表的所有列, 返回 list
                    # 保留原始列名，不提前转义
                    raw_update_col = [item for item in cols_exist if item not in icm_update and item != 'id']  # 除了主键外的其他列

                    # 构建条件参数（使用原始列名）
                    condition_params = []
                    condition_parts = []
                    for up_col in icm_update:
                        condition_parts.append(f"`{up_col}` = %s")  # SQL 转义
                        condition_params.append(dict_data[up_col])  # 原始列名用于访问数据

                    # 动态转义列名生成 SQL 查询字段
                    escaped_update_col = [f'`{col}`' for col in raw_update_col]
                    sql = f"""SELECT {','.join(escaped_update_col)} FROM `{table_name}` WHERE {' AND '.join(condition_parts)}"""
                    cursor.execute(sql, condition_params)
                    results = cursor.fetchall()

                    if results:
                        for result in results:
                            change_col = []
                            change_placeholders = []
                            set_params = []
                            for raw_col in raw_update_col:
                                # 使用原始列名访问数据
                                df_value = str(dict_data[raw_col])
                                mysql_value = str(result[raw_col])

                                # 清理小数点后多余的零
                                if '.' in df_value:
                                    df_value = re.sub(r'0+$', '', df_value).rstrip('.')
                                if '.' in mysql_value:
                                    mysql_value = re.sub(r'0+$', '', mysql_value).rstrip('.')

                                if df_value != mysql_value:
                                    change_placeholders.append(f"`{raw_col}` = %s")  # 动态转义列名
                                    set_params.append(dict_data[raw_col])
                                    change_col.append(raw_col)

                            if change_placeholders:
                                full_params = set_params + condition_params
                                sql = f"""UPDATE `{table_name}` 
                                             SET {','.join(change_placeholders)} 
                                             WHERE {' AND '.join(condition_parts)}"""
                                cursor.execute(sql, full_params)
                    else:  # 没有数据返回，则直接插入数据
                        # 参数化插入
                        cols = ', '.join([f'`{k}`' for k in dict_data.keys()])
                        placeholders = ', '.join(['%s'] * len(dict_data))
                        sql = f"INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders})"
                        cursor.execute(sql, tuple(dict_data.values()))
                    connection.commit()  # 提交数据库
                    continue

                # 标准插入逻辑（参数化修改）
                # 构造更新列（排除主键）
                update_cols = [k for k in dict_data.keys()]
                # 构建SQL
                cols = ', '.join([f'`{k}`' for k in dict_data.keys()])
                placeholders = ', '.join(['%s'] * len(dict_data))
                update_clause = ', '.join([f'`{k}` = VALUES(`{k}`)' for k in update_cols]) or 'id=id'

                sql = f"""INSERT INTO `{table_name}` ({cols}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
                # 执行参数化查询
                try:
                    cursor.execute(sql, tuple(dict_data.values()))
                    connection.commit()
                except pymysql.Error as e:
                    logger.error(f"插入失败: {e}\nSQL: {cursor.mogrify(sql, tuple(dict_data.values()))}")
                    connection.rollback()
        connection.close()

    # @try_except
    def dict_to_mysql(self, db_name, table_name, dict_data, icm_update=None, index_length=100, set_typ=None, allow_not_null=False, cut_data=None):
        """
        插入字典数据
        dict_data： 字典
        index_length: 索引长度
        icm_update: 增量更新
        set_typ: {}
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return

        if cut_data:
            if '日期' in dict_data.keys():
                try:
                    __y = pd.to_datetime(dict_data['日期']).strftime('%Y')
                    __y_m = pd.to_datetime(dict_data['日期']).strftime('%Y-%m')
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{__y}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{__y_m}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY);"
                cursor.execute(sql)
                logger.info(f'创建 mysql 表: {table_name}')

            # 根据 dict_data 的值添加指定的数据类型
            dtypes, dict_data = self.cover_dict_dtypes(dict_data=dict_data)  # {'店铺名称': 'varchar(100)',...}
            if set_typ:
                # 更新自定义的列数据类型
                for k, v in dtypes.copy().items():
                    # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                    [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

            # 检查列
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]  # 已存在的所有列
            col_not_exist = [col for col in dict_data.keys() if col not in col_exist]  # 不存在的列
            # 不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    if allow_not_null:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]};"
                    else:
                        sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]} NOT NULL;"
                    cursor.execute(sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    if col == '日期':
                        sql = f"CREATE INDEX index_name ON `{table_name}`(`{col}`);"
                        logger.info(f"设置为索引: {col}({dtypes[col]})")
                        cursor.execute(sql)
            connection.commit()  # 提交事务
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            """"""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""
            # 处理插入的数据
            if icm_update:
                """ 使用增量更新: 需确保 icm_update['主键'] 传进来的列组合是数据表中唯一，值不会发生变化且不会重复，否则可能产生覆盖 """
                sql = """SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s"""
                cursor.execute(sql, (db_name, table_name))
                cols_exist = [col['COLUMN_NAME'] for col in cursor.fetchall()] # 数据表的所有列, 返回 list

                # 保留原始列名，不提前转义
                raw_update_col = [item for item in cols_exist if item not in icm_update and item != 'id']

                # 构建条件参数（使用原始列名）
                condition_params = []
                condition_parts = []
                for up_col in icm_update:
                    condition_parts.append(f"`{up_col}` = %s")  # SQL 转义
                    condition_params.append(dict_data[up_col])  # 原始列名访问数据

                # 动态转义列名生成 SQL 查询字段
                escaped_update_col = [f'`{col}`' for col in raw_update_col]
                sql = f"""SELECT {','.join(escaped_update_col)} FROM `{table_name}` WHERE {' AND '.join(condition_parts)}"""
                cursor.execute(sql, condition_params)
                results = cursor.fetchall()

                if results:
                    for result in results:
                        change_col = []
                        change_placeholders = []
                        set_params = []
                        for raw_col in raw_update_col:
                            # 使用原始列名访问数据
                            df_value = str(dict_data[raw_col])
                            mysql_value = str(result[raw_col])

                            # 清理小数点后多余的零
                            if '.' in df_value:
                                df_value = re.sub(r'0+$', '', df_value).rstrip('.')
                            if '.' in mysql_value:
                                mysql_value = re.sub(r'0+$', '', mysql_value).rstrip('.')

                            if df_value != mysql_value:
                                change_placeholders.append(f"`{raw_col}` = %s")  # 动态转义列名
                                set_params.append(dict_data[raw_col])
                                change_col.append(raw_col)

                        if change_placeholders:
                            full_params = set_params + condition_params
                            sql = f"""UPDATE `{table_name}` 
                                         SET {','.join(change_placeholders)} 
                                         WHERE {' AND '.join(condition_parts)}"""
                            cursor.execute(sql, full_params)
                else:  # 没有数据返回，则直接插入数据
                    # 参数化插入语句
                    keys = [f"`{k}`" for k in dict_data.keys()]
                    placeholders = ','.join(['%s'] * len(dict_data))
                    update_clause = ','.join([f"`{k}`=VALUES(`{k}`)" for k in dict_data.keys()])
                    sql = f"""INSERT INTO `{table_name}` ({','.join(keys)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
                    cursor.execute(sql, tuple(dict_data.values()))
                connection.commit()  # 提交数据库
                connection.close()
                return

            # 常规插入处理（参数化）
            keys = [f"`{k}`" for k in dict_data.keys()]
            placeholders = ','.join(['%s'] * len(dict_data))
            update_clause = ','.join([f"`{k}`=VALUES(`{k}`)" for k in dict_data.keys()])
            sql = f"""INSERT INTO `{table_name}` ({','.join(keys)}) VALUES ({placeholders}) ON DUPLICATE KEY UPDATE {update_clause}"""
            cursor.execute(sql, tuple(dict_data.values()))
            connection.commit()
        connection.close()

    def cover_dict_dtypes(self, dict_data):
        """ 清理字典键值 并转换数据类型  """
        if not dict_data:
            logger.info(f'mysql.py -> MysqlUpload -> cover_dict_dtypes -> 传入的字典不能为空')
            return
        __res_dict = {}
        new_dict_data = {}
        for k, v in dict_data.items():
            k = str(k).lower()
            k = re.sub(r'[()\-，,$&~^、 （）\"\'“”=·/。》《><！!`]', '_', k, re.IGNORECASE)
            k = k.replace('）', '')
            k = re.sub(r'_{2,}', '_', k)
            k = re.sub(r'_+$', '', k)
            if str(v) == '':
                v = 0
            v = str(v)
            v = re.sub('^="|"$', '', v, re.I)
            v = re.sub(r'[\x00-\x1F\x7F-\x9F]', '', str(v))  # 移除控制字符
            if re.findall(r'^[-+]?\d+\.?\d*%$', v):
                v = str(float(v.rstrip("%")) / 100)

            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            date_type = otk.is_valid_date(v)  # 判断日期时间
            int_num = otk.is_integer(v)  # 判断整数
            count_int, count_float = count_decimal_places(v)  # 判断小数，返回小数位数
            if result1:  # 京东sku/spu商品信息
                __res_dict.update({k: 'varchar(100)'})
            elif k == '日期':
                __res_dict.update({k: 'DATE'})
            elif k == '更新时间':
                __res_dict.update({k: 'TIMESTAMP'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif date_type == 1:  # 纯日期
                __res_dict.update({k: 'DATE'})
            elif date_type == 2:  # 日期+时间
                __res_dict.update({k: 'DATETIME'})
            elif int_num:
                __res_dict.update({k: 'INT'})
            elif count_float > 0:
                if count_int + count_float > 10:
                    # if count_float > 5:
                    #     v = round(float(v), 4)
                    if count_float >= 6:
                        __res_dict.update({k: 'decimal(14,6)'})
                    else:
                        __res_dict.update({k: 'decimal(14,4)'})
                elif count_float >= 6:
                    __res_dict.update({k: 'decimal(14,6)'})
                elif count_float >= 4:
                    __res_dict.update({k: 'decimal(12,4)'})
                else:
                    __res_dict.update({k: 'decimal(10,2)'})
            else:
                __res_dict.update({k: 'varchar(255)'})
            new_dict_data.update({k: v})
        return __res_dict, new_dict_data

    def convert_df_dtypes(self, df: pd.DataFrame):
        """ 清理 df 的值和列名，并转换数据类型 """
        df = otk.cover_df(df=df)  # 清理 df 的值和列名
        [pd.to_numeric(df[col], errors='ignore') for col in df.columns.tolist()]
        dtypes = df.dtypes.to_dict()
        __res_dict = {}
        for k, v in dtypes.copy().items():
            result1 = re.findall(r'编码|_?id|货号|款号|文件大小', k, re.IGNORECASE)
            result2 = re.findall(r'占比$|投产$|产出$|roi$|率$', k, re.IGNORECASE)
            result3 = re.findall(r'同比$|环比$', k, re.IGNORECASE)
            result4 = re.findall(r'花费$|消耗$|金额$', k, re.IGNORECASE)

            if result1:  # id/sku/spu商品信息
                __res_dict.update({k: 'varchar(50)'})
            elif result2:  # 小数
                __res_dict.update({k: 'decimal(10,4)'})
            elif result3:  # 小数
                __res_dict.update({k: 'decimal(12,4)'})
            elif result4:  # 小数
                __res_dict.update({k: 'decimal(12,2)'})
            elif k == '日期':
                __res_dict.update({k: 'date'})
            elif k == '更新时间':
                __res_dict.update({k: 'timestamp'})
            elif v == 'int64':
                __res_dict.update({k: 'int'})
            elif v == 'float64':
                __res_dict.update({k: 'decimal(10,4)'})
            elif v == 'bool':
                __res_dict.update({k: 'boolean'})
            elif v == 'datetime64[ns]':
                __res_dict.update({k: 'datetime'})
            else:
                __res_dict.update({k: 'varchar(255)'})
        return __res_dict, df

    @try_except
    def df_to_mysql(self, df, db_name, table_name, set_typ=None, icm_update=[], move_insert=False, df_sql=False,
                    filename=None, count=None, allow_not_null=False, cut_data=None):
        """
        db_name: 数据库名
        table_name: 表名
        move_insert: 根据df 的日期，先移除数据库数据，再插入, df_sql, icm_update 都要设置为 False
        原则上只限于聚合数据使用，原始数据插入时不要设置
        df_sql: 这是一个临时参数, 值为 True 时使用 df.to_sql 函数上传整个表, 不会排重，初创表大量上传数据的时候使用
        icm_update: 增量更新, 在聚合数据中使用，原始文件不要使用
                使用增量更新: 必须确保 icm_update 传进来的列必须是数据表中唯一主键，值不会发生变化，不会重复，否则可能产生错乱覆盖情况
        filename: 用来追踪处理进度，传这个参数是方便定位产生错误的文件
        allow_not_null: 创建允许插入空值的列，正常情况下不允许空值
        """
        if not self.config:
            return
        if icm_update:
            if move_insert or df_sql:
                logger.info(f'icm_update/move_insert/df_sql 参数不能同时设定')
                return
        if move_insert:
            if icm_update or df_sql:
                logger.info(f'icm_update/move_insert/df_sql 参数不能同时设定')
                return

        self.filename = filename
        if isinstance(df, pd.DataFrame):
            if len(df) == 0:
                logger.info(f'{db_name}: {table_name} 传入的 df 数据长度为0, {self.filename}')
                return
        else:
            logger.info(f'{db_name}: {table_name} 传入的 df 不是有效的 dataframe 结构, {self.filename}')
            return
        if not db_name or db_name == 'None':
            logger.info(f'{db_name} 不能为 None')
            return

        if cut_data:
            if '日期' in df.columns.tolist():
                try:
                    df['日期'] = pd.to_datetime(df['日期'], format='%Y-%m-%d', errors='ignore')
                    min_year = df['日期'].min(skipna=True).year
                    min_month = df['日期'].min(skipna=True).month
                    if 0 < int(min_month) < 10 and not str(min_month).startswith('0'):
                        min_month = f'0{min_month}'
                    if str(cut_data).lower() == 'year':
                        table_name = f'{table_name}_{min_year}'
                    elif str(cut_data).lower() == 'month':
                        table_name = f'{table_name}_{min_year}-{min_month}'
                    else:
                        logger.info(f'参数不正确，cut_data应为 year 或 month ')
                except Exception as e:
                    logger.error(f'{table_name} 将数据按年/月保存(cut_data)，但在转换日期时报错 -> {e}')
        # 清理 dataframe 非法值，并转换获取数据类型
        dtypes, df = self.convert_df_dtypes(df)
        if set_typ:
            # 更新自定义的列数据类型
            for k, v in dtypes.copy().items():
                # 确保传进来的 set_typ 键存在于实际的 df 列才 update
                [dtypes.update({k: inside_v}) for inside_k, inside_v in set_typ.items() if k == inside_k]

        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES LIKE %s", (db_name,))  # 检查数据库是否存在
            database_exists = cursor.fetchone()
            if not database_exists:
                # 如果数据库不存在，则新建
                sql = f"CREATE DATABASE `{db_name}` COLLATE utf8mb4_0900_ai_ci"
                cursor.execute(sql)
                connection.commit()
                logger.info(f"创建Database: {db_name}")

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            # 1. 查询表, 不存在则创建一个空表
            sql = "SHOW TABLES LIKE %s;"  # 有特殊字符不需转义
            cursor.execute(sql, (table_name,))
            if not cursor.fetchone():
                create_table_sql = f"CREATE TABLE IF NOT EXISTS `{table_name}` (id INT AUTO_INCREMENT PRIMARY KEY)"
                cursor.execute(create_table_sql)
                logger.info(f'创建 mysql 表: {table_name}')

            #  有特殊字符不需转义
            sql = "SELECT COLUMN_NAME FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s;"
            cursor.execute(sql, (db_name, table_name))
            col_exist = [item['COLUMN_NAME'] for item in cursor.fetchall()]
            cols = df.columns.tolist()
            col_not_exist = [col for col in cols if col not in col_exist]

            # 检查列，不存在则新建列
            if col_not_exist:  # 数据表中不存在的列
                for col in col_not_exist:
                    #  创建列，需转义
                    alter_sql = f"ALTER TABLE `{table_name}` ADD COLUMN `{col}` {dtypes[col]}"
                    if not allow_not_null:
                        alter_sql += " NOT NULL"
                    cursor.execute(alter_sql)
                    logger.info(f"添加列: {col}({dtypes[col]})")  # 添加列并指定数据类型

                    # 创建索引
                    if col == '日期':
                        sql = f"SHOW INDEXES FROM `{table_name}` WHERE `Column_name` = %s"
                        cursor.execute(sql, (col,))
                        result = cursor.fetchone()  # 检查索引是否存在
                        if not result:
                            cursor.execute(f"CREATE INDEX index_name ON `{table_name}`(`{col}`)")
            connection.commit()  # 提交事务

            if df_sql:
                logger.info(f'正在更新: mysql ({self.host}:{self.port}) {db_name}/{table_name}, {count}, {self.filename}')
                engine = create_engine(
                    f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}")  # 创建数据库引擎
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=1000,
                    method='multi'
                )
                connection.commit()  # 提交事务
                connection.close()
                return

            # 5. 移除指定日期范围内的数据，原则上只限于聚合数据使用，原始数据插入时不要设置
            if move_insert and '日期' in df.columns.tolist():
                # 移除数据
                dates = df['日期'].values.tolist()
                dates = [pd.to_datetime(item) for item in dates]  # 需要先转换类型才能用 min, max
                start_date = pd.to_datetime(min(dates)).strftime('%Y-%m-%d')
                end_date = (pd.to_datetime(max(dates)) + datetime.timedelta(days=1)).strftime('%Y-%m-%d')

                delete_sql = f"""
                                DELETE FROM `{table_name}` 
                                WHERE 日期 BETWEEN %s AND %s
                            """
                cursor.execute(delete_sql, (start_date, end_date))
                connection.commit()

                # 插入数据
                engine = create_engine(
                    f"mysql+pymysql://{self.username}:{self.password}@{self.host}:{self.port}/{db_name}")  # 创建数据库引擎
                df.to_sql(
                    name=table_name,
                    con=engine,
                    if_exists='append',
                    index=False,
                    chunksize=1000,
                    method='multi'
                )
                return

            datas = df.to_dict(orient='records')
            for data in datas:
                # data 是传进来待处理的数据, 不是数据库数据
                # data 示例: {'日期': Timestamp('2024-08-27 00:00:00'), '推广费余额': 33299, '品销宝余额': 2930.73, '短信剩余': 67471}
                try:
                    # 预处理数据：转换非字符串类型
                    processed_data = {}
                    for k, v in data.items():
                        if isinstance(v, (int, float)):
                            processed_data[k] = float(v)
                        elif isinstance(v, pd.Timestamp):
                            processed_data[k] = v.strftime('%Y-%m-%d')
                        else:
                            processed_data[k] = str(v)

                    # 构建基础SQL要素
                    columns = [f'`{k}`' for k in processed_data.keys()]
                    placeholders = ', '.join(['%s'] * len(processed_data))
                    values = list(processed_data.values())

                    # 构建基本INSERT语句
                    insert_sql = f"INSERT INTO `{table_name}` ({', '.join(columns)}) VALUES ({placeholders})"

                    if icm_update:  # 增量更新, 专门用于聚合数据，其他库不要调用
                        # 获取数据表结构
                        cursor.execute(
                            "SELECT COLUMN_NAME FROM information_schema.columns "
                            "WHERE table_schema = %s AND table_name = %s",
                            (db_name, table_name)
                        )
                        cols_exist = [row['COLUMN_NAME'] for row in cursor.fetchall()]
                        update_columns = [col for col in cols_exist if col not in icm_update and col != 'id']

                        # 构建WHERE条件
                        where_conditions = []
                        where_values = []
                        for col in icm_update:
                            where_conditions.append(f"`{col}` = %s")
                            where_values.append(processed_data[col])

                        # 查询现有数据
                        select_sql = f"SELECT {', '.join([f'`{col}`' for col in update_columns])} " \
                                     f"FROM `{table_name}` WHERE {' AND '.join(where_conditions)}"
                        cursor.execute(select_sql, where_values)
                        existing_data = cursor.fetchone()

                        if existing_data:
                            # 比较并构建更新语句
                            update_set = []
                            update_values = []
                            for col in update_columns:
                                db_value = existing_data[col]
                                new_value = processed_data[col]

                                # 处理数值类型的精度差异
                                if isinstance(db_value, float) and isinstance(new_value, float):
                                    if not math.isclose(db_value, new_value, rel_tol=1e-9):
                                        update_set.append(f"`{col}` = %s")
                                        update_values.append(new_value)
                                elif db_value != new_value:
                                    update_set.append(f"`{col}` = %s")
                                    update_values.append(new_value)

                            if update_set:
                                update_sql = f"UPDATE `{table_name}` SET {', '.join(update_set)} " \
                                             f"WHERE {' AND '.join(where_conditions)}"
                                cursor.execute(update_sql, update_values + where_values)
                        else:
                            cursor.execute(insert_sql, values)
                    else:
                        # 普通插入
                        cursor.execute(insert_sql, values)
                except Exception as e:
                    pass
        connection.commit()  # 提交事务
        connection.close()


class OptimizeDatas:
    """
    数据维护 删除 mysql 的冗余数据
    更新过程:
    1. 读取所有数据表
    2. 遍历表, 遍历列, 如果存在日期列则按天遍历所有日期, 不存在则全表读取
    3. 按天删除所有冗余数据(存在日期列时)
    tips: 查找冗余数据的方式是创建一个临时迭代器, 逐行读取数据并添加到迭代器, 出现重复时将重复数据的 id 添加到临时列表, 按列表 id 执行删除
    """
    def __init__(self, username: str, password: str, host: str, port: int, charset: str = 'utf8mb4'):
        self.username = username
        self.password = password
        self.host = host
        self.port = port  # 默认端口, 此后可能更新，不作为必传参数
        self.charset = charset
        self.config = {
            'host': self.host,
            'port': int(self.port),
            'user': self.username,
            'password': self.password,
            'charset': self.charset,  # utf8mb4 支持存储四字节的UTF-8字符集
            'cursorclass': pymysql.cursors.DictCursor,
        }
        self.db_name_lists: list = []  # 更新多个数据库 删除重复数据
        self.db_name = None
        self.days: int = 63  # 对近 N 天的数据进行排重
        self.end_date = None
        self.start_date = None
        self.connection = None

    @staticmethod
    def try_except(func):  # 在类内部定义一个异常处理方法

        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                logger.error(f'{func.__name__}, {e}')  # 将异常信息返回

        return wrapper

    def keep_connect(self, _db_name, _config, max_try: int=10):
        attempts = 1
        while attempts <= max_try:
            try:
                connection = pymysql.connect(**_config)  # 连接数据库
                return connection
            except Exception as e:
                logger.error(f'{_db_name}连接失败，正在重试: {self.host}:{self.port}  {attempts}/{max_try} {e}')
                attempts += 1
                time.sleep(30)
        logger.error(f'{_db_name}: 连接失败，重试次数超限，当前设定次数: {max_try}')
        return None

    def optimize_list(self):
        """
        更新多个数据库 移除冗余数据
        需要设置 self.db_name_lists
        """
        if not self.db_name_lists:
            logger.info(f'尚未设置参数: self.db_name_lists')
            return
        for db_name in self.db_name_lists:
            self.db_name = db_name
            self.optimize()

    def optimize(self, except_key=['更新时间']):
        """ 更新一个数据库 移除冗余数据 """
        if not self.db_name:
            logger.info(f'尚未设置参数: self.db_name')
            return
        tables = self.table_list(db_name=self.db_name)
        if not tables:
            logger.info(f'{self.db_name} -> 数据表不存在')
            return

        # 日期初始化
        if not self.end_date:
            self.end_date = pd.to_datetime(datetime.datetime.today())
        else:
            self.end_date = pd.to_datetime(self.end_date)
        if self.days:
            self.start_date = pd.to_datetime(self.end_date - datetime.timedelta(days=self.days))
        if not self.start_date:
            self.start_date = self.end_date
        else:
            self.start_date = pd.to_datetime(self.start_date)
        start_date_before = self.start_date
        end_date_before = self.end_date

        logger.info(f'mysql({self.host}: {self.port}) {self.db_name} 数据库优化中(日期长度: {self.days} 天)...')
        for table_dict in tables:
            for key, table_name in table_dict.items():
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
                if not self.connection:
                    return
                with self.connection.cursor() as cursor:
                    sql = f"SELECT 1 FROM `{table_name}` LIMIT 1"
                    cursor.execute(sql)
                    result = cursor.fetchone()
                    if not result:
                        logger.info(f'数据表: {table_name}, 数据长度为 0')
                        continue  # 检查数据表是否为空

                    cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    date_exist = False
                    for col in columns:  # 遍历列信息，检查是否存在类型为日期的列
                        if col['Field'] == '日期' and (col['Type'] == 'date' or col['Type'].startswith('datetime')):
                            date_exist = True
                            break
                    if date_exist:  # 存在日期列
                        sql_max = f"SELECT MAX(日期) AS max_date FROM `{table_name}`"
                        sql_min = f"SELECT MIN(日期) AS min_date FROM `{table_name}`"
                        cursor.execute(sql_max)
                        max_result = cursor.fetchone()
                        cursor.execute(sql_min)
                        min_result = cursor.fetchone()
                        # 匹配修改为合适的起始和结束日期
                        if self.start_date < pd.to_datetime(min_result['min_date']):
                            self.start_date = pd.to_datetime(min_result['min_date'])
                        if self.end_date > pd.to_datetime(max_result['max_date']):
                            self.end_date = pd.to_datetime(max_result['max_date'])
                        dates_list = self.day_list(start_date=self.start_date, end_date=self.end_date)
                        # dates_list 是日期列表
                        for date in dates_list:
                            self.delete_duplicate(table_name=table_name, date=date, except_key=except_key)
                        self.start_date = start_date_before  # 重置，不然日期错乱
                        self.end_date = end_date_before
                    else:  # 不存在日期列的情况
                        self.delete_duplicate2(table_name=table_name, except_key=except_key)
                self.connection.close()
        logger.info(f'mysql({self.host}: {self.port}) {self.db_name} 数据库优化完成!')

    def delete_duplicate(self, table_name, date, except_key=['更新时间']):
        datas = self.table_datas(db_name=self.db_name, table_name=str(table_name), date=date)
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            for e_key in except_key:
                if e_key in data.keys():  # 在检查重复数据时，不包含 更新时间 字段
                    del data[e_key]
            try:
                delete_id = data['id']
                del data['id']
                data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
                if data in all_datas:  # 数据出现重复时
                    if delete_id:
                        duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                        continue
                all_datas.append(data)  # 数据没有重复
            except Exception as e:
                logger.debug(f'{table_name} 函数: mysql - > OptimizeDatas -> delete_duplicate -> {e}')
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM `{table_name}` WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                logger.debug(f"{table_name} -> {date.strftime('%Y-%m-%d')} before: {len(datas)}, remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            logger.error(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def delete_duplicate2(self, table_name, except_key=['更新时间']):
        with self.connection.cursor() as cursor:
            sql = f"SELECT * FROM `{table_name}`"  # 如果不包含日期列，则获取全部数据
            cursor.execute(sql)
            datas = cursor.fetchall()
        if not datas:
            return
        duplicate_id = []  # 出现重复的 id
        all_datas = []  # 迭代器
        for data in datas:
            for e_key in except_key:
                if e_key in data.keys():  # 在检查重复数据时，不包含 更新时间 字段
                    del data[e_key]
            delete_id = data['id']
            del data['id']
            data = re.sub(r'\.0+\', ', '\', ', str(data))  # 统一移除小数点后面的 0
            if data in all_datas:  # 数据出现重复时
                duplicate_id.append(delete_id)  # 添加 id 到 duplicate_id
                continue
            all_datas.append(data)  # 数据没有重复
        del all_datas

        if not duplicate_id:  # 如果没有重复数据，则跳过该数据表
            return

        try:
            with self.connection.cursor() as cursor:
                placeholders = ', '.join(['%s'] * len(duplicate_id))
                # 移除冗余数据
                sql = f"DELETE FROM `{table_name}` WHERE id IN ({placeholders})"
                cursor.execute(sql, duplicate_id)
                logger.info(f"{table_name} -> before: {len(datas)}, "
                      f"remove: {cursor.rowcount}")
            self.connection.commit()  # 提交事务
        except Exception as e:
            logger.error(f'{self.db_name}/{table_name}, {e}')
            self.connection.rollback()  # 异常则回滚

    def database_list(self):
        """ 获取所有数据库 """
        connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW DATABASES")
            databases = cursor.fetchall()  # 获取所有数据库的结果
        connection.close()
        return databases

    def table_list(self, db_name):
        """ 获取指定数据库的所有数据表 """
        connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
        if not connection:
            return
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SHOW DATABASES LIKE '{db_name}'")  # 检查数据库是否存在
                database_exists = cursor.fetchone()
                if not database_exists:
                    logger.info(f'{db_name}: 数据表不存在!')
                    return
        except Exception as e:
            logger.error(f'002 {e}')
            return
        finally:
            connection.close()  # 断开连接

        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        with connection.cursor() as cursor:
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()  # 获取所有数据表
        connection.close()
        return tables

    def table_datas(self, db_name, table_name, date):
        """
        获取指定数据表的数据, 按天获取
        """
        self.config.update({'database': db_name})  # 添加更新 config 字段
        connection = self.keep_connect(_db_name=db_name, _config=self.config, max_try=10)
        if not connection:
            return
        try:
            with connection.cursor() as cursor:
                sql = f"SELECT * FROM `{table_name}` WHERE {'日期'} BETWEEN '%s' AND '%s'" % (date, date)
                cursor.execute(sql)
                results = cursor.fetchall()
        except Exception as e:
            logger.error(f'001 {e}')
        finally:
            connection.close()
        return results

    def day_list(self, start_date, end_date):
        start_date = pd.to_datetime(start_date)
        end_date = pd.to_datetime(end_date)
        date_list = []
        while start_date <= end_date:
            date_list.append(pd.to_datetime(start_date.date()))
            start_date += datetime.timedelta(days=1)
        return date_list

    def rename_column(self):
        """ 批量修改数据库的列名 """
        """
        # for db_name in ['京东数据2', '推广数据2', '市场数据2', '生意参谋2', '生意经2', '属性设置2',]:
        #     s = OptimizeDatas(username=username, password=password, host=host, port=port)
        #     s.db_name = db_name
        #     s.rename_column()
        """
        tables = self.table_list(db_name=self.db_name)
        for table_dict in tables:
            for key, table_name in table_dict.items():
                self.config.update({'database': self.db_name})  # 添加更新 config 字段
                self.connection = self.keep_connect(_db_name=self.db_name, _config=self.config, max_try=10)
                if not self.connection:
                    return
                with self.connection.cursor() as cursor:
                    cursor.execute(f"SHOW FULL COLUMNS FROM `{table_name}`")  # 查询数据表的列信息
                    columns = cursor.fetchall()
                    columns = [{column['Field']: column['Type']} for column in columns]
                    for column in columns:
                        for key, value in column.items():
                            if key.endswith('_'):
                                new_name = re.sub(r'_+$', '', key)
                                sql = f"ALTER TABLE `{table_name}` CHANGE COLUMN {key} {new_name} {value}"
                                cursor.execute(sql)
                self.connection.commit()
        if self.connection:
            self.connection.close()


if __name__ == '__main__':
    pass

    # 初始化上传器
    uploader = MySQLUploader(
        username='root',
        password='1',
        host='localhost',
        port=3306,
        enable_logging=True,
        log_level='INFO'
    )

    # 定义列和数据类型
    columns = {
        'id': 'INT',
        'name': 'VARCHAR(255)',
        'age': 'INT',
        'salary': 'DECIMAL(10,2)',
        '日期': 'DATE'
    }

    # 准备数据
    data = [
        {'name': 'Alice', 'age': 30, 'salary': 50000.50, '日期': '2023-01-15'},
        {'name': 'Bob', 'age': 25, 'salary': 45000.75, '日期': '2023-02-20'},
        {'name': 'Charlie', 'age': 35, 'salary': 60000.00, '日期': '2023-01-10'}
    ]

    # 上传数据
    uploader.upload_data(
        db_name='test_db',
        table_name='employees',
        data=data,
        columns=columns,
        primary_keys=[],
        check_duplicate=True,
        replace=True,
        duplicate_columns=['name'],
        allow_null=False,
        partition_by='month'  # 按月分表
    )

    # 关闭上传器
    uploader.close()
