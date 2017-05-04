from ..util import APIMethodView, external_url_for


class IndexView(APIMethodView):
    def get(self):
        return {
            "search_url": external_url_for(".search"),
            "artists_url": external_url_for(".artists"),
            "albums_url": external_url_for(".albums"),
            "torrents_url": external_url_for(".torrents"),
        }
