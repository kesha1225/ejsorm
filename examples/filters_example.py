from typing import List

from ejsorm import Ejsorm, EJModel


db = Ejsorm("db.json")
db.drop()


