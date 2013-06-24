#!/usr/bin/python
# -*- coding: utf-8 -*-


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, Boolean


class ToDo(Base):
    __tablename__ = 'TODO'
    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    description = Column(String)
    created_at = Column(DateTime) # why failed to map "datetime('now', 'localtime')" of sqlite
    status = Column(Boolean)


if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)

    Session = sessionmaker(bind=engine)
    s = Session()

    for td in s.query(ToDo).filter(ToDo.status == False).filter(ToDo.username == 'raa0121').order_by(ToDo.id):
        print(td.status, td.username, td.created_at, td.description)

