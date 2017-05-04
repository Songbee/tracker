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


class Torrent(db.Model):
    __tablename__ = "torrents"

    id = db.Column(db.String(40), primary_key=True)
    info = db.Column(db.PickleType, default=dict)
    
    albums = db.relationship("Album", back_populates="torrent")
    
    def to_file(self):
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
        }

    @classmethod
    def from_file(cls, file, **kwargs):
        """
        Make a Torrent object from .torrent (optionally bencoded).
        """

        torrent = cls(**kwargs)
        if not isinstance(torrent, dict):
            file = bencode.loads(file)

        if "info" in file:
            torrent.info = file["info"]
        elif b"info" in file:
            torrent.info = file[b"info"]
        else:
            raise ValueError("torrent has no 'info' field")
        
        # Set id to infohash in base16
        torrent.id = hashlib.sha1(bencode.dumps(torrent.info)).hexdigest()

        return torrent
    
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



class SearchQuery(BaseQuery, SearchQueryMixin):
    pass


class Album(db.Model):
    __tablename__ = "albums"
    query_class = SearchQuery

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid1)
    title = db.Column(db.String)
    artist = db.Column(db.String)
    tracks = db.Column(JSONType, default=list)
    search_vector = db.Column(TSVectorType())
    
    torrent_id = db.Column(db.String(40), db.ForeignKey("torrents.id"))
    torrent = db.relationship("Torrent", back_populates="albums")

    def update_search_vector(self):
        words = [self.title, self.artist.name, (
            [track.get("title", []), track.get("artists", [])]
            for track in self.tracks
        )]
        text = " ".join(flatten(words))
        self.search_vector = db.func.to_tsvector(text)

    def __repr__(self):
        return "<Album %s by %s>" % (
            self.meta.get("title", "Untitled"),
            self.meta.get("artist", "Unknown Artist"))
