from pathlib import Path

from flask import url_for
from ruamel import yaml
from beerializer import fields, Serializer
from beerializer.validators import JSONSchemaValidator

from .models import Album, Artist

TRACKS_SCHEMA = yaml.load(
    (Path(__file__).parent / "metainfo_schema.yml").open())


class URLField(fields.Field):
    readonly = True

    def __init__(self, endpoint, param="id", attr=None, external=True, **kwargs):
        super().__init__(**kwargs)
        self.endpoint = endpoint
        self.external = external
        self.param = param
        self.attr = attr if attr is not None else param

        self.readonly = True

    def object_to_data(self, obj):
        if callable(self.attr):
            value = self.attr(obj)
        else:
            value = getattr(obj, self.attr)

        kw = {self.param: value}
        return url_for(self.endpoint, _external=self.external, **kw)


class AlbumSerializer(Serializer):
    class Meta:
        model = Album

    id = URLField("api_v1.album", name="url", attr=str)
    title = fields.StringField()
    artist = URLField("api_v1.artist", name="artist_url")
    artist_id = fields.UuidField(hidden=True)
    tracks = fields.Field(validators=[JSONSchemaValidator(TRACKS_SCHEMA)])


class AlbumMiniSerializer(Serializer):
    class Meta:
        model = Album

    id = URLField("api_v1.album", name="url", attr=str)
    title = fields.StringField()


class ArtistSerializer(Serializer):
    class Meta:
        model = Artist

    id = fields.UuidField(readonly=True)
    name = fields.StringField()
    description = fields.StringField()
    albums = fields.ListField(fields.ObjectField(AlbumMiniSerializer))
