from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine

from config import DB_URL

Base = declarative_base()


class SeleniumGrid(Base):
    __tablename__ = 'selenium_grid'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)


engine = create_engine(DB_URL)


if __name__ == '__main__':
    Base.metadata.create_all(engine)
