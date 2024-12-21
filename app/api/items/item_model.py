from sqlalchemy import Column, Integer, String

from db.db import Database

Base = Database().Base


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)

    def __repr__(self):
        return f"<Item(id={self.id}, name={self.name})>"

    def __str__(self):
        return f"<Item(id={self.id}, name={self.name})>"
