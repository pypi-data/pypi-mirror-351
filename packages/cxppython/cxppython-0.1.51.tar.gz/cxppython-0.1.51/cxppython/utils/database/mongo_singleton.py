from typing import Union, Dict, Any, List
from urllib.parse import quote_plus

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
import cxppython as cc

class MongoDBSingleton:
    __instance = None
    __connection_string = None

    def __new__(cls, *args, **kwargs):
        """实现单例模式"""
        if cls.__instance is None:
            cls.__instance = super(MongoDBSingleton, cls).__new__(cls)
        return cls.__instance

    @staticmethod
    def create(connection: Union[str, Dict[str, Any]]) -> 'MongoDBSingleton':
        """
        静态方法，用于创建 MongoUtil 单例实例
        :param connection: 连接字符串或配置字典
        :return: MongoUtil 实例
        """
        if MongoDBSingleton.__instance is not None:
            return MongoDBSingleton.__instance

        # 处理连接参数
        if isinstance(connection, str):
            client = MongoClient(connection)
            # 从连接字符串中提取数据库名称
            MongoDBSingleton.__connection_string = connection
            db_name = connection.split('/')[-1].split('?')[0]
        elif isinstance(connection, dict):
            client = MongoClient(
                host=connection.get('host'),
                port=connection.get('port'),
                username=connection.get('user'),
                password=connection.get('password')
            )
            username = quote_plus(connection.get('user', '')) if connection.get('user') else None
            password = quote_plus(connection.get('password', '')) if connection.get('password') else None
            host = connection.get('host', 'localhost')
            port = connection.get('port', 27017)
            MongoDBSingleton.__connection_string = f"mongodb://{username}:{password}@{host}:{port}" if username and password else f"mongodb://{host}:{port}"
            db_name = connection.get('database')
            if not db_name:
                raise ValueError("字典连接参数必须包含 'database' 字段")
        else:
            raise ValueError("连接参数必须是字符串或字典")

        # 初始化单例实例
        MongoDBSingleton.__instance = MongoDBSingleton.__new__(MongoDBSingleton)
        MongoDBSingleton.__instance._init_connection(client, db_name)
        return MongoDBSingleton.__instance

    @staticmethod
    def instance():
        return MongoDBSingleton.__instance

    @staticmethod
    def test_connection() -> bool:
        """
        测试 MongoDB 连接是否有效
        :return: 连接成功返回 True，否则返回 False
        """
        try:
            # 执行简单的服务器状态查询以测试连接
            MongoDBSingleton.__instance.client.admin.command('ping')
            cc.logging.success(f"Database connection successful! : {MongoDBSingleton.__instance.print_connection_string()}")
            return True
        except ConnectionFailure:
            print("MongoDB 连接失败：无法连接到服务器")
            return False
        except Exception as e:
            print(f"MongoDB 连接测试失败：{str(e)}")
            return False

    def _init_connection(self, client: MongoClient, db_name: str):
        """
        初始化 MongoDB 连接
        :param client: MongoClient 实例
        :param db_name: 数据库名称
        """
        self.client = client
        self.db = self.client[db_name]

    def print_connection_string(self) -> None|str:
        """
        打印 MongoDB 连接字符串，密码部分替换为 ***
        """
        if not MongoDBSingleton.__connection_string:
            print("未找到连接字符串")
            return None

        # 处理连接字符串，替换密码为 ***
        connection_str = MongoDBSingleton.__connection_string
        if '@' in connection_str and ':' in connection_str.split('@')[0]:
            # 提取用户名和密码部分
            prefix = connection_str.split('://')[0] + '://'
            user_pass = connection_str.split('://')[1].split('@')[0]
            host_part = connection_str.split('@')[1]
            username = user_pass.split(':')[0]
            # 替换密码为 ***
            safe_connection_str = f"{prefix}{username}:***@{host_part}"
            # print(f"MongoDB 连接字符串: {safe_connection_str}")
            return safe_connection_str
        else:
            # 如果没有用户名和密码，直接打印
            # print(f"MongoDB 连接字符串: {connection_str}")
            return connection_str

    def get_collection(self, collection_name: str):
        """
        获取或创建指定集合
        :param collection_name: 集合名称
        :return: MongoDB 集合对象
        """
        return self.db[collection_name]

    def get_client(self):
        """
        获取MongoClient对象
        :return: MongoClient 对象
        """
        return self.client

    def list_collections(self) -> List[str]:
        """
        列出数据库中的所有集合
        :return: 集合名称列表
        """
        return self.db.list_collection_names()

    def create_collection(self, collection_name: str) -> None:
        """
        创建新集合（如果不存在）
        :param collection_name: 集合名称
        """
        if collection_name not in self.db.list_collection_names():
            self.db.create_collection(collection_name)

    def drop_collection(self, collection_name: str) -> None:
        """
        删除指定集合
        :param collection_name: 集合名称
        """
        self.db[collection_name].drop()

    def insert_one(self, collection_name: str, document: Dict[str, Any]) -> str:
        """
        插入单个文档到指定集合
        :param collection_name: 集合名称
        :param document: 要插入的文档
        :return: 插入文档的ID
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_one(document)
        return str(result.inserted_id)

    def insert_many(self, collection_name: str, documents: List[Dict[str, Any]]) -> List[str]:
        """
        插入多个文档到指定集合
        :param collection_name: 集合名称
        :param documents: 要插入的文档列表
        :return: 插入文档的ID列表
        """
        collection = self.get_collection(collection_name)
        result = collection.insert_many(documents)
        return [str(id) for id in result.inserted_ids]

    def find_one(self, collection_name: str, query: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        查询指定集合中的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件，默认为None（返回第一个文档）
        :return: 查找到的文档
        """
        collection = self.get_collection(collection_name)
        return collection.find_one(query)

    def find_many(self, collection_name: str, query: Dict[str, Any] = None, limit: int = 0) -> List[Dict[str, Any]]:
        """
        查询指定集合中的多个文档
        :param collection_name: 集合名称
        :param query: 查询条件，默认为None（返回所有文档）
        :param limit: 返回文档数量限制，0表示无限制
        :return: 查找到的文档列表
        """
        collection = self.get_collection(collection_name)
        cursor = collection.find(query)
        if limit > 0:
            cursor = cursor.limit(limit)
        return list(cursor)

    def update_one(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        更新指定集合中的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件
        :param update: 更新内容
        :return: 受影响的文档数量
        """
        collection = self.get_collection(collection_name)
        result = collection.update_one(query, {"$set": update})
        return result.modified_count

    def update_many(self, collection_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """
        更新指定集合中的多个文档
        :param collection_name: 集合名称
        :param query: 查询条件
        :param update: 更新内容
        :return: 受影响的文档数量
        """
        collection = self.get_collection(collection_name)
        result = collection.update_many(query, {"$set": update})
        return result.modified_count

    def delete_one(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        删除指定集合中的单个文档
        :param collection_name: 集合名称
        :param query: 查询条件
        :return: 删除的文档数量
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_one(query)
        return result.deleted_count

    def delete_many(self, collection_name: str, query: Dict[str, Any]) -> int:
        """
        删除指定集合中的多个文档
        :param collection_name: 集合名称
        :param query: 查询条件
        :return: 删除的文档数量
        """
        collection = self.get_collection(collection_name)
        result = collection.delete_many(query)
        return result.deleted_count

    def close(self):
        """
        关闭MongoDB连接
        """
        if self.client:
            self.client.close()
            MongoDBSingleton.__instance = None
