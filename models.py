from peewee import *

# Create a database instance that will manage the connection and
# execute queries
database = SqliteDatabase('edu.db')

# Create a base-class all our models will inherit, which defines
# the database we'll be using.
class BaseModel(Model):
    class Meta:
        database = database

class Log(BaseModel):
    id = PrimaryKeyField()
    imageText = CharField(default="")
    usrPrices = IntegerField(default=0)
    ok = CharField(default="")
    bz = CharField(default="")

    remark = CharField(default="")
    carid = CharField(default="")
    orderId = CharField(default="")
    imageurl = CharField(default="")
    studentName = CharField(default="")
    mobile = CharField(default="")
    prices = IntegerField(default=0)
    className = CharField(default="")
    deptName = CharField(default="")

if __name__ == '__main__':
  with database:
    # print(database.execute_sql("ALTER TABLE log ADD COLUMN bz VARCHAR(50) DEFAULT '';"))
    pass