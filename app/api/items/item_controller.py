from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.utils.api_exceptions import APIError
from app.api.items.item_schema import CreateItemSchema, UpdateItemSchema
from app.api.items.item_service import ItemService


item_bp = Blueprint("item", __name__)
item_service = ItemService()

create_item_schema = CreateItemSchema()
update_item_schema = UpdateItemSchema()


@item_bp.get("/")
def get_items():
    # SERVICE
    items = item_service.get_all_items()
    # RESPONSE
    return jsonify(items)


@item_bp.get("/<int:item_id>")
def get_item_by_id(item_id):
    # VALIDATION
    if not isinstance(item_id, int):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {item_id}", 400
        )
    # SERVICE
    item = item_service.get_item_by_id(item_id)
    # RESPONSE
    return jsonify(item)


@item_bp.post("/")
def create_item():
    # VALIDATION
    if not request.is_json:
        raise APIError("Malformed request", "Request body is not JSON", 400)

    body = request.get_json(silent=True)
    if body is None:
        raise APIError("Malformed request", "Request body is empty", 400)

    try:
        body = create_item_schema.load(body)
        # SERVICE
        item = item_service.create_item(body["name"])
        # RESPONSE
        return jsonify(item), 201
        # EXCEPTIONS
    except ValidationError as e:
        raise APIError(
            "Malformed request", f"Validation error: {e.messages}", 400
        ) from e


@item_bp.put("/<int:item_id>")
def update_item(item_id):
    # VALIDATION
    if not isinstance(item_id, int):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {item_id}", 400
        )
    if not request.is_json:
        raise APIError("Malformed request", "Request body is not JSON", 400)

    body = request.get_json(silent=True)
    if body is None:
        raise APIError("Malformed request", "Request body is empty", 400)

    try:
        body = update_item_schema.load(request.get_json())
        # SERVICE
        item = item_service.update_item(item_id, body["name"])
        # RESPONSE
        return jsonify(item)
        # EXCEPTIONS
    except ValidationError as e:
        raise APIError(
            "Malformed request", f"Validation error: {e.messages}", 400
        ) from e


@item_bp.delete("/<int:item_id>")
def delete_item(item_id):
    # VALIDATION
    if not isinstance(item_id, int):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {item_id}", 400
        )
    # SERVICE
    item = item_service.delete_item(item_id)
    # RESPONSE
    return jsonify(item), 204
