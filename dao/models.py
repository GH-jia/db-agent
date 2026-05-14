from sqlalchemy import BigInteger, Boolean, CheckConstraint, Column, DateTime, Float, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB

from dao.database import Base


class ItemModel(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)


class AgentDbConnectionModel(Base):
    __tablename__ = "agent_db_connections"
    __table_args__ = (
        CheckConstraint("db_type IN ('postgresql', 'mysql')", name="chk_agent_db_connections_db_type"),
        CheckConstraint("port > 0 AND port <= 65535", name="chk_agent_db_connections_port"),
        CheckConstraint(
            "ssl_mode IN ('disable', 'allow', 'prefer', 'require', 'verify-ca', 'verify-full')",
            name="chk_agent_db_connections_ssl_mode",
        ),
        CheckConstraint("status IN ('active', 'disabled')", name="chk_agent_db_connections_status"),
    )

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    connection_id = Column(String(64), nullable=False, unique=True, index=True)
    user_id = Column(String(100), nullable=True, index=True)
    name = Column(String(100), nullable=False)
    db_type = Column(String(30), nullable=False, default="postgresql")
    host = Column(String(255), nullable=False)
    port = Column(Integer, nullable=False)
    database_name = Column(String(100), nullable=False)
    username = Column(String(100), nullable=False)
    password_ciphertext = Column(Text, nullable=False)
    ssl_mode = Column(String(20), nullable=False, default="prefer")
    readonly = Column(Boolean, nullable=False, default=True)
    status = Column(String(20), nullable=False, default="active", index=True)
    extra = Column(JSONB, nullable=False, default=dict)
    last_tested_at = Column(DateTime(timezone=True), nullable=True)
    last_test_success = Column(Boolean, nullable=True)
    last_test_message = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
