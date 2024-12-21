from flask import Blueprint
from app.api.items.item_controller import item_bp

# Create the blueprint
api_bp = Blueprint("api", __name__)
api_bp.register_blueprint(item_bp, url_prefix="/items")


# Define routes for the blueprint
@api_bp.route("/healthz")
def healthz():
    return "OK"
