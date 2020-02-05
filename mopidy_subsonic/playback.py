import logging

from mopidy import backend

logger = logging.getLogger(__name__)


class SubsonicPlaybackProvider(backend.PlaybackProvider):
    def translate_uri(self, uri):
        track_id = uri.rsplit(":")[-1]
        return self.backend.client.get_stream_uri(track_id)
        stream_uri = self.backend.client.get_stream_uri(track_id)

        logger.debug("Translated: %s -> %s", uri, stream_uri)
        return stream_uri
