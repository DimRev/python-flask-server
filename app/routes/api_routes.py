from flask import Blueprint
from app.api.items.item_controller import item_bp
from app.api.finances.finance_controller import finance_bp

# Create the blueprint
api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(item_bp, url_prefix="/items")
api_bp.register_blueprint(finance_bp, url_prefix="/finances")


# Define routes for the blueprint
@api_bp.route("/healthz")
def healthz():
    return "OK"
