from marshmallow import Schema, fields


class CreateFinanceSchema(Schema):
    symbol = fields.String(required=True)


class UpdateFinanceSchema(Schema):
    is_tracking = fields.Boolean()
    last_closing_price = fields.Float()
    daily_change_value = fields.Float()
    daily_change_percentage = fields.Float()
