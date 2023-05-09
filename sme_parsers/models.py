from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, Boolean, Float, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import os
from datetime import datetime


engine = create_engine(f"postgresql+psycopg2://admin:admin@{os.getenv('DB_URL')}/{os.getenv('DB_NAME')}", pool_pre_ping=True)
engine.dispose(close=False)


Base = declarative_base()


class Parser(Base):
    __tablename__ = 'parsers'

    id = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    name = Column(String(25), nullable=False, unique=True)
    default_commission = Column(Float(), default=0.0)
    default_bonus = Column(Float(), default=0.0)
    games = Column(String(), default='csgo, dota2, tf2, rust')
    is_market = Column(Boolean(), default=False)
    is_exchanger = Column(Boolean(), default=False)

    items = relationship('Item', back_populates='parser')

    class Meta:
        pass


class Item(Base):
    __tablename__ = 'item'

    pk = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    hash_name = Column(String(), nullable=False)
    parser_name = Column(String(), ForeignKey('parsers.name', onupdate='CASCADE', ondelete='CASCADE'))
    game = Column(String(), nullable=False)
    price = Column(Float(), nullable=False)
    analytic = Column(Float())
    count = Column(Integer(), nullable=False)
    link = Column(String(), nullable=False)
    tradelock = Column(Integer())
    time = Column(DateTime(), default=datetime.now())

    parser = relationship("Parser", back_populates="items")

class User(Base):
    __tablename__ = 'user'

    pk = Column(Integer(), primary_key=True, autoincrement=True, nullable=False)
    tg_id = Column(Integer(), unique=True, nullable=False)
    tg_username = Column(String(), nullable=False)