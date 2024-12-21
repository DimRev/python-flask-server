from datetime import datetime

from flask import Blueprint, jsonify, request
from marshmallow import ValidationError

from app.utils.api_exceptions import APIError
from app.api.finances.finance_service import FinanceService
from app.api.finances.finance_schema import CreateFinanceSchema, UpdateFinanceSchema

finance_bp = Blueprint("finance", __name__)
finance_service = FinanceService()

create_finance_schema = CreateFinanceSchema()
update_finance_schema = UpdateFinanceSchema()


@finance_bp.get("/")
def get_finances():
    # SERVICE
    finances = finance_service.get_all_finances_symbols()
    # RESPONSE
    return jsonify(finances)


@finance_bp.get("/<string:symbol>")
def get_finance_by_symbol(symbol):
    # QUERY PARAMS
    with_history = request.args.get("with_history", default="false").lower() == "true"
    from_ts = request.args.get("from_ts")
    to_ts = request.args.get("to_ts")

    # VALIDATION
    if not isinstance(symbol, str):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {symbol}", 400
        )

    if from_ts:
        try:
            from_ts = datetime.fromisoformat(from_ts)
        except ValueError as e:
            raise APIError(
                "Invalid from_ts", "Invalid 'from_ts' timestamp format", 400
            ) from e

    if to_ts:
        try:
            to_ts = datetime.fromisoformat(to_ts)
        except ValueError as e:
            raise APIError(
                "Invalid to_ts", "Invalid 'to_ts' timestamp format", 400
            ) from e
    # SERVICE
    finance = finance_service.get_finance_details_by_symbol(
        symbol, with_history, from_ts, to_ts
    )
    # RESPONSE
    return jsonify(finance)


@finance_bp.post("/")
def create_finance():
    # VALIDATION
    if not request.is_json:
        raise APIError("Malformed request", "Request body is not JSON", 400)

    body = request.get_json(silent=True)
    if body is None:
        raise APIError("Malformed request", "Request body is empty", 400)

    try:
        body = create_finance_schema.load(body)
        # SERVICE
        finance = finance_service.create_finance_by_symbol(body["symbol"])
        # RESPONSE
        return jsonify(finance), 201
    except ValidationError as e:
        raise APIError(
            "Malformed request", f"Validation error: {e.messages}", 400
        ) from e


@finance_bp.put("/<string:symbol>")
def update_finance(symbol):
    # VALIDATION
    if not isinstance(symbol, str):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {symbol}", 400
        )
    if not request.is_json:
        raise APIError("Malformed request", "Request body is not JSON", 400)

    body = request.get_json(silent=True)
    if body is None:
        raise APIError("Malformed request", "Request body is empty", 400)

    try:
        body = update_finance_schema.load(request.get_json())
        # SERVICE
        finance = finance_service.update_finance_by_symbol(symbol, **body)
        # RESPONSE
        return jsonify(finance)
    except ValidationError as e:
        raise APIError(
            "Malformed request", f"Validation error: {e.messages}", 400
        ) from e


@finance_bp.delete("/<string:symbol>")
def delete_finance(symbol):
    # VALIDATION
    if not isinstance(symbol, str):
        raise APIError(
            "Invalid route parameter", f"Invalid route parameter: {symbol}", 400
        )
    # SERVICE
    response = finance_service.delete_finance_by_symbol(symbol)
    # RESPONSE
    return jsonify(response), 204


@finance_bp.post("/crawl")
def execute_finance_crawl():
    # SERVICE
    try:
        finance_crawl_result = finance_service.execute_finance_crawl_by_symbols()
        return jsonify(finance_crawl_result), 200
    except APIError as e:
        return jsonify({"error": str(e)}), 500
