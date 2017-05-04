from flask import Blueprint

from .index import IndexView
from .search import SearchView
from .albums import AlbumsView, AlbumView
from .artists import ArtistsView, ArtistView
from .torrents import TorrentsView, TorrentView


bp = Blueprint("api_v1", __name__)


bp.add_url_rule("/", view_func=IndexView.as_view("index"))
bp.add_url_rule("/search", view_func=SearchView.as_view("search"))
bp.add_url_rule("/albums", view_func=AlbumsView.as_view("albums"))
bp.add_url_rule("/albums/<id>", view_func=AlbumView.as_view("album"))
bp.add_url_rule("/artists", view_func=ArtistsView.as_view("artists"))
bp.add_url_rule("/artists/<id>", view_func=ArtistView.as_view("artist"))
bp.add_url_rule("/torrents", view_func=TorrentsView.as_view("torrents"))
bp.add_url_rule("/torrents/<id>", view_func=TorrentView.as_view("torrent"))
