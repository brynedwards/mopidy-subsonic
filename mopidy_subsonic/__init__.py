import pathlib

import pkg_resources

from mopidy import config, ext

__version__ = pkg_resources.get_distribution("Mopidy-Subsonic").version


class Extension(ext.Extension):

    dist_name = "Mopidy-Subsonic"
    ext_name = "subsonic"
    version = __version__

    def get_default_config(self):
        return config.read(pathlib.Path(__file__).parent / "ext.conf")

    def get_config_schema(self):
        schema = super().get_config_schema()

        schema["base_url"] = config.String()
        schema["username"] = config.String()
        schema["password"] = config.Secret()
        schema["port"] = config.Port(optional=True)
        return schema

    def setup(self, registry):
        from .backend import SubsonicBackend
        registry.add("backend", SubsonicBackend)
