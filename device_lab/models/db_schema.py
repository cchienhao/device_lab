from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm.session import sessionmaker

from config import DB_URL

Base = declarative_base()


class SeleniumGridHub(Base):
    __tablename__ = 'selenium_grid_hub'
    id = Column(Integer, primary_key=True)
    url = Column(String(250), nullable=False)


engine = create_engine(DB_URL)

Session = sessionmaker()
Session.configure(bind=engine)


def create_engine():
    Base.metadata.create_all(engine)


if __name__ == '__main__':
    create_engine()
