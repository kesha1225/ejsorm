from ejsorm import Ejsorm, EJModel
import datetime

db = Ejsorm("test_db.json")
db.drop()


class BaseModel(EJModel):
    __database__ = db


class User(EJModel):
    __database__ = db
    username: str


class Tweet(EJModel):
    __database__ = db
    user: User
    message: str
    created_date: datetime.datetime
    is_published: bool = True


def test_tweet():
    charlie = User.create(username="charlie")
    huey = User(username="huey")
    huey.save()

    Tweet.create(
        user=charlie, message="My first tweet", created_date=datetime.datetime.now()
    )

    User.get_one(username="charlie")

    usernames = ["charlie", "huey", "mickey"]

    users = User.get_all(username__in=usernames)

    assert len(users) == 2
    assert users[0].username == "charlie"
    assert users[1].__id == 1

    tweets = Tweet.get_all(user__in=users)
    assert len(tweets) == 1
    assert tweets[0].user.username == "charlie"
    assert tweets[0].message == "My first tweet"
    assert tweets[0].is_published

    tweets_today = Tweet.get_all(
        created_date__lte=datetime.datetime.now(), is_published=True
    )
    assert tweets_today == tweets
