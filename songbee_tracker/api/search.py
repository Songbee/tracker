from flask import request
from sqlalchemy_searchable import search

from ..models import Album, Artist
from ..serializers import AlbumSerializer, ArtistSerializer
from ..util import APIMethodView


class SearchView(APIMethodView):
    def get(self):
        if "q" not in request.args:
            return {
                "error": "'q' is required"
            }, 400

        albums = search(Album.query, request.args["q"])
        artists = search(Artist.query, request.args["q"])

        return {
            "albums": [
                AlbumSerializer.dump(album)
                for album in albums.limit(10).all()  # TODO: paginate
            ],
            "artists": [
                ArtistSerializer.dump(album)
                for album in artists.limit(10).all()  # TODO: paginate
            ],
        }
