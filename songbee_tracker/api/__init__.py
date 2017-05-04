from flask import Blueprint

from .albums import AlbumsView, AlbumView
from .torrents import TorrentsView, TorrentView


bp = Blueprint("api_v1", __name__)


bp.add_url_rule("/albums", view_func=AlbumsView.as_view("albums"))
bp.add_url_rule("/albums/<id>", view_func=AlbumView.as_view("album"))
bp.add_url_rule("/torrents", view_func=TorrentsView.as_view("torrents"))
bp.add_url_rule("/torrents/<id>", view_func=TorrentView.as_view("torrent"))
