import typing

import pydantic
from pydantic.main import ModelMetaclass

from heftydb.response import ResponseModel

T = typing.TypeVar("T")


class HeftyField:
    def __init__(self, field, field_obj, obj_name):
        self.__field = field
        self.__field_obj = field_obj
        self.__obj = obj_name
        self.__parsed_obj = obj_name.parse_obj(field_obj.__dict__)

    def add(self, db, *args):
        # тут надо не ток для листов сделать
        if "typing.List" not in str(self.__field.outer_type_):
            raise RuntimeError("не лист добавлять нельзя...")
        current_value: typing.Optional[
            typing.List[typing.Any]
        ] = self.__field_obj.dict()[self.__field.name]
        if current_value is None:
            current_value = list(args)
        else:
            current_value.extend(args)
        self.__field_obj.__dict__[self.__field.name] = current_value
        db.update(
            self.__parsed_obj, self.__field_obj.__dict__["__id"],
        )

    def __iter__(self):
        return iter(self.__field_obj.__dict__[self.__field.name])

    def __repr__(self):
        item = self.__field_obj.dict()[self.__field.name]
        if isinstance(item, dict):
            return " ".join(
                f"{k}={v!r}"
                for k, v in self.__field_obj.dict()[self.__field.name].items()
            )
        return repr(item)

    def __getattr__(self, item):
        if item == "pk":
            return self.__field_obj.dict()[self.__field.name]["__id"]
        return self.__field_obj.dict()[self.__field.name][item]


class MetaField:
    def __init__(
        self, field, local_fields, stack: typing.Optional[typing.List[str]] = None
    ):
        self.stack = stack

        if stack is None:
            self.stack = []
        self.stack.append(field.name)

        self.field = field
        self.local_fields = local_fields

    def __getattr__(self, item):

        return MetaField(
            field=self.local_fields[self.field.name].type_.__fields__[item],
            local_fields=self.local_fields,
            stack=self.stack,
        )


class HeftyModelmeta(ModelMetaclass):
    def __getattr__(self, item):
        local_fields = self.__fields__

        if item in local_fields:
            return MetaField(field=local_fields[item], local_fields=local_fields)
        return super().__getattribute__(item)


class HeftyModel(pydantic.BaseModel, metaclass=HeftyModelmeta):
    __database__ = None

    @classmethod
    def create(cls, **kwargs) -> T:
        obj: T = cls.parse_obj(kwargs)
        obj_id = cls.__database__.write(obj)
        setattr(obj, "__id", obj_id)
        return obj

    def save(self) -> T:
        obj: T = self.parse_obj(self.dict())
        obj_id = self.__database__.write(obj)

        # hak)
        setattr(obj, "__id", obj_id)
        return obj

    def delete(self) -> None:
        self.__database__.delete(
            table_name=self.__class__.__name__, to_delete=self.dict()
        )

    @classmethod
    def get_one(
        cls, return_raw: bool = False, with_refs: bool = True, **kwargs,
    ) -> "HeftyModel":
        return cls.__database__.find_one(
            find_obj=cls, return_raw=return_raw, with_refs=with_refs, **kwargs
        )

    @classmethod
    def get_all(
        cls, return_raw: bool = False, with_refs: bool = True, **kwargs,
    ) -> ResponseModel:
        # TODO: возвращаемый тип
        return ResponseModel(
            cls.__database__.find_all(
                find_obj=cls, return_raw=return_raw, with_refs=with_refs, **kwargs
            )
        )

    def __setattr__(self, key, value):
        # vfvf ,kz...

        if key == "__id":
            self.__dict__[key] = value
            return None
        return super(HeftyModel, self).__setattr__(key, value)

    def __getattribute__(self, item):
        if item == "pk":
            return super().__getattribute__("__id")

        attr = super().__getattribute__(item)

        if item in super().__dict__:
            obj = super(HeftyModel, self)

            # why obj.fields is good but obj.__fields__ == {}
            field = obj.fields[item]
            # TODO: тут наверное не только листы надо переделывать и вообще ужас какой то
            if "typing.List" in str(field.outer_type_):
                return HeftyField(field, obj, self.__class__)
        return attr
