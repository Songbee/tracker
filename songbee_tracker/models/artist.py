from . import db, SearchQuery


class Artist(db.Model):
    __tablename__ = "albums"
    query_class = SearchQuery

    id = db.Column(UUIDType, primary_key=True, default=uuid.uuid1)
    name = db.Column(db.String)
    description = db.Column(db.String)
    search_vector = db.Column(TSVectorType())

    def update_search_vector(self):
        words = [self.name, self.description]
        text = " ".join(flatten(words))
        self.search_vector = db.func.to_tsvector(text)

    def __repr__(self):
        return "<Artist %s>" % self.name
