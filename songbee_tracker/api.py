from flask import Blueprint, request
from flask.views import MethodView
from sqlalchemy_searchable import search

from better_bencode import _pure as bencode

from .models import db, Album, Torrent
from .serializers import AlbumSerializer


bp = Blueprint("api_v1", __name__)


class AlbumsView(MethodView):
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

bp.add_url_rule("/albums", view_func=AlbumsView.as_view("albums"))


class AlbumView(MethodView):
    def get(self, id):
        album = Album.query.get_or_404(id)
        return AlbumSerializer.dump(r)

    def patch(self, id):
        album = Album.query.get_or_404(id)
        AlbumSerializer.update(r, request.json)
        album.update_search_vector()
        db.session.add(r)
        db.session.commit()
        return AlbumSerializer.dump(r)

bp.add_url_rule("/albums/<id>", view_func=AlbumView.as_view("album"))


class TorrentView(MethodView):
    def get(self, infohash):
        if len(infohash) < 40:
            try:
                infohash = b32_to_b16(infohash)
            except:
                pass  # TODO: 404

        r = Torrent.query.get_or_404(infohash)
        t = r.to_file()
        filename = str(r.id) + ".torrent"
        return bencode.dumps(t), 200, {
            "Content-Type": "application/x-bittorrent",
            "Content-Disposition": "attachment; filename=%s" % filename
        }

bp.add_url_rule("/torrents/<infohash>", view_func=TorrentView.as_view("torrent"))
