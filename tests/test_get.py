from heftydb import HeftyDB, HeftyModel


db = HeftyDB("test_db.json")
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


def test_get():
    track = Track.get_one(title="The Bird")
    assert track.album.name == "Malibu"
    assert track.album.pk == 0

    track = Track.get_one(title="The Bird")
    assert track.album.name == "Malibu"
    assert track.title == "The Bird"
    assert track.position == 1

    tracks = Track.get_all(album__name="Fantasies")
    assert len(tracks) == 2
    assert tracks[0].title == "Help I'm Alive"
    assert tracks[1].position == 2
    assert tracks[1].album == Album(name='Fantasies', __id=1)

    tracks = Track.get_all(album__name__iexact="fantasies")
    assert len(tracks) == 2

    tracks = Track.get_all()
    assert len(tracks) == 5
    assert tracks[-1].title == "Sick Muse"
    assert tracks[-2].pk == 3
    assert tracks[-3].album.name == "Malibu"
