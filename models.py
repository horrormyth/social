import datetime
from flask_bcrypt import generate_password_hash
from flask_login import UserMixin
from peewee import IntegrityError, ForeignKeyField, CharField, BooleanField, DateTimeField, TextField

from base_model import BaseModel, sql_db


class User(UserMixin, BaseModel):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        order_by = ('-joined_at',)

    def following(self):
        return (
            User.select().join(
                Relationship, on=Relationship.to_user
            ).where(
                Relationship.from_user == self
            )

        )

    def followers(self):
        return (
            User.select().join(
                Relationship, on=Relationship.from_user
            ).where(
                Relationship.to_user == self
            )
        )

    def get_posts(self):
        return Post.select().where(Post.user == self)

    def get_stream(self):
        return Post.select().where(
            (Post.user << self.following()) |
            (Post.user == self)
        )

    @classmethod
    def create_users(cls, username, email, password, admin=False):
        try:
            with sql_db.transaction():
                cls.create(
                    username=username,
                    email=email,
                    password=generate_password_hash(password),
                    is_admin=admin
                )
        except IntegrityError:
            raise ValueError('User Already Exists')


class Post(BaseModel):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        model=User,
        related_name='posts'
    )
    content = TextField()

    class Meta:
        order_by = ('-timestamp',)


class Relationship(BaseModel):
    from_user = ForeignKeyField(model=User, related_name='relationships')
    to_user = ForeignKeyField(model=User, related_name='related_to')

    class Meta:
        indexes = ((('from_user', 'to_user'), True),)
