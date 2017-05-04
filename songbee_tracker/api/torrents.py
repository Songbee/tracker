from flask import request, url_for
from sqlalchemy.exc import IntegrityError
from better_bencode import _pure as bencode

from ..models import db, Torrent
from ..util import APIMethodView


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
