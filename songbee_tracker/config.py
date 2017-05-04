from smartgetenv import get_env, get_list

BANNER = get_env("BANNER", "Songbee Tracker v{version}")

SECRET_KEY = get_env("SECRET_KEY")

TRACKERS = get_list("TRACKERS", [
    "udp://bt.songbee.net:6969/announce",
    "http://bt.songbee.net/announce",
    "udp://tracker.openbittorrent.com:80/announce",
    "udp://tracker.leechers-paradise.org:6969/announce",
    "udp://IPv6.leechers-paradise.org:6969/announce",
    "udp://tracker.coppersurfer.tk:6969/announce",
    "http://retracker.local/announce",
])
PRIMARY_TRACKER = TRACKERS[0]
SCRAPE_URL = get_env("SCRAPE_URL", "http://bt.songbee.net/scrape")
TORRENT_PUBLISHER = get_env("TORRENT_PUBLISHER", "Songbee")
TORRENT_PUBLISHER_URL = get_env("TORRENT_PUBLISHER_URL", "http://songbee.net")
TORRENT_COMMENT = get_env("TORRENT_COMMENT", TORRENT_PUBLISHER_URL)

SQLALCHEMY_DATABASE_URI = get_env("DATABASE_URL", "postgres://")
