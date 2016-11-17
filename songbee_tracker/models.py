import random
import uuid
import hashlib
from collections import defaultdict

import requests
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy_searchable import make_searchable
from sqlalchemy_utils import ScalarListType, UUIDType, TSVectorType
from better_bencode import _pure as bencode

db = SQLAlchemy()


make_searchable()


PRIMARY_TRACKER = "http://bt.songbee.net/announce"

TRACKERS = [
    "udp://tracker.leechers-paradise.org:6969/announce",
    "udp://IPv6.leechers-paradise.org:6969/announce",
    "udp://zer0day.ch:1337",
    "udp://tracker.pirateparty.gr:6969/announce",
    "udp://tracker.internetwarriors.net:1337/announce",
    "udp://tracker.leechers-paradise.org:6969/announce",
    "udp://tracker.coppersurfer.tk:6969/announce",
    "udp://exodus.desync.com:6969/announce",
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://tracker.sktorrent.net:6969/announce",
    "udp://tracker.zer0day.to:1337/announce",
]

SCRAPE_URL = "http://bt.songbee.net/scrape"


class Release(db.Model):
    """
    An album or a single or something. Also, a torrent.
    """

    __tablename__ = "releases"
    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid1)
    title = db.Column(db.Unicode(255))
    artist = db.Column(db.Unicode(255))
    external_links = db.Column(ScalarListType, doc='["{type}:{urn}", ...]')
    info = db.Column(db.PickleType, default=dict)
    tracks = db.Column(db.PickleType, default=dict,
                       doc='{"{filename}": {"title": "{title}", ...}, ...}')

    _track_names = db.Column(db.UnicodeText, doc="For search vector only")
    search_vector = db.Column(TSVectorType("title", "artist", "_track_names"))

    def to_torrent(self):
        """
        Return a dict which, when bencoded, can be used as a .torrent file.
        """
        announce = [PRIMARY_TRACKER] + random.sample(TRACKERS, 4)
        return {
            "announce": announce[0],
            "announce-list": [[ann] for ann in announce],
            "comment": "https://tracker.songbee.net/",
            "created by": "Songbee Tracker/0.0.0",
            # "creation date": <unix timestamp>,
            "encoding": "UTF-8",
            "info": self.info,
            "publisher": "songbee.net",
            "publisher-url": "https://tracker.songbee.net/",
            "x-songbee": {
                "id": str(self.id),
                "title": self.title or "",
                "artist": self.artist or "",
                "tracks": self.tracks,
                "tracker": "https://tracker.songbee.net/",
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
            r = requests.get(SCRAPE_URL, params={"info_hash": info_hash},
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
