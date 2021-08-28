import enum
from typing import Optional

from ejsorm import EjModel


class PetType(enum.Enum):
    CAT = "CAT"
    DOG = "DOG"


class Pet(EjModel):
    pet_type: PetType
    name: str


class Number(EjModel):
    value: int


class UserDB(EjModel):
    username: str
    age: Optional[int] = None
    pet: Pet
    numbers: list[Number]


