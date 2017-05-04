from flask import Blueprint, request, url_for
from sqlalchemy.exc import IntegrityError
from sqlalchemy_searchable import search

from better_bencode import _pure as bencode

from .models import db, Album, Torrent
from .serializers import AlbumSerializer
from .util import APIMethodView


bp = Blueprint("api_v1", __name__)


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

bp.add_url_rule("/albums", view_func=AlbumsView.as_view("albums"))


class AlbumView(APIMethodView):
    def get(self, id):
        album = Album.query.get_or_404(id)
        return AlbumSerializer.dump(r)

    def patch(self, id):
        album = Album.query.get_or_404(id)
        AlbumSerializer.update(album, request.json)
        album.update_search_vector()
        db.session.add(album)
        db.session.commit()
        return AlbumSerializer.dump(album)

bp.add_url_rule("/albums/<id>", view_func=AlbumView.as_view("album"))


class TorrentsView(APIMethodView):
    def get(self):
        return [{
            "id": t.id,
            "url": url_for(".torrent", id=t.id),
        } for t in Torrent.query.limit(10).all()]

    def post(self):
        t = Torrent.from_file(request.files["torrent"].read())
        try:
            db.session.add(t)
            db.session.commit()
        except IntegrityError:
            return {
                "error": "Torrent already exists",
                "id": t.id,
                "url": url_for(".torrent", id=t.id),
            }, 303
        return {
            "id": t.id,
            "url": url_for(".torrent", id=t.id),
        }, 201

bp.add_url_rule("/torrents", view_func=TorrentsView.as_view("torrents"))


class TorrentView(APIMethodView):
    def get(self, id):
        if len(id) < 40:
            try:
                id = b32_to_b16(id)
            except:
                pass  # TODO: 404

        r = Torrent.query.get_or_404(id)
        t = r.to_file()
        filename = str(r.id) + ".torrent"
        return bencode.dumps(t), 200, {
            "Content-Type": "application/x-bittorrent",
            "Content-Disposition": "attachment; filename=%s" % filename
        }

bp.add_url_rule("/torrents/<id>", view_func=TorrentView.as_view("torrent"))
