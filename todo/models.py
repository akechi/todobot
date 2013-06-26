#!/usr/bin/python
# -*- coding: utf-8 -*-


from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from sqlalchemy import Column, Integer, String, DateTime, Boolean


get_session = None
"""
    User of this module MUST supply this.

    Most cases, it should be scoped session.
    http://docs.sqlalchemy.org/en/rel_0_8/orm/session.html#thread-local-scope
"""


class ToDo(Base):
    __tablename__ = 'TODO'
    id = Column(Integer, primary_key=True)
    username = Column(String(30))
    description = Column(String)
    created_at = Column(DateTime) # why failed to map "datetime('now', 'localtime')" of sqlite
    status = Column(Boolean)

    def prnformat(self):
        s = []
        if self.status:
            s.append('[X]')
        else:
            s.append('[_]')
        s.append("%04d" % self.id)
        s.append(self.username)
        s.append(str(self.created_at))
        s.append(self.description)
        return ' '.join(s)

    @classmethod
    def add(cls, **kw):
        session = get_session()
        obj = cls(**kw)
        session.add(obj)
        session.commit()
        toget = obj.id
        return session.query(ToDo).get(toget)

    @classmethod
    def get(self, which):
        session = get_session()
        return session.query(ToDo).get(which)
    
    def done(self):
        session = get_session()
        self.status = True
        session.add(self)
        session.commit()

    def delete(self):
        session = get_session()
        session.delete(self)
        session.commit()

    @classmethod
    def list_whose(cls, whose, status=None):
        session = get_session()
        if status is None:
            return session.query(ToDo).filter(ToDo.username == whose)
        else:
            return session.query(ToDo).\
                    filter(ToDo.username == whose).\
                    filter(ToDo.status == status)

    @classmethod
    def list_all(cls):
        session = get_session()
        return session.query(ToDo)





if __name__ == '__main__':
    from sqlalchemy import create_engine
    from sqlalchemy.pool import QueuePool
    from sqlalchemy.orm import sessionmaker

    engine = create_engine('sqlite:///./todo.sqlite', poolclass=QueuePool)

    Session = sessionmaker(bind=engine)
    s = Session()
    try:
        for td in s.query(ToDo).filter(ToDo.status == False).filter(ToDo.username == 'raa0121').order_by(ToDo.id):
            print(td.status, td.username, td.created_at, td.description)
    finally:
        s.close()

