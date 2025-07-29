from sqlalchemy import create_engine, Table, Column, Integer, String, Float, Boolean, MetaData, inspect
from sqlalchemy.exc import SQLAlchemyError
import pymongo
import urllib.parse
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DBConnector:
    def __init__(self, db_url):
        self.db_url = db_url
        self.is_sql = not db_url.startswith("mongodb://")
        self.connection = None
        
        # Validate db_url
        if self.is_sql and "mysql" in db_url:
            if "+pymysql" not in db_url:
                db_url = db_url.replace("mysql://", "mysql+pymysql://")
                logger.info("Chuyển sang sử dụng pymysql cho MySQL")
            if "@@" in db_url:
                logger.warning("Mật khẩu chứa ký tự '@'. Hãy mã hóa '@' thành '%40'.")
                db_url = db_url.replace("@@", "%40%40")
        
        try:
            if self.is_sql:
                self.engine = create_engine(db_url, echo=False)
                self.metadata = MetaData()
                self.connection = self.engine.connect()
                self.inspector = inspect(self.engine)
                logger.info(f"Kết nối thành công với SQL database: {db_url}")
            else:
                self.mongo_client = pymongo.MongoClient(db_url)
                db_name = urllib.parse.urlparse(db_url).path.lstrip("/")
                self.mongo_db = self.mongo_client[db_name]
                logger.info(f"Kết nối thành công với MongoDB: {db_url}")
        except (SQLAlchemyError, pymongo.errors.PyMongoError) as e:
            logger.error(f"Lỗi khi kết nối tới database: {e}")
            if "mysql" in db_url and "No module named 'MySQLdb'" in str(e):
                logger.error("Thiếu driver MySQL. Hãy cài đặt pymysql: `poetry add pymysql`")
            raise

    def _map_python_type_to_sql(self, key, value):
        """Ánh xạ kiểu Python sang kiểu SQLAlchemy với độ dài phù hợp."""
        if isinstance(value, str):
            if key == "name":
                return String(255)
            elif key == "phone":
                return String(20)
            elif key == "address":
                return String(500)
            else:
                return String(255)
        elif isinstance(value, int):
            return Integer
        elif isinstance(value, float):
            return Float
        elif isinstance(value, bool):
            return Boolean
        else:
            return String(255)

    def _check_column_lengths(self, table_name, data):
        """Kiểm tra độ dài cột trong bảng hiện có so với dữ liệu."""
        if not self.is_sql or not self.inspector.has_table(table_name):
            return True
        
        table_info = self.inspector.get_columns(table_name)
        column_lengths = {col['name']: col['type'].length for col in table_info if hasattr(col['type'], 'length')}
        
        for row in data:
            for key, value in row.items():
                if key in column_lengths and isinstance(value, str):
                    max_length = column_lengths[key]
                    if max_length and len(value) > max_length:
                        logger.error(
                            f"Dữ liệu cho cột '{key}' quá dài: '{value}' (dài {len(value)} ký tự, giới hạn {max_length}). "
                            f"Hãy dùng --drop-table để tạo lại bảng hoặc điều chỉnh schema."
                        )
                        return False
        return True

    def save_to_db(self, table_name, data, drop_table=False):
        """Lưu dữ liệu vào database (SQL hoặc MongoDB)."""
        if not data:
            logger.warning("Không có dữ liệu để lưu!")
            return False

        try:
            if self.is_sql:
                # Kiểm tra độ dài cột trước khi chèn
                if not self._check_column_lengths(table_name, data):
                    return False

                # Kiểm tra bảng đã tồn tại
                table_exists = self.inspector.has_table(table_name)
                if table_exists and drop_table:
                    logger.info(f"Xóa bảng {table_name} trước khi tạo mới")
                    if table_name in self.metadata.tables:
                        self.metadata.tables[table_name].drop(self.engine)
                    else:
                        table = Table(table_name, self.metadata, autoload_with=self.engine)
                        table.drop(self.engine)
                    table_exists = False

                if not table_exists:
                    # Tạo bảng động nếu chưa tồn tại
                    columns = []
                    for key, value in data[0].items():
                        col_type = self._map_python_type_to_sql(key, value)
                        if key == 'id':
                            columns.append(Column(key, col_type, primary_key=True))
                        else:
                            columns.append(Column(key, col_type))
                    
                    table = Table(table_name, self.metadata, *columns)
                    self.metadata.create_all(self.engine)
                    logger.info(f"Tạo bảng mới {table_name}")
                else:
                    # Sử dụng bảng hiện có
                    table = Table(table_name, self.metadata, autoload_with=self.engine)
                    logger.info(f"Sử dụng bảng hiện có {table_name}")

                # Lưu dữ liệu theo batch với transaction
                with self.connection.begin() as transaction:
                    batch_size = 1000
                    for i in range(0, len(data), batch_size):
                        self.connection.execute(table.insert(), data[i:i+batch_size])
                    transaction.commit()
                    logger.info(f"Lưu {len(data)} bản ghi vào bảng {table_name} (SQL)")
                return True
            else:
                # Lưu vào MongoDB collection
                collection = self.mongo_db[table_name]
                if drop_table:
                    logger.info(f"Xóa collection {table_name} trước khi lưu")
                    collection.drop()
                collection.insert_many(data, ordered=False)
                logger.info(f"Lưu {len(data)} bản ghi vào collection {table_name} (MongoDB)")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Lỗi khi lưu vào database: {e}")
            if "Data too long for column" in str(e):
                logger.error(
                    "Dữ liệu quá dài so với giới hạn cột. "
                    "Hãy kiểm tra cấu trúc bảng bằng `DESCRIBE users;` hoặc dùng --drop-table để tạo lại bảng."
                )
            return False
        except pymongo.errors.PyMongoError as e:
            logger.error(f"Lỗi khi lưu vào MongoDB: {e}")
            return False

    def close(self):
        """Đóng kết nối database."""
        if self.is_sql and self.connection:
            self.connection.close()
            self.engine.dispose()
            logger.info("Đóng kết nối SQL database")
        elif not self.is_sql:
            self.mongo_client.close()
            logger.info("Đóng kết nối MongoDB")