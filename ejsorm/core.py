import os
import pathlib
from typing import Optional, Type, Union

from . import EJModel
from .constants import DEFAULT_FILE_NAME, DEFAULT_DATA, ENCODING, PK_FIELD
from .exceptions import EJException
from .reference import REF, Reference

try:
    import orjson as json
except ImportError:
    import json


class EJ:
    def __init__(self, file_name: str = DEFAULT_FILE_NAME, ensure_ascii: bool = False):
        self.file_name = file_name
        self.ensure_ascii = ensure_ascii
        self._check_file()
        self._data: Optional[dict] = None
        self.models: dict[str, EJModel] = {}

    @property
    def data(self):
        if self._data is None:
            self._data = self._read()
        return self._data

    @data.setter
    def data(self, new_data: dict):
        self._data = new_data

    def _read(self):
        return json.loads(pathlib.Path(self.file_name).read_text(encoding=ENCODING))

    def _dump(self):
        return pathlib.Path(self.file_name).write_text(
            json.dumps(self.data, ensure_ascii=self.ensure_ascii), encoding=ENCODING
        )

    def _check_file(self):
        if not os.path.exists(self.file_name):
            return pathlib.Path(self.file_name).write_text(
                json.dumps(DEFAULT_DATA, ensure_ascii=self.ensure_ascii)
            )
        if self.read_metadata() != DEFAULT_DATA["metadata"]:
            raise EJException("file is invalid, recreate it.")

    def read_metadata(self) -> Optional[dict]:
        return self._read().get("metadata")

    def init_models(self, *models: Type[EJModel]):
        for model in models:
            model.__db__ = self
            self.models[model.__name__] = model

    def drop(self):
        self.data = DEFAULT_DATA
        self._dump()

    def get_table_data(self, table_name: str) -> dict:
        tables = self.data["tables"]
        if table_name not in tables:
            tables[table_name] = {}
        return tables[table_name]

    def get_model_by_ref(self, ref_string: str) -> EJModel:
        class_name = ref_string.split("/")[-1]
        if class_name not in self.models:
            raise EJException(f"model <{class_name}> not initialized")
        return self.models[class_name]

    def get_references(self, model: Union[Type[EJModel], EJModel]) -> list[Reference]:
        references = []
        for property_name, property_data in model.get_properties():
            if REF not in property_data:
                continue
            references.append(
                Reference(
                    model=self.get_model_by_ref(
                        property_data[REF],
                    ),
                    field_title=property_name,
                )
            )
        return references

    def create(self, model: EJModel) -> EJModel:
        table_data = self.get_table_data(model.table_name())
        last_id = len(table_data.keys()) + 1
        model_dict = model.dict()

        for reference in model.get_references():
            reference_field = model_dict[reference.field_title]
            if reference_field is None:
                continue
            reference_id = reference_field[PK_FIELD]
            if reference_id is None:
                raise EJException(
                    f"no instanse of <{reference.field_title}>, reference must exist"
                )
            model_dict[
                reference.field_title
            ] = f"{reference.model.table_name()}_{reference_id}"

        del model_dict[PK_FIELD]
        table_data[last_id] = model_dict
        model.id = last_id
        self._dump()
        return model

    def get(self, model: Union[Type[EJModel], EJModel], **kwargs):
        table_data = self.get_table_data(model.table_name())
        if PK_FIELD in kwargs:
            object_id = kwargs[PK_FIELD]
            if object_id not in table_data:
                raise EJException(f"no such model {model.__name__}(id={object_id})")
            result_data = table_data[object_id]

            for reference in model.get_references():
                reference_data = result_data[reference.field_title]
                if isinstance(reference_data, EJModel):
                    reference_id = reference_data.id
                else:
                    reference_id = int(
                        reference_data.removeprefix(f"{reference.model.table_name()}_")
                    )
                result_data[reference.field_title] = self.get(
                    reference.model, id=reference_id
                )
            return model(**table_data[object_id], id=object_id)

        match_count = len(kwargs)
        current_match = 0
        # TODO: кварги нет в схеме
        # owner_id owner__name lt gt etc
        for pk, data in table_data.items():
            for key, value in kwargs.items():
                if data.get(key) == value:
                    current_match += 1
                if current_match == match_count:
                    return model(**data, id=pk)
