from flask import Blueprint, request, jsonify
from flask.views import MethodView
from sqlalchemy_searchable import search

from better_bencode import _pure as bencode

from .models import db, Release


bp = Blueprint("api_v1", __name__)


class ReleasesView(MethodView):
    def get(self):
        query = Release.query

        if "q" in request.args:
            query = search(query, request.args["q"])
        else:
            # latest additions
            pass

        return jsonify([{
            "id": str(r.id),
            "title": r.title,
            "artist": r.artist,
            "tracks": [t["title"] for t in r.tracks.values()],
            "stats": r.stats,
        } for r in query.limit(10).all()])  # TODO: paginate

    def post(self):
        r = Release.from_torrent(request.files["torrent"].read())
        db.session.add(r)
        db.session.commit()
        return jsonify({
            "id": str(r.id),
            "title": r.title,
            "artist": r.artist,
            "tracks": [t["title"] for t in r.tracks.values()],
            "stats": r.stats,
        }), 201

bp.add_url_rule('/releases',
                view_func=ReleasesView.as_view("releases"))


class ReleaseView(MethodView):
    def get(self, id):
        r = Release.query.get_or_404(id)

        return jsonify({
            "id": str(r.id),
            "title": r.title,
            "artist": r.artist,
            "tracks": [t["title"] for t in r.tracks.values()],
            "stats": r.stats,
        })

    def patch(self, id):
        r = Release.query.get_or_404(id)

        if "title" in request.json:
            r.title = request.json["title"]
        if "artist" in request.json:
            r.title = request.json["artist"]
        if "tracks" in request.json:
            r.title = request.json["tracks"]

        return jsonify({
            "id": str(r.id),
            "title": r.title,
            "artist": r.artist,
            "tracks": [t["title"] for t in r.tracks.values()],
            "stats": r.stats,
        })

bp.add_url_rule('/releases/<id>',
                view_func=ReleaseView.as_view("release"))


class TorrentView(MethodView):
    def get(self, id):
        r = Release.query.get_or_404(id)
        t = r.to_torrent()
        filename = str(r.id) + ".torrent"
        return bencode.dumps(t), 200, {
            "Content-Type": "application/x-bittorrent",
            "Content-Disposition": "attachment; filename=%s" % filename
        }

bp.add_url_rule('/releases/<id>/torrent',
                view_func=TorrentView.as_view("torrent"))
