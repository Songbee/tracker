from pathlib import Path

import jsonschema
from ruamel import yaml
from beerializer import fields, Serializer, ValidationError

from .models import Album

METAINFO_SCHEMA = yaml.load(
    (Path(__file__).parent / "metainfo_schema.yml").open())


class JSONSchemaValidator:
    def __init__(self, schema):
        self.schema = schema

    def validate(self, field, data):
        try:
            jsonschema.validate(data, self.schema)
        except jsonschema.ValidationError as je:
            raise ValidationError(je.message) from je


class LambdaField(fields.Field):
    readonly = True

    def __init__(self, object_to_data=None, clean=None, **kwargs):
        super().__init__(**kwargs)
        if object_to_data is not None:
            self._object_to_data = object_to_data
        else:
            self.hidden = True

        if clean is not None:
            self._clean = clean
        else:
            self.readonly = True

    def clean(self, data):
        return self._clean(data)

    def object_to_data(self, obj):
        return self._object_to_data(obj)


class AlbumSerializer(Serializer):
    class Meta:
        model = Album

    id = fields.UuidField(readonly=True)
    title = fields.StringField()
    artist = fields.StringField()
    tracks = fields.DictField(validators=[JSONSchemaValidator(METAINFO_SCHEMA)])
