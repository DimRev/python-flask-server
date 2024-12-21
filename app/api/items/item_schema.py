from marshmallow import Schema, fields


# Schema for POST / create item
class CreateItemSchema(Schema):
    name = fields.String(required=True)


# Schema for PUT / update item
class UpdateItemSchema(Schema):
    name = fields.String(required=True)
