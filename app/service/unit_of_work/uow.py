import abc
from sqlalchemy import Engine
from app.database.db import main_engine
from app.database.dao import DbModels


class AbstractUnitOfWork(abc.ABC):
    tables: DbModels

    def __enter__(self) -> "AbstractUnitOfWork":
        return self

    def __exit__(self, *args):
        self.rollback()

    @abc.abstractmethod
    def commit(self):
        raise NotImplementedError

    @abc.abstractmethod
    def rollback(self):
        raise NotImplementedError


class SqlAlchemyUnitOfWork(AbstractUnitOfWork):
    def __init__(
        self,
        engine=main_engine,
    ):
        self.engine: Engine = engine

    def __enter__(self):
        self.conn = self.engine.connect()
        self.tables = DbModels(self.conn)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.conn.close()

    def commit(self):
        """Manual step so user has a control over committing a transaction"""
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()
