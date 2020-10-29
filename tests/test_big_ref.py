from heftydb import HeftyDB, HeftyModel

db = HeftyDB("test_db.json")
db.drop()


class Model1(HeftyModel):
    __database__ = db

    value: int


class Model2(HeftyModel):
    __database__ = db

    value: Model1


class Model3(HeftyModel):
    __database__ = db

    value: Model2


class Model4(HeftyModel):
    __database__ = db

    value: Model3


class Model5(HeftyModel):
    __database__ = db

    value: Model4


class Model6(HeftyModel):
    __database__ = db

    value: Model5


class Model7(HeftyModel):
    __database__ = db

    value: Model6


def test_get_long_ref():
    model1 = Model1.create(value=1)

    model2 = Model2.create(value=model1)
    model3 = Model3.create(value=model2)
    model4 = Model4.create(value=model3)
    model5 = Model5.create(value=model4)
    model6 = Model6.create(value=model5)
    model7 = Model7.create(value=model6)

    assert model4.value.value.value.value == 1
    assert model1.value == 1
    assert model7.value.value.value.value.value.value.value == 1
