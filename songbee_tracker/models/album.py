from . import db, SearchQuery


class Album(db.Model):
    __tablename__ = "albums"
    query_class = SearchQuery

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid1)
    title = db.Column(db.String)
    tracks = db.Column(JSONType, default=list)
    search_vector = db.Column(TSVectorType())

    torrent_id = db.Column(db.String(40), db.ForeignKey("torrents.id"))
    torrent = db.relationship("Torrent", back_populates="albums")

    artist_id = db.Column(UUIDType, db.ForeignKey("artists.id"))
    artist = db.relationship("Artist", back_populates="albums")

    def update_search_vector(self):
        words = [self.title, self.artist.name, (
            [track.get("title", []), track.get("artists", [])]
            for track in self.tracks
        )]
        text = " ".join(flatten(words))
        self.search_vector = db.func.to_tsvector(text)

    def __repr__(self):
        return "<Album %s by %s>" % (self.title, self.artist.name)
