from datetime import datetime, timezone, timedelta
from typing import Sequence
from sqlalchemy import Column, String, DateTime
from sqlalchemy.dialects.postgresql import JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql.schema import ForeignKey
from sqlalchemy.sql.sqltypes import BigInteger, Integer, Numeric
from core.src.infra.config import Base


class Package(Base):
    """Packages Entity"""

    __tablename__ = "packages"

    id = Column(String(36), primary_key=True)
    name = Column(String(), nullable=False, unique=False)
    symbol = Column(String(), nullable=True, unique=False)
    created_at = Column(
        DateTime, default=datetime.now(timezone(timedelta(hours=-3))), nullable=False
    )
    updated_at = Column(
        DateTime, default=datetime.now(timezone(timedelta(hours=-3))), nullable=False
    )
    empresa_id = Column(String(36), nullable=False)
    created_by = Column(String(36), nullable=True)
    updated_by = Column(String(36), nullable=True)
    products = relationship("Product", innerjoin=True)

    def __repr__(self):
        return f"Package [name={self.name}]"

    def __eq__(self, other):
        if (
            self.id == other.id
            and self.name == other.name
            and self.symbol == other.symbol
        ):
            return True
        return False
