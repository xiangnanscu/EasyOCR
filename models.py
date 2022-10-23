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
    usrPrices = FloatField(default=0)
    ok = CharField(default="")
    bz = CharField(default="")
    usrPrices_tmp = IntegerField(default=0)
    prices_tmp = IntegerField(default=0)

    remark = CharField(default="")
    carid = CharField(default="")
    orderId = CharField(default="")
    imageurl = CharField(default="")
    studentName = CharField(default="")
    mobile = CharField(default="")
    prices = FloatField(default=0)
    className = CharField(default="")
    deptName = CharField(default="")

if __name__ == '__main__':
  with database:
    # print(database.execute_sql("ALTER TABLE log ADD COLUMN usrPrices1 type float DEFAULT 0;"))
    # print(database.execute_sql("UPDATE log set usrPrices1 = usrPrices;"))
    # print(database.execute_sql("ALTER TABLE log rename column usrPrices to usrPrices_tmp;"))
    # print(database.execute_sql("ALTER TABLE log rename column usrPrices1 to usrPrices;"))
    pass