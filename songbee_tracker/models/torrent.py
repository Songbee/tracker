import hashlib
from collections import defaultdict

from flask import current_app as app
from better_bencode import _pure as bencode

import requests

from . import db


class Torrent(db.Model):
    __tablename__ = "torrents"

    id = db.Column(db.String(40), primary_key=True)
    info = db.Column(db.PickleType, default=dict)

    albums = db.relationship("Album", back_populates="torrent")

    def to_file(self):
        """
        Return a dict which, when bencoded, can be used as a .torrent file.
        """

        announce = app.config["TRACKERS"]
        return {
            "announce": announce[0],
            "announce-list": [[ann] for ann in announce],
            "comment": app.config["TORRENT_COMMENT"],
            "created by": "Songbee Tracker/0.0.0",
            # "creation date": <unix timestamp>,
            "encoding": "UTF-8",
            "info": self.info,
            "publisher": app.config["TORRENT_PUBLISHER"],
            "publisher-url": app.config["TORRENT_PUBLISHER_URL"],
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
            r = requests.get(app.config["SCRAPE_URL"],
                             params={"info_hash": info_hash},
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
