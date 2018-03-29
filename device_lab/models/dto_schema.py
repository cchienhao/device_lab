from marshmallow import Schema, fields

from spec import register_schema


class BaseSchema(Schema):
    @classmethod
    def from_json(cls, json_data, many=None, *args, **kwargs):
        return cls(strict=True).loads(json_data, many=many, *args, **kwargs).data

    @classmethod
    def to_json(cls, obj, many=None, update_fields=True, *args, **kwargs):
        return cls(strict=True).dumps(obj, many=many, update_fields=update_fields, *args, **kwargs).data


class CapabilityLockSchema(BaseSchema):
    appium_url = fields.String(required=True)
    udid = fields.String(required=True)
    timeout = fields.Integer(required=True, validate=lambda i: 0 < i < 7200)
register_schema('CapabilityLock', CapabilityLockSchema)
