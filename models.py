__author__ = 'devndraghimire'

import datetime
from flask.ext.bcrypt import generate_password_hash
from flask.ext.login import UserMixin
from peewee import *


DATABASE = SqliteDatabase('awp_social.db') #Database

class User (UserMixin, Model):
    username = CharField(unique=True)
    email = CharField(unique=True)
    password = CharField(max_length=100)
    joined_at = DateTimeField(default=datetime.datetime.now)
    is_admin = BooleanField(default=False)

    class Meta:
        database = DATABASE
        order_by =('-joined_at',) #DESCENDING DISPLAY OF THE USERS
    def get_posts(self):
        return Post.select().where(Post.user == self)
    def get_stream(self):
        return Post.select().where(
            (Post.user == self)
        )

    @classmethod  #it will create the user model instance when it runs the method
    def create_users(cls, username, email, password,admin=False):
        try:
            with DATABASE.transaction():
                cls.create(
                    username=username,
                    email =email,
                    password=generate_password_hash(password),
                    is_admin =admin
                )
        except IntegrityError:
            raise ValueError('User Already Exists')

class Post(Model):
    timestamp = DateTimeField(default=datetime.datetime.now)
    user = ForeignKeyField(
        rel_model=User,
        related_name='posts'
    )
    content = TextField()
    class Meta:
        database = DATABASE
        order_by = ('-timestamp',)#touples

def initialize():
    DATABASE.connect()
    DATABASE.create_tables([User,Post],safe=True)
    DATABASE.close()
