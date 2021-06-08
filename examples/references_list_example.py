from typing import List

from ejsorm import Ejsorm, EJModel


db = Ejsorm("db.json")
db.drop()


class Album(EJModel):
    __database__ = db

    name: str


class Genre(EJModel):
    __database__ = db

    title: str


class Track(EJModel):
    __database__ = db

    album: Album
    title: str
    position: int
    genres: List[Genre]


rock = Genre.create(title="Rock")
pop = Genre.create(title="pop")
punk = Genre.create(title="punk")

album = Album.create(name="eee rok")

track = Track.create(album=album, title="rok pesnya)", position=1, genres=[rock])
track2 = Track.create(album=album, title="все жанры", position=1, genres=[rock, punk])

# we can add element in list
track2.genres.add(pop)


print(Track.get_all())
print(Track.get_one(genres=[rock, punk]))  # None

print(Track.get_one(genres__contains=punk, album__name="eee rok"))

print(Track.get_one(genres__contains=pop))
