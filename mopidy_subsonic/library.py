import logging

from mopidy import backend
from mopidy.models import Album, Artist, Ref, Track

logger = logging.getLogger(__name__)


class SubsonicLibraryProvider(backend.LibraryProvider):
    root_directory = Ref.directory(uri="subsonic:root", name="Subsonic")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.client = self.backend.client

        self._root = [
            Ref.directory(uri="subsonic:directory", name="Folders"),
            Ref.directory(uri="subsonic:album", name="Albums"),
            Ref.directory(uri="subsonic:artist", name="Artists"),
            Ref.directory(uri="subsonic:track", name="Tracks"),
            Ref.directory(uri="subsonic:genre", name="Genres"),
        ]

    def _do(self, *args, **kwargs):
        return self.client.do(*args, **kwargs)

    def browse(self, uri):
        logger.debug("browse: %s", str(uri))
        if not uri:
            return []

        if uri == self.root_directory.uri:
            return self._root

        if uri == "subsonic:artist":
            return self._browse_artists()

        parts = uri.split(":")

        if len(parts) == 3 and parts[1] == "artist":
            return self._browse_artist(parts[2])

        if len(parts) == 3 and parts[1] == "album":
            return self._browse_album(parts[2])

        logger.debug("Unknown uri for browse request: %s", uri)
        return []

    def lookup(self, uri):
        if uri.startswith("subsonic:track:"):
            return self._lookup_track(uri)
        elif uri.startswith("subsonic:album:"):
            return self._lookup_album(uri)
        elif uri.startswith("subsonic:artist:"):
            return self._lookup_artist(uri)
        else:
            return []

    def _lookup_track(self, uri):
        track = self._do("getSong", {"id": uri.split(":")[2]})["song"]
        return [Track(
            uri="subsonic:track:" + track["id"],
            name=track["title"],
            artists=[Artist(uri="subsonic:artist:" + track["artistId"], name=track["artist"])],
            album=Album(uri="subsonic:album:" + track["album"], name=track["album"]),
            track_no=track["track"],
            disc_no=track["discNumber"],
            length=track["duration"] * 1000,
            bitrate=track["bitRate"]
        )]

    def _browse_artists(self):
        response = self._do("getArtists")
        artists = [
            artist
            for index in response["artists"]["index"]
            for artist in index["artist"]
        ]
        return [
            Ref.directory(uri="subsonic:artist:" + a["id"], name=a["name"])
            for a in artists
        ]

    def _browse_artist(self, id):
        response = self._do("getArtist", params={"id": id})
        albums = [album for album in response["artist"]["album"]]
        return [
            Ref.directory(uri="subsonic:album:" + a["id"], name=a["name"])
            for a in albums
        ]

    def _browse_album(self, id):
        response = self._do("getAlbum", params={"id": id})
        tracks = [track for track in response["album"]["song"]]
        return [
            Ref.track(uri="subsonic:track:" + a["id"], name=a["title"])
            for a in tracks
        ]
