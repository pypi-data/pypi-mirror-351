from .mongo_singleton import MongoDBSingleton
from .mysql_singleton import MysqlDBSingleton
from .mysql import MysqlDB
db = MysqlDBSingleton
mongo = MongoDBSingleton