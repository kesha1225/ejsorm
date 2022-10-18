from typing import Optional

from ejsorm import EJModel, EJ


class User(EJModel, table="user"):
    name: str


class A:
    test: int


# default table name = Car


class Car(EJModel):
    numberplate: str
    mark: str
    owner: Optional[User]


db = EJ()
db.init_models(User, Car)
db.drop()

me = User(name="kolya").create()
# print(me.id)

my_shoha = Car(numberplate="о001оо", mark="lada", owner=me)
my_shoha.create()

# print(my_shoha.id, my_shoha.owner, my_shoha.numberplate)
# TODO: find

User(name="test1").create()
User(name="test234").create()
Car(numberplate="о002оо", mark="makr").create()
Car(numberplate="о003оо", mark="makr", owner=User(name="owneruser").create()).create()

target_user = User.get(name="2")
print(target_user)
target_car = Car.get(numberplate="о001оо", owner=2)
print(target_car)
