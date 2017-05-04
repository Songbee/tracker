import hashlib
import json
import uuid
from collections import defaultdict

import requests
import sqlalchemy as sa
from sqlalchemy import func
from flask_sqlalchemy import SQLAlchemy, BaseQuery
from sqlalchemy_utils import UUIDType, JSONType, TSVectorType
from sqlalchemy_searchable import make_searchable, SearchQueryMixin
from better_bencode import _pure as bencode

from .. import config

db = SQLAlchemy()
# make_searchable()  # XXX: works OK without it, investigate


class SearchQuery(BaseQuery, SearchQueryMixin):
    pass


from .torrent import Torrent
from .album import Album
from .artist import Artist
