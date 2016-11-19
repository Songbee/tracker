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

from . import config

db = SQLAlchemy()
# make_searchable()


class ReleaseQuery(BaseQuery, SearchQueryMixin):
    pass


class Release(db.Model):
    """
    An album or a single or something. Also, a torrent.
    """

    __tablename__ = "releases"
    query_class = ReleaseQuery

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid1)
    meta = db.Column(JSONType, default=dict)
    info = db.Column(db.PickleType, default=dict)
    search_vector = db.Column(TSVectorType())


    def to_torrent(self):
        """
        Return a dict which, when bencoded, can be used as a .torrent file.
        """

        announce = config.TRACKERS
        return {
            "announce": announce[0],
            "announce-list": [[ann] for ann in announce],
            "comment": config.TORRENT_COMMENT,
            "created by": "Songbee Tracker/0.0.0",
            # "creation date": <unix timestamp>,
            "encoding": "UTF-8",
            "info": self.info,
            "publisher": config.TORRENT_PUBLISHER,
            "publisher-url": config.TORRENT_PUBLISHER_URL,
            "x-songbee": {
                "id": str(self.id),
                "meta": json.dumps(self.meta),
            }
        }

    @classmethod
    def from_torrent(cls, torrent, **kwargs):
        """
        Make a Release object from torrent (optionally bencoded).
        """

        release = cls(**kwargs)
        if not isinstance(torrent, dict):
            torrent = bencode.loads(torrent)

        if "info" in torrent:
            release.info = torrent["info"]
        elif b"info" in torrent:
            release.info = torrent[b"info"]
        else:
            raise ValueError("torrent has no 'info' field")

        return release

    @property
    def infohash(self):
        return hashlib.sha1(bencode.dumps(self.info))

    @property
    def stats(self):
        """
        A dictionary with keys:
        - complete (int): number of peers with the entire file, i.e. seeders
        - downloaded (int): total number of times the tracker has registered
            a completion ("event=complete", i.e. a client finished
            downloading the torrent)
        - incomplete (int): number of non-seeder peers, aka "leechers"

        We get this from the scrape server defined in SCRAPE_URL.
        """

        info_hash = self.infohash.digest()
        file = defaultdict(lambda: None)
        try:
            r = requests.get(config.SCRAPE_URL, params={"info_hash": info_hash},
                             timeout=2)
            b = bencode.loads(r.content)
            file = b[b"files"].get(info_hash, file)
        except:
            pass

        return {
            "complete": file[b"complete"],
            "downloaded": file[b"downloaded"],
            "incomplete": file[b"incomplete"],
        }

    def update_search_vector(self):
        text = " ".join(list(filter(lambda x: x is not None, [
                self.meta.get("title", "memes"),
                self.meta.get("artist"),
            ])) + [
                track.get("title", "") + " " + " ".join(track.get("artists", []))
                for track in self.meta.get("tracks", [])
            ])
        self.search_vector = db.func.to_tsvector(text)

    def __repr__(self):
        return "<Release %s by %s>" % (
            self.meta.get("title", "(none)"),
            self.meta.get("artist", "(none)"))
