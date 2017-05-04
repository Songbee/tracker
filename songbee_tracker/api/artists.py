from flask import request
from sqlalchemy_searchable import search

from ..models import db, Artist
from ..serializers import ArtistSerializer
from ..util import APIMethodView


class ArtistsView(APIMethodView):
    def get(self):
        query = Artist.query

        if "q" in request.args:
            query = search(query, request.args["q"])
        else:
            # latest additions
            pass

        return [
            ArtistSerializer.dump(artist)
            for artist in query.limit(10).all()  # TODO: paginate
        ]

    def post(self):
        artist = ArtistSerializer.load(request.data)
        artist.update_search_vector()
        db.session.add(artist)
        db.session.commit()
        return ArtistSerializer.dump(artist), 201


class ArtistView(APIMethodView):
    def get(self, id):
        artist = Artist.query.get_or_404(id)
        return ArtistSerializer.dump(artist)

    def patch(self, id):
        artist = Artist.query.get_or_404(id)
        ArtistSerializer.update(artist, request.data)
        artist.update_search_vector()
        db.session.add(artist)
        db.session.commit()
        return ArtistSerializer.dump(artist)
