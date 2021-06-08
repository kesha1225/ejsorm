from ejsorm import Ejsorm, EJModel

db = Ejsorm("db.json")
db.drop()


class Album(EJModel):
    __database__ = db

    name: str


class Track(EJModel):
    __database__ = db

    album: Album
    title: str
    position: int


# Create some records to work with.

malibu = Album.create(name="Malibu", number=1)

Track.create(album=malibu, title="The Bird", position=1)
Track.create(album=malibu, title="Heart don't stand a chance", position=2)
Track.create(album=malibu, title="The Waters", position=3)

# year = Year.create(number=2010, v=False, db=db)
# date = Date.create(day=31, month=1, year=year, db=db)

fantasies = Album.create(name="Fantasies", number=2)

Track.create(album=fantasies, title="Help I'm Alive", position=1)
Track.create(album=fantasies, title="Sick Muse", position=2)
# сделать везде поле __айди и в него пихать иначе никак

# Fetch an instance, without loading a foreign key relationship on it.


track = Track.get_one(title="The Bird")
print(track)
tracks = Track.get_all(album__name="Fantasies").order_by(Track.position, order_type="DESC")
print(tracks)
