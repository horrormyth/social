from peewee import Model, SqliteDatabase

sql_db = SqliteDatabase('awp_social.db')


class BaseModel(Model):
    class Meta:
        database = sql_db
