from typing import List

from heftydb import HeftyDB, HeftyModel


db = HeftyDB("db.json")
db.drop()


class Album(HeftyModel):
    __database__ = db

    name: str


class Genre(HeftyModel):
    __database__ = db

    title: str


class Track(HeftyModel):
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
print(Track.get_one(genres=[rock, punk])) # None

print(Track.get_one(genres__contains=punk, album__name="eee rok"))

print(Track.get_one(genres__contains=pop))
