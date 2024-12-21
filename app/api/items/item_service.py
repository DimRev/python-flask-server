from sqlalchemy.exc import SQLAlchemyError
from app.utils.api_consts import APIError
from app.api.items.item_model import Item
from db.db import Database


class ItemService:
    def __init__(self):
        self.db = Database()

    def get_all_items(self):
        try:
            with self.db.session_local() as session:
                items = session.query(Item).all()
                return [{"id": item.id, "name": item.name} for item in items]
        except SQLAlchemyError as e:
            raise APIError("Failed to retrieve items", str(e), 500) from e

    def get_item_by_id(self, item_id):
        try:
            with self.db.session_local() as session:
                item = session.query(Item).filter_by(id=item_id).first()
                if not item:
                    raise APIError(
                        "Item not found", f"Item with ID {item_id} not found", 404
                    )
                return {"id": item.id, "name": item.name}
        except SQLAlchemyError as e:
            raise APIError("Failed to retrieve item", str(e), 500) from e

    def create_item(self, name):
        try:
            with self.db.session_local() as session:
                new_item = Item(name=name)
                session.add(new_item)
                session.commit()
                return {"id": new_item.id, "name": new_item.name}
        except SQLAlchemyError as e:
            session.rollback()
            raise APIError("Failed to create item", str(e), 500) from e

    def update_item(self, item_id, name):
        try:
            with self.db.session_local() as session:
                item = session.query(Item).filter_by(id=item_id).first()
                if not item:
                    raise APIError(
                        "Item not found", f"Item with ID {item_id} not found", 404
                    )
                item.name = name
                session.commit()
                return {"id": item.id, "name": item.name}
        except SQLAlchemyError as e:
            session.rollback()
            raise APIError("Failed to update item", str(e), 500) from e

    def delete_item(self, item_id):
        try:
            with self.db.session_local() as session:
                item = session.query(Item).filter_by(id=item_id).first()
                if not item:
                    raise APIError(
                        "Item not found", f"Item with ID {item_id} not found", 404
                    )
                session.delete(item)
                session.commit()
                return {"message": "Item deleted successfully"}
        except SQLAlchemyError as e:
            session.rollback()
            raise APIError("Failed to delete item", str(e), 500) from e
