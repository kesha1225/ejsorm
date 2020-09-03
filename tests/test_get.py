from heftydb import HeftyDB, HeftyModel


db = HeftyDB("test_db.json")
db.drop()


class Album(HeftyModel):
    name: str


class Track(HeftyModel):
    album: Album
    title: str
    position: int


malibu = Album.create(db=db, name="Malibu")
Track.create(album=malibu, title="The Bird", position=1, db=db)
Track.create(album=malibu, title="Heart don't stand a chance", position=2, db=db)
Track.create(album=malibu, title="The Waters", position=3, db=db)

fantasies = Album.create(name="Fantasies", db=db)
Track.create(album=fantasies, title="Help I'm Alive", position=1, db=db)
Track.create(album=fantasies, title="Sick Muse", position=2, db=db)


def test_get():
    track = Track.get_one(title="The Bird", db=db)
    assert track.album.name == "Malibu"
    assert track.album.pk == 0

    track = Track.get_one(title="The Bird", db=db)
    assert track.album.name == "Malibu"
    assert track.title == "The Bird"
    assert track.position == 1

    tracks = Track.get_all(album__name="Fantasies", db=db)
    assert len(tracks) == 2
    assert tracks[0].title == "Help I'm Alive"
    assert tracks[1].position == 2
    assert tracks[1].album == Album(name='Fantasies', __id=1)

    tracks = Track.get_all(album__name__iexact="fantasies", db=db)
    assert len(tracks) == 2

    tracks = Track.get_all(db=db)
    assert len(tracks) == 5
    assert tracks[-1].title == "Sick Muse"
    assert tracks[-2].pk == 3
    assert tracks[-3].album.name == "Malibu"
