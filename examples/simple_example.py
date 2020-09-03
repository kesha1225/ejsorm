from heftydb import HeftyDB, HeftyModel

db = HeftyDB("db.json")
db.drop()


# TODO: макс лен для строк например

class Year(HeftyModel):
    number: int
    v: bool


class Date(HeftyModel):
    day: int
    month: int
    year: Year


class Album(HeftyModel):
    name: str
    date: Date


class Track(HeftyModel):
    album: Album
    title: str
    position: int


# TODO мб убрать передачу дб и сделать метадату в классах
# Create some records to work with.
# malibu = Album.create(db=db, name="Malibu", date=Date(day=1, month=2, year=Year(number=2020, v=True))) так не пашет

year = Year.create(number=2020, v=True, db=db)

date = Date.create(day=1, month=2, year=year, db=db)
malibu = Album.create(db=db, name="Malibu", date=date)

Track.create(album=malibu, title="The Bird", position=1, db=db)
Track.create(album=malibu, title="Heart don't stand a chance", position=2, db=db)
Track.create(album=malibu, title="The Waters", position=3, db=db)

year = Year.create(number=2010, v=False, db=db)
date = Date.create(day=31, month=1, year=year, db=db)

fantasies = Album.create(name="Fantasies", db=db, date=date)

Track.create(album=fantasies, title="Help I'm Alive", position=1, db=db)
Track.create(album=fantasies, title="Sick Muse", position=2, db=db)
# сделать везде поле __айди и в него пихать иначе никак

# Fetch an instance, without loading a foreign key relationship on it.


tracks = Track.get_all(album__date__year__number=2020, db=db)

print(tracks)
