from .constants import DEFAULT_FILE_NAME

try:
    import orjson as json
except ImportError:
    import json


class Ejsorm:
    def __init__(self, file_name: str = DEFAULT_FILE_NAME):
        self.file_name = file_name

