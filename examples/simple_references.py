from typing import Optional

from ejsorm import EJModel, EJ


class Letter1(EJModel):
    test: str


class Letter2(EJModel):
    test: Letter1


class Letter3(EJModel):
    test: Letter2


class Letter4(EJModel):
    test: Letter3


class Number(EJModel):
    letters: Letter4


class User(EJModel):
    name: str
    number: Number


class Car(EJModel):
    numberplate: str
    mark: str
    owner: Optional[User]
    letter2: Letter2


db = EJ()
db.init_models(User, Car, Number, Letter4, Letter3, Letter2, Letter1)
db.drop()

letter2 = Letter2(test=Letter1(test="123").create()).create()
user1 = User(
    name="name",
    number=Number(
        letters=Letter4(test=Letter3(test=letter2).create()).create()
    ).create(),
).create()
Car(numberplate="213", mark="dsaas", owner=user1, letter2=letter2).create()

result = Car.get(id=1)
print(result)

# TODO: на гх залить
