"""数据库连接（可选）：用于测试前数据清理或断言数据一致性。

默认关闭（config.yaml 中 database.enabled=false）。
如需启用，请安装 pymysql：pip install pymysql
"""
import pymysql
from common.config import config
from common.logger import logger


class Database:
    def __init__(self):
        self.conn = None

    def connect(self):
        if not config.database.get("enabled", False):
            logger.debug("数据库未启用，跳过连接")
            return None
        try:
            self.conn = pymysql.connect(
                host=config.database["host"],
                port=config.database["port"],
                user=config.database["username"],
                password=config.database["password"],
                database=config.database["database"],
                charset="utf8mb4",
                cursorclass=pymysql.cursors.DictCursor,
            )
            logger.info("数据库连接成功")
            return self.conn
        except Exception as e:
            logger.error(f"数据库连接失败：{e}")
            raise

    def execute(self, sql, params=None):
        if not self.conn:
            self.connect()
        with self.conn.cursor() as cursor:
            cursor.execute(sql, params)
            self.conn.commit()
            return cursor.fetchall()

    def close(self):
        if self.conn:
            self.conn.close()
            self.conn = None
            logger.info("数据库连接已关闭")


db = Database()
