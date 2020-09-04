import os
import typing
import copy

import orjson
from pydantic.fields import ModelField
from pydantic.main import ModelMetaclass, BaseConfig

from ._types import HeftyData, HeftyTable, HeftyTableData, HeftyObject
from .exceptions import HeftyError
from .filters import HEFTY_FILTERS
from .models import HeftyModel

DOUBLE_UNDERSCORE = "__"
HEFTY_OBJECT_ID_FIELD = "__id"

AVAILABLE_MAPPING_TYPES_KEY = (str,)
AVAILABLE_MAPPING_TYPES_VALUE = (str, int, float, None, bool)

PK_FIELD = ModelField(
    name="__id",
    type_=int,
    required=True,
    model_config=BaseConfig,
    class_validators=None,
)


class HeftyDB:
    def __init__(self, path: str):
        if not path.endswith(".json"):
            raise HeftyError(f"Path must has .json file extension, got {path}")
        self.path = path
        self._data: typing.Optional[HeftyData] = None

    @property
    def data(self) -> HeftyData:
        if self._data is None:
            self._data = self._loads_data()
        return self._data

    def drop(self):
        self.__save(
            [{"__heftydb__": "generated"}, {"__table__": "__other", "__data__": {}}]
        )
        return self.data

    def _loads_data(self):
        if not os.path.exists(self.path):
            return self.drop()

        with open(self.path) as file:
            data = orjson.loads(file.read())
            if not {"__heftydb__": "generated"} in data:
                raise HeftyError(
                    "File is not generated by HeftyDB, clear it or delete or use db.drop() and rerun"
                )
        return data

    def __save(self, data: HeftyData):
        self._data = data
        with open(self.path, "wb") as file:
            file.write(orjson.dumps(self._data))

    def _get_table(self, table_name: str) -> HeftyTable:
        for _table in self.data[1:]:
            if _table["__table__"] == table_name:
                return _table
        _table = {"__table__": table_name, "__data__": []}
        self.data.append(_table)
        return _table

    def _get_table_data(self, table_name: str) -> HeftyTableData:
        current_table = self._get_table(table_name)
        current_table_data: HeftyTableData = current_table["__data__"]
        return current_table_data

    def _get_table_data_from_obj(
            self, find_obj: typing.Union[typing.Type[HeftyModel], str]
    ):
        return self._get_table_data(
            find_obj if isinstance(find_obj, str) else find_obj.__name__
        )

    @staticmethod
    def _check_return_raw_and_get_refs(return_raw: bool, with_refs: bool):
        if not return_raw and not with_refs:
            raise HeftyError(
                "'return_raw=False' can work only with 'get_all_refs=True'. Can work with:\n"
                "db.find_one(..., return_raw=True, with_refs=True),\n"
                "db.find_one(..., return_raw=False, with_refs=True),\n"
                "db.find_one(..., return_raw=True, with_refs=False),\n"
            )

    def _save_element(self, table_name: str, obj: HeftyObject) -> int:
        current_table_data = self._get_table_data(table_name)
        obj_id = len(current_table_data)
        obj.update({"__id": obj_id})
        current_table_data.append(obj)
        data = self.data
        self.__save(self.data)
        return obj_id

    def _get_object_from_str_reference(self, str_reference: str):
        ref_table, ref_id = str_reference.split("_")[3:5]
        obj = self.find_one(ref_table, __id=int(ref_id), return_raw=True)
        return obj

    def _get_all_obj_refs(self, obj):
        obj = copy.deepcopy(obj)
        for obj_key, obj_value in obj.copy().items():
            found_obj_values = obj_value if isinstance(obj_value, list) else [obj_value]
            obj[obj_key] = []
            for found_obj_value in found_obj_values:
                if isinstance(found_obj_value, str) and found_obj_value.startswith(
                        "__reference"
                ):
                    obj[obj_key].append(
                        self._get_object_from_str_reference(found_obj_value)
                    )
                else:
                    obj[obj_key].append(found_obj_value)
            obj[obj_key] = (
                obj[obj_key] if isinstance(obj_value, list) else obj[obj_key][0]
            )
        return obj

    def _check_obj(self, obj: dict, check_kwargs: dict):
        # todo: че делать если там лист с рефами
        # todo: sort skip limit
        found = []
        checked_reference_keys = []

        obj = obj.copy()

        obj = self._get_all_obj_refs(obj)

        for obj_key, obj_value in obj.items():
            for find_key, find_value in check_kwargs.items():
                if (
                        DOUBLE_UNDERSCORE in find_key
                        and find_key != HEFTY_OBJECT_ID_FIELD
                        and find_key not in checked_reference_keys
                ):
                    # obj = self._get_all_obj_refs(obj)
                    # хз может как то по кускам доставать

                    query: typing.List[str] = find_key.split(DOUBLE_UNDERSCORE)
                    query_filter = None
                    if query[-1] in HEFTY_FILTERS:
                        query_filter = query.pop()
                    for element_number in range(len(query)):
                        child_field = query[element_number]
                        child_obj = obj

                        if len(query) >= element_number + 1:
                            child_fields = query[: element_number + 2]
                            for field in child_fields[:-1]:
                                child_obj = child_obj.get(field)
                                if child_obj is None:
                                    raise HeftyError(f"Object doesn't have field - {field}")
                        if query_filter is not None:
                            if child_field not in child_obj:
                                continue
                            found.append(
                                HEFTY_FILTERS[query_filter](
                                    child_obj, child_field, find_value
                                )
                            )
                        elif self._check_obj(child_obj, {child_field: find_value}):
                            found.append(True)
                        checked_reference_keys.append(find_key)

                if find_key == obj_key:
                    if find_value == obj_value:
                        found.append(True)
                        continue

                    # {'name': 'New Tournament', '__id': 0} {'name': 'New Tournament'} мудила гороховый
                    if isinstance(obj_value, dict) and isinstance(find_value, dict):
                        if obj_value.get("__id") is not None:
                            # так а зачем я это ваще писал
                            # print(obj_value)
                            # del obj_value["__id"]
                            pass
                    # опять ты выходишь на связь
                    if find_value == obj_value:
                        found.append(True)
        return bool(found and all(found) and len(found) == len(check_kwargs))

    def find_one(
            self,
            find_obj: typing.Union[typing.Type[HeftyModel], str],
            return_raw: bool = False,
            with_refs: bool = True,
            **kwargs,
    ) -> typing.Optional[typing.Union[HeftyObject, typing.Any]]:
        self._check_return_raw_and_get_refs(return_raw, with_refs)
        current_table_data = self._get_table_data_from_obj(find_obj)

        if not kwargs:
            if with_refs:
                return (
                    self._get_all_obj_refs(current_table_data)[0]
                    if current_table_data
                    else []
                )
            return current_table_data[0] if current_table_data else []

        for obj in current_table_data:
            if self._check_obj(obj, kwargs):
                break
        else:
            return None

        if with_refs:
            obj = self._get_all_obj_refs(obj)
        if return_raw:
            return obj

        if issubclass(find_obj, HeftyModel):
            references = self._get_object_references_fields(find_obj.__fields__)
            find_obj.__fields__["__id"] = PK_FIELD
            for ref in references:
                ref.type_.__fields__["__id"] = PK_FIELD

            object_model = find_obj(**obj)
            # setattr(object_model, "__id", obj["__id"])

            # setattr(object_model, "__db", self)
            # не хочешь сетаттр? я его тебе прямо в регистры памяти суну тварь
            # object_model.__dict__["__db"] = self
            return object_model
        return obj

    def find_all(
            self,
            find_obj: typing.Union[typing.Type[HeftyModel], str],
            return_raw: bool = False,
            with_refs: bool = True,
            **kwargs,
    ) -> typing.Optional[
        typing.Union[typing.List[typing.Union[HeftyObject, typing.Any]]]
    ]:
        self._check_return_raw_and_get_refs(return_raw, with_refs)

        current_table_data = self._get_table_data_from_obj(find_obj)

        if not kwargs:
            if with_refs:
                if return_raw:
                    return [self._get_all_obj_refs(obj) for obj in current_table_data]
                return [
                    find_obj(**obj)
                    for obj in current_table_data
                    if issubclass(find_obj, HeftyModel)
                ]
            if return_raw:
                return current_table_data
            return [
                find_obj(**obj)
                for obj in current_table_data
                if issubclass(find_obj, HeftyModel)
            ]

        found_objs = []
        for obj in current_table_data:
            if self._check_obj(obj, kwargs):
                if with_refs:
                    obj = self._get_all_obj_refs(obj)
                found_objs.append(obj)
        if return_raw:
            return found_objs
        return [
            find_obj(**obj) for obj in found_objs if issubclass(find_obj, HeftyModel)
        ]

    @staticmethod
    def _get_reference_name(reference_table_title: str, reference_object_id: int):
        return f"__reference_{reference_table_title}_{reference_object_id}__"

    def _get_object_references_fields(
            self, obj_class_fields: typing.Dict[str, ModelField]
    ) -> typing.List[ModelField]:
        found_references = []

        for _, ref_field in obj_class_fields.items():
            ref_field: ModelField
            current_ref_field = ref_field
            if isinstance(current_ref_field, ModelField) and isinstance(
                    current_ref_field.type_, ModelMetaclass
            ):
                found_references.append(current_ref_field)
                current_ref_field = self._get_object_references_fields(
                    current_ref_field.type_.__fields__
                )
                found_references.extend(current_ref_field)

        return found_references

    @staticmethod
    def _check_model_fields(model_fields: typing.Dict[str, ModelField]):
        for _, field in model_fields.items():
            if field.key_field is None:
                continue
            if field.key_field.type_ not in AVAILABLE_MAPPING_TYPES_KEY:
                raise HeftyError(
                    f"Mapping key type must be in {AVAILABLE_MAPPING_TYPES_KEY}, got {field.key_field.type_}"
                )
            if field.type_ not in AVAILABLE_MAPPING_TYPES_VALUE:
                raise HeftyError(
                    f"Mapping value type must be in {AVAILABLE_MAPPING_TYPES_VALUE}, got {field.type_}"
                )

    def _add_to_table(self, table_name: str, obj: HeftyObject, obj_class: HeftyModel):
        # todo: решить че делать с диктовыми референасами (нужны ли они...)

        self._check_model_fields(obj_class.__fields__)

        found_references = self._get_object_references_fields(obj_class.__fields__)
        for ref in found_references:
            for ref_data in found_references:
                ref_key = ref_data.name
                current_ref_table_name = ref.type_.__name__
                if ref_data.name != ref.name or ref_data.name not in obj:
                    continue

                refs_data_to_find = (
                    obj[ref_key] if isinstance(obj[ref_key], list) else [obj[ref_key]]
                )
                if refs_data_to_find == [None] and not ref.required:
                    continue

                obj[ref_key] = []
                for ref_data_to_find in refs_data_to_find:
                    reference_in_db: list = self.find_all(
                        current_ref_table_name, **ref_data_to_find, return_raw=True, with_refs=False
                    )
                    if not reference_in_db:
                        reference_obj_id = self._add_to_table(
                            current_ref_table_name, ref_data_to_find, obj_class,
                        )
                        obj[ref_key].append(
                            self._get_reference_name(
                                current_ref_table_name, reference_obj_id
                            )
                        )
                    else:
                        for found_ref in reference_in_db:
                            obj[ref_key].append(
                                self._get_reference_name(
                                    current_ref_table_name, found_ref["__id"]
                                )
                            )
                obj[ref_key] = (
                    obj[ref_key] if len(obj[ref_key]) > 1 else obj[ref_key][0]
                )
        return self._save_element(table_name, obj)

    def delete(self, table_name: str, to_delete: HeftyObject):
        self._get_table_data(table_name).remove(to_delete)

    def update(self, obj: HeftyModel, model_id: int):
        old = self.find_one(
            obj.__class__.__name__,
            **{"__id": model_id},
            return_raw=True,
            with_refs=False,
        )
        self.delete(obj.__class__.__name__, old)
        self.write(obj)

    def write(self, obj: HeftyModel):
        return self._add_to_table(
            table_name=obj.__class__.__name__, obj_class=obj, obj=obj.dict(),
        )

    def write_many(self):
        pass
