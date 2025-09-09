# server/app/models/__init__.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """
    すべてのデータベースモデルが継承する基本クラス。
    """
    pass
