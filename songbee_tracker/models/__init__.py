from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_searchable import make_searchable, SearchQueryMixin  # noqa

db = SQLAlchemy()
# make_searchable()  # XXX: works OK without it, investigate


class SearchQuery(BaseQuery, SearchQueryMixin):
    pass


from .torrent import Torrent  # noqa
from .artist import Artist  # noqa
from .album import Album  # noqa
