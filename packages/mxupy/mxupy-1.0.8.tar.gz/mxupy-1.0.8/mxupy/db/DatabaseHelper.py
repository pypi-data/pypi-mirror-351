import importlib

from peewee import ModelBase
from playhouse.shortcuts import ReconnectMixin
from playhouse.pool import PooledMySQLDatabase

class ReconnectPooledMySQLDatabase(ReconnectMixin, PooledMySQLDatabase):
    """ 提供 MySql 数据库重连支持

    Args:
        ReconnectMixin (ReconnectMixin): 
            这是一个 mixin 类，用于提供自动重连功能。当数据库连接失败时，ReconnectMixin会尝试重新建立连接。
            这对于处理网络波动或数据库服务重启导致的连接中断非常有用。
            通过继承 ReconnectMixin，ReconnectPooledMySQLDatabase 类将获得自动重连的能力。

        PooledMySQLDatabase (_type_): 
            这是peewee库中的一个类，用于创建一个连接池，管理对MySQL数据库的连接。
            使用连接池可以提高数据库操作的性能，因为它允许复用现有的数据库连接，而不是每次操作都创建新的连接。
            PooledMySQLDatabase接受数据库连接参数（如主机名、用户名、密码等），并管理一个连接池，使得应用程序可以高效地执行数据库查询。

    """
    pass
    
class DatabaseHelper:
    """ 数据库
    """
    
    def __init__(self, name, username, password, host='127.0.0.1', port=3306, charset= 'utf8',
                max_connections=100000, stale_timeout=60, timeout=60):
        """ 连接数据库
        Args:
            
            
            name (str): 库名
            username (str): 用户名
            password (str): 密码
            host (str, optional): 地址
            port (int, optional): 端口
            charset (str, optional): 编码
            max_connections (int, optional): 最大连接数
            stale_timeout (int, optional): 空闲时长（秒）
                这个参数定义了连接池中连接的最大空闲时间。
                如果一个连接在连接池中空闲超过这个时间，它将被认为是“陈旧的”（stale），并且会被自动关闭和从连接池中移除。
                stale_timeout有助于防止使用过时的连接，这些连接可能因为长时间空闲而变得不稳定或不再有效。
                如果stale_timeout设置为None，则连接不会自动因为空闲时间过长而被关闭。
            timeout (int, optional): 超时时长（秒）
                这个参数定义了从连接池请求一个连接时的超时时间。
                如果连接池中没有可用的连接，并且达到了最大连接数限制，那么请求者会等待直到超时。
                如果timeout设置为0，则表示请求者会无限期等待，直到连接池中有可用的连接。
                如果timeout设置为一个正数，那么在指定的时间内如果没有可用连接，请求者会收到一个超时异常。
            
            # 没有找到下列参数
            reconnect_timeout (int, optional): 重连超时时间（秒）
            max_retries (int, optional): 最大重连次数
            initial_delay (int, optional): 初始延迟时间（秒）
            max_delay (int, optional): 最大延迟时间（秒）
            backoff (int, optional): 重连尝试之间的等待时间翻倍
        """
        
        # self.model_path = model_path
        self._db = ReconnectPooledMySQLDatabase(
            database=name,
            user=username,
            password=password,
            host=host,
            port=port,
            charset=charset,
            max_connections=max_connections,
            stale_timeout=stale_timeout,
            timeout=timeout
        )
    
    @property
    def db(self):
        """ 数据库实例

        Returns:
            ReconnectPooledMySQLDatabase: 拥有重连功能的数据库实例
        """
        return self._db
    
    def connect(self, reuse_if_open=False):
        """ 连接数据库

        Args:
            reuse_if_open (bool, optional): 
                True：当尝试建立新的数据库连接时，如果池中已经有一个打开的连接，那么这个打开的连接会被重用，而不是创建一个新的连接。
                False：即使池中已经有打开的连接，也会尝试创建一个新的连接。

        """
        if self._db:
            self._db.connect(reuse_if_open)
        
    def close(self):
        """ 关闭数据库连接

        """
        if self._db:
            self._db.close()
        
    # def table_models(self):
    #     """ 获取所有表与模型集，表名为 key，模型为 value

    #     Returns:
    #         dict[table:Model]: 表与模型集
    #     """
    #     mds = {}
        
    #     mps = self.model_path if isinstance(self.model_path, list) else [self.model_path]
        
    #     for mp in mps:
            
    #         package = importlib.import_module(mp)
    #         # 获取模块中的所有属性
    #         attrs = dir(package)
    #         for attr in attrs:
                
    #             clazz = getattr(package, attr)
    #             if not isinstance(clazz, ModelBase) :
    #                 continue
                
    #             cn = clazz.__name__
    #             if cn == 'EntityX' or cn == 'TreeEntityX':
    #                 continue
                
    #             mds[cn] = clazz
                
    #     return mds
    
    # def models(self, tables=['*']):
    #     """ 根据表名获取模型

    #     Args:
    #         tables (str|list[str]): 表名集
            
    #     Returns:
    #         list[Model]: 模型集
    #     """
    #     if tables == '*' or tables == ['*']:
    #         return list(self.table_models().values())

    #     if not isinstance(tables, list):
    #         tables = [tables]

    #     tms = self.table_models()
    #     return [tms.get(t) for t in tables if t in tms]
        
    # def table_names(self):
    #     """ 获取所有的表名

    #     Returns:
    #         list[str]: 表名集
    #     """
    #     return list(self.table_models().keys())

    # def create_tables(self, tables=['*'], safe=True):
    #     """ 按表名创建表

    #     Args:
    #         db (ReconnectPooledMySQLDatabase): 库
    #         tables (list, optional): _description_. Defaults to ['*'].
    #         safe (bool, optional): _description_. Defaults to True.
    #     """
    #     # db.connect()
    #     ms = self.models(tables)
    #     if ms:
    #         self.db.create_tables(ms, safe=safe)
    #     # db.close()
        
    # def drop_tables(self, tables=['*'], safe=False):
    #     # db.connect()
    #     ms = self.models(tables)
    #     if ms:
    #         self.db.drop_tables(ms, safe=safe)
    #     # db.close()