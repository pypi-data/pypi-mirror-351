import json
import os
import uuid
import re
from copy import deepcopy
from pathlib import Path
from threading import Lock
from typing import List, Optional, Union, Pattern

# from app.core.CustomLogging import logger
from seCore.jsondb.db_types import DBSchemaType, IdGeneratorType, NewKeyValidTypes, SingleDataType, ReturnWithIdType, QueryType
from seCore.jsondb.errors import IdDoesNotExistError, SchemaTypeError, UnknownKeyError, IdAllReadyExistError

from seCore import logger

# https://dollardhingra.com/blog/python-json-benchmarking
try:
    import ujson
    UJSON = True
except ImportError: # pragma: no cover
    UJSON = False


class JsonDB:

    def __init__(self, filename: str, auto_update: bool = True, indent: int = 4, ujson: bool = None, load_json: DBSchemaType = None) -> None:
        self.filename = filename
        self.auto_update = auto_update
        self._au_memory: DBSchemaType = {'keys': [], 'data': {}}
        self.indent = indent
        self.lock = Lock()

        self.ujson = UJSON if ujson is None else ujson

        if load_json is not None:
            self._au_memory = load_json
            self.auto_update = False

        self._gen_db_file()

    def _load_file(self) -> DBSchemaType:
        if self.auto_update:
            with open(self.filename, encoding='utf-8', mode='r') as f:
                if self.ujson:
                    return ujson.load(f)
                else:
                    return json.load(f)
        else:
            return deepcopy(self._au_memory)

    def _dump_file(self, data: DBSchemaType) -> None:
        if self.auto_update:
            if os.path.exists(self.filename):   # ToDo: Throw exception if file/folder does not exist
                with open(self.filename, encoding='utf-8', mode='w') as f:
                    if self.ujson:
                        ujson.dump(data, f, indent=self.indent)
                    else:
                        json.dump(data, f, indent=self.indent)
        else:
            self._au_memory = deepcopy(data)
        return None

    def _gen_db_file(self) -> None:
        if self.auto_update:
            if not Path(self.filename).is_file(): # pragma: no cover
                self.lock.acquire()
                self._dump_file(
                    {'keys': [], 'data': {}}
                )
                self.lock.release()

    def force_load(self) -> None:
        """
        Used when the data from a file needs to be loaded when auto update is turned off.
        """
        if not self.auto_update:
            self.auto_update = True
            self._au_memory = self._load_file()
            self.auto_update = False

    def commit(self) -> None:
        if not self.auto_update:
            self.auto_update = True
            self._dump_file(self._au_memory)
            self.auto_update = False

    def stats(self) -> dict:
        with self.lock:
            data = self._load_file()['data']
            if isinstance(data, dict):
                return {
                    "Count": len(data)
                    }
        return {} # pragma: no cover

    def add(self, data: object) -> str:
        if not isinstance(data, dict):
            raise TypeError(f'data must be of type dict and not {type(data)}')

        with self.lock:
            db_data = self._load_file()

            keys = db_data['keys']
            if not isinstance(keys, list): # pragma: no cover
                raise SchemaTypeError(f"keys must be of type 'list' and not {type(keys)}")
            if len(keys) == 0:
                db_data['keys'] = sorted(list(data.keys()))
            else:
                if not sorted(keys) == sorted(data.keys()):
                    raise UnknownKeyError(
                        f'Unrecognized / missing key(s) {set(keys) ^ set(data.keys())}'
                        '(Either the key(s) does not exists in the DB or is missing in the given data)'
                    )

            if not isinstance(db_data['data'], dict): # pragma: no cover
                raise SchemaTypeError('data key in the db must be of type "dict"')

            logger.debug(f'data: {data}')
            if "key" in data:
                _id = data['key']
            elif "Key" in data:
                _id = data['Key']
                if _id == "00000000-0000-0000-0000-000000000000":
                    _id = str(uuid.uuid4())
                    data['Key'] = _id
            else:
                _id = str(uuid.uuid4())

            if _id not in db_data['data']:
                db_data['data'][_id] = data
                self._dump_file(db_data)
                return _id
            else:
                raise IdAllReadyExistError(f'Id `{_id}` already in DB')

    def add_many(self, data: list, json_response: bool = True) -> Union[SingleDataType, None]:

        new_data = {}

        for d in data:
            try:
                _id = self.add(d)

            except Exception as e: # pragma: no cover
                # todo: Add exception instead of logging
                logger.debug(f"Add Many - Exception: {e}")

            else:
                if json_response:
                    new_data[_id] = self.get_by_id(_id)

        logger.info(json.dumps({"jsonDB": "add_many",
                                "count": len(new_data),
                                "data": new_data
                                }))

        return new_data if json_response else None

    def get_all(self) -> ReturnWithIdType:
        with self.lock:
            data = self._load_file()['data']
            if isinstance(data, dict):
                return data
        return {} # pragma: no cover

    def get_by_id(self, id: str) -> SingleDataType:
        if not isinstance(id, str):  # pragma: no cover
            raise TypeError(f'id must be of type "str" and not {type(id)}')

        with self.lock:
            data = self._load_file()['data']
            if isinstance(data, dict):
                if id in data:
                    return data[id]
                else:
                    raise IdDoesNotExistError(f'{id!r} does not exists in the DB')  # pragma: no cover
            else:
                raise SchemaTypeError('"data" key in the DB must be of type dict')  # pragma: no cover

    def get_by_query(self, query: QueryType) -> ReturnWithIdType:
        if not callable(query):  # pragma: no cover
            raise TypeError(f'"query" must be a callable and not {type(query)!r}')

        with self.lock:
            new_data: ReturnWithIdType = {}
            data = self._load_file()['data']
            if isinstance(data, dict):
                for id, values in data.items():
                    if isinstance(values, dict):
                        if query(values):
                            new_data[id] = values

            return new_data

    def get_by_search(self, key: str, _re: Union[str, Pattern[str]]) -> tuple[list[int | str | bool], int]:

        pattern = _re
        if not isinstance(_re, re.Pattern):
            pattern = re.compile(str(_re))

        items = []
        data = self.get_all()

        for d in data:
            for k, v in data[d].items():
                if k == key and re.search(pattern, v):
                    items.append(v)
                    continue

        return items, len(items)

    def update_by_id(self, id: str, new_data: object) -> SingleDataType:
        if not isinstance(new_data, dict):  # pragma: no cover
            raise TypeError(f'new_data must be of type dict and not {type(new_data)!r}')

        with self.lock:
            data = self._load_file()
            keys = data['keys']

            if isinstance(keys, list):
                if not all(i in keys for i in new_data):  # pragma: no cover
                    raise UnknownKeyError(f'Unrecognized key(s) {[i for i in new_data if i not in keys]}')

            if not isinstance(data['data'], dict): # pragma: no cover
                raise SchemaTypeError('the value for the data keys in the DB must be of type dict')

            if id not in data['data']:  # pragma: no cover
                raise IdDoesNotExistError(f'The id {id!r} does noe exists in the DB')

            data['data'][id] = {**data['data'][id], **new_data}

            self._dump_file(data)
            return data['data'][id]

    def update_by_query(self, query: QueryType, new_data: object) -> List[str]:
        if not callable(query):  # pragma: no cover
            raise TypeError(f'"query" must be a callable and not {type(query)!r}')

        if not isinstance(new_data, dict):  # pragma: no cover
            raise TypeError(f'"new_data" must be of type dict and not f{type(new_data)!r}')

        with self.lock:
            updated_keys = []
            db_data = self._load_file()
            keys = db_data['keys']

            if isinstance(keys, list):
                if not all(i in keys for i in new_data):  # pragma: no cover
                    raise UnknownKeyError(f'Unrecognized / missing key(s) {[i for i in new_data if i not in keys]}')

            if not isinstance(db_data['data'], dict):  # pragma: no cover
                raise SchemaTypeError('The data key in the DB must be of type dict')

            for key, value in db_data['data'].items():
                if query(value):
                    db_data['data'][key] = {**db_data['data'][key], **new_data}
                    updated_keys.append(key)

            self._dump_file(db_data)
            return updated_keys

    def delete_by_id(self, id: str) -> None:
        with self.lock:
            data = self._load_file()
            if not isinstance(data['data'], dict):  # pragma: no cover
                raise SchemaTypeError('"data" key in the DB must be of type dict')
            if id not in data['data']:  # pragma: no cover
                raise IdDoesNotExistError(f'ID {id} does not exists in the DB')
            del data['data'][id]

            self._dump_file(data)

    def delete_by_query(self, query: QueryType) -> List[str]:
        if not callable(query):
            raise TypeError(f'"query" must be a callable and not {type(query)!r}')  # pragma: no cover

        with self.lock:
            data = self._load_file()
            if not isinstance(data['data'], dict):
                raise SchemaTypeError('"data" key in the DB must be of type dict')  # pragma: no cover
            ids_to_delete = []
            for id, value in data['data'].items():
                if query(value):
                    ids_to_delete.append(id)
            for id in ids_to_delete:
                del data['data'][id]

            self._dump_file(data)
            return ids_to_delete

    def purge(self) -> None:
        with self.lock:
            data = self._load_file()
            if not isinstance(data['data'], dict):  # pragma: no cover
                raise SchemaTypeError('"data" key in the DB must be of type dict')
            if not isinstance(data['keys'], list):  # pragma: no cover
                raise SchemaTypeError('"key" key in the DB must be of type dict')
            data['data'] = {}
            data['keys'] = []
            self._dump_file(data)

    def add_new_key(self, key: str, default: Optional[NewKeyValidTypes] = None) -> None:

        if default is not None:
            if not isinstance(default, (list, str, int, bool, dict)):
                raise TypeError(
                    f'default field must be of any of (list, int, str, bool, dict) but for {type(default)}')

        with self.lock:
            data = self._load_file()
            if isinstance(data['keys'], list):
                if key in data['keys']:
                    raise KeyError(f'Key {key!r} already exists in the DB')

                data['keys'].append(key)
                data['keys'].sort()

            if isinstance(data['data'], dict): # pragma: no cover
                for d in data['data'].values():
                    logger.warning(d)
                    if key not in d:
                        d[key] = default

            self._dump_file(data)

    def dump_json(self):
        data = self._load_file()

        return data
