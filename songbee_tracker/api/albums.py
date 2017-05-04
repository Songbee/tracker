from flask import request
from sqlalchemy_searchable import search

from ..models import db, Album
from ..serializers import AlbumSerializer
from ..util import APIMethodView


class AlbumsView(APIMethodView):
    def get(self):
        query = Album.query

        if "q" in request.args:
            query = search(query, request.args["q"])
        else:
            # latest additions
            pass

        return [
            AlbumSerializer.dump(album)
            for album in query.limit(10).all()  # TODO: paginate
        ]

    def post(self):
        album = AlbumSerializer.load(request.data)
        db.session.add(album)
        db.session.commit()
        return AlbumSerializer.dump(album), 201


class AlbumView(APIMethodView):
    def get(self, id):
        album = Album.query.get_or_404(id)
        return AlbumSerializer.dump(album)

    def patch(self, id):
        album = Album.query.get_or_404(id)
        AlbumSerializer.update(album, request.json)
        album.update_search_vector()
        db.session.add(album)
        db.session.commit()
        return AlbumSerializer.dump(album)
