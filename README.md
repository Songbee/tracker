# Songbee Tracker

A torrent server, generating torrent files on the fly and serving some statistics.


## Installing

Please note that you'll also need to run your own torrent tracker for this to work. We're running an open instance at `http://bt.songbee.net/announce` / `udp://bt.songbee.net:6969/announce` (hardcoded for now) but please don't use it for anything serious (and illegal! :). An easy start is to run [opentracker in Docker](https://github.com/Lednerb/opentracker-docker).

```bash
docker-compose run web flask initdb
docker-compose up
```

### ...without Docker!

M'kay, m'kay, I got it. You'll need to set PostgreSQL connection info in `songbee_tracker/models.py` (other databases aren't supported for now). Apart from that,

```bash
virtualenv -p python3.5 venv
. venv/bin/activate
pip install -r requirements.txt
export FLASK_APP="songbee_tracker/__init__.py"
export SECRET_KEY="foo"
# See config.py for more configuration options
flask run
```


## API

```bash
$ http post http://127.0.0.1:5000/api/v1/releases --form torrent@my.torrent
# As in:
#
# <form action="/api/v1/releases" method="POST" enctype="multipart/form-data">
#   <input type="file" name="torrent"><br>
#   <input type="submit">
# </form>
#
# (this form is also available at http://127.0.0.1:5000/)

{
    "artist": "", 
    "id": "deadface-3046-402b-8dc7-8d0da84304f0", 
    "stats": {
        "complete": null, 
        "downloaded": null, 
        "incomplete": null
    }, 
    "title": "", 
    "tracks": []
}
```

We'll now see our release in the list:

```bash
$ http get http://127.0.0.1:5000/api/v1/releases

[
    {
        "artist": "", 
        "id": "deadface-3046-402b-8dc7-8d0da84304f0", 
        "stats": {
            "complete": null, 
            "downloaded": null, 
            "incomplete": null
        }, 
        "title": "", 
        "tracks": []
    }
]
```

...and via permalink:

```bash
$ http get http://127.0.0.1:5000/api/v1/releases/deadface-3046-402b-8dc7-8d0da84304f0

{
    "artist": "", 
    "id": "deadface-3046-402b-8dc7-8d0da84304f0", 
    "stats": {
        "complete": null, 
        "downloaded": null, 
        "incomplete": null
    }, 
    "title": "", 
    "tracks": []
}
```

Let's add some metainfo now:

```bash
$ http patch http://127.0.0.1:5000/api/v1/releases/deadface-3046-402b-8dc7-8d0da84304f0 \
    --json artist=Pendulum title=Immersion

{
    "artist": "Pendulum", 
    "id": "deadface-3046-402b-8dc7-8d0da84304f0", 
    "stats": {
        "complete": null, 
        "downloaded": null, 
        "incomplete": null
    }, 
    "title": "Immersion", 
    "tracks": []
}
```

Looks great! Except the `stats` field, it's a bit empty. Let's change that.

```bash
$ http get http://127.0.0.1:5000/api/v1/releases/deadface-3046-402b-8dc7-8d0da84304f0/torrent > my-new.torrent
$ qbittorrent my-new.torrent &  # your favourite torrent client here

$ http get http://127.0.0.1:5000/api/v1/releases/deadface-3046-402b-8dc7-8d0da84304f0

{
    "artist": "Pendulum", 
    "id": "deadface-3046-402b-8dc7-8d0da84304f0", 
    "stats": {
        "complete": 0, 
        "downloaded": 0, 
        "incomplete": 1  // we're here!
    }, 
    "title": "Immersion", 
    "tracks": []
}
```

It works!

**Bonus:** let's examine the `my-new.torrent` file. We have a handy tool `bdecode.py` (in the repo root) for that:

```bash
$ venv/bin/python bdecode.py my-new.torrent
{b'announce': b'http://bt.songbee.net/announce',
 b'announce-list': [[b'http://bt.songbee.net/announce'],
                    [b'udp://exodus.desync.com:6969/announce'],
                    [b'udp://zer0day.ch:1337'],
                    [b'udp://tracker.coppersurfer.tk:6969/announce'],
                    [b'udp://IPv6.leechers-paradise.org:6969/announce']],
 b'comment': b'https://tracker.songbee.net/',
 b'created by': b'Songbee Tracker/0.0.0',
 b'encoding': b'UTF-8',
 b'info': {b'files': [{b'length': 3447551,
                       b'path': [b'Immersion', b'rickroll.mp3']}],
           b'name': b'Pendulum',
           b'piece length': 262144,
           b'pieces': '(...)'},
 b'publisher': b'songbee.net',
 b'publisher-url': b'https://tracker.songbee.net/',
 b'x-songbee': {b'artist': b'Pendulum',
                b'id': b'deadface-3046-402b-8dc7-8d0da84304f0',
                b'title': b'Immersion',
                b'tracker': b'https://tracker.songbee.net/',
                b'tracks': {}}}
```

As we see, a copy of the metadata is embedded into the torrent file. Quite handy, isn't it?