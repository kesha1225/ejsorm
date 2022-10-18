from typing import Optional, Dict, Any, TYPE_CHECKING

from pydantic import BaseModel

from ejsorm.exceptions import EJException

if TYPE_CHECKING:
    from ejsorm.reference import Reference
    from ejsorm.core import EJ


class EJModel(BaseModel):
    # TODO: constaints (uniq, etc)
    __table__: Optional[str] = None
    __db__: Optional["EJ"] = None
    id: Optional[int] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @classmethod
    def table_name(cls) -> str:
        return cls.__table__ or cls.__name__

    @classmethod
    def get_properties(cls) -> list[tuple[str, dict]]:
        return cls.schema()["properties"].items()

    @classmethod
    def get_references(cls) -> list["Reference"]:
        return cls.__db__.get_references(cls)

    def __init_subclass__(cls, **kwargs):
        cls.__table__ = kwargs.get("table")

    def create(self) -> "EJModel":
        if self.__db__ is None:
            raise EJException(f"model <{self.__class__.__name__}> is not initialized")
        return self.__db__.create(self)

    @classmethod
    def get(cls, **kwargs):
        return cls.__db__.get(cls, **kwargs)

    # def dict(self, *args, **kwargs) -> Dict[str, Any]:
    #     # а че если что то уже ексклюдится..
    #     kwargs["exclude"] = {"id"}
    #     return super().dict(*args, **kwargs)


# TODO
# class MyBase(BaseModel):
#     pass
#
#
# class Car(MyBase):
#     number: int
#
# number= typehint!!
# Car()
