# HeftyDB

База данных (по совместительству orm) для json.


Примеры - [/examples](https://github.com/kesha1225/HeftyDB/tree/master/examples)

```python
from heftydb import HeftyDB, HeftyModel

db = HeftyDB("db.json")
db.drop()


class Album(HeftyModel):
    __database__ = db

    name: str


class Track(HeftyModel):
    __database__ = db

    album: Album
    title: str
    position: int


malibu = Album.create(name="Malibu")
Track.create(album=malibu, title="The Bird", position=1)
Track.create(album=malibu, title="Heart don't stand a chance", position=2)
Track.create(album=malibu, title="The Waters", position=3)

fantasies = Album.create(name="Fantasies")
Track.create(album=fantasies, title="Help I'm Alive", position=1)
Track.create(album=fantasies, title="Sick Muse", position=2)


# Fetch an instance, without loading a foreign key relationship on it.
track = Track.get_one(title="The Bird")

# We have an album instance, but it only has the primary key populated
print(track.album)       # Album(name='Malibu' __id=0) [sparse]
print(track.album.pk)    # 1


# Load the relationship from the database

assert track.album.name == "Malibu"

# This time, fetch an instance, loading the foreign key relationship.
track = Track.get_one(title="The Bird")

assert track.album.name == "Malibu"

# Fetch instances, with a filter across an FK relationship.
tracks = Track.get_all(album__name="Fantasies")
assert len(tracks) == 2

# Fetch instances, with a filter and operator across an FK relationship.
tracks = Track.get_all(album__name__iexact="fantasies")
assert len(tracks) == 2

```