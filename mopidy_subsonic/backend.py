import logging
import time
# from threading import Lock

import pykka

from mopidy import backend

from .client import SubsonicClient
from .library import SubsonicLibraryProvider
from .playback import SubsonicPlaybackProvider
# from .playlists import SubsonicPlaylistsProvider
# from .repeating_timer import RepeatingTimer
# from .session import SubsonicSession

logger = logging.getLogger(__name__)


class SubsonicBackend(
    pykka.ThreadingActor, backend.Backend
):
    def __init__(self, config, audio):
        super().__init__()

        self.config = config
        self.client = SubsonicClient(config)

        self.library = SubsonicLibraryProvider(backend=self)
        self.playback = SubsonicPlaybackProvider(audio=audio, backend=self)
        # self.playlists = SubsonicPlaylistsProvider(backend=self)

        self.uri_schemes = ["subsonic"]
