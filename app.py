from flask import Flask, render_template, request

from peewee import *
import datetime
import numpy

app = Flask(__name__)

db = SqliteDatabase('people.db')


# classes which we'll use

class BaseModel(Model):
    class Meta:
        database = db


class Person(BaseModel):
    id = AutoField()
    name = CharField()
    email = CharField()


class Category(BaseModel):
    id = AutoField()
    title = CharField()


class Buying(BaseModel):
    id = AutoField()
    date = DateTimeField()
    price = IntegerField()
    title = CharField(null=True)
    person = ForeignKeyField(Person, backref="buyings")  # one person has many buyings
    category = ForeignKeyField(Category, backref="buyings")  # one category has many buyings


# STATISTICS

def getGeneralStatistics(user, dateStart, dateFinish):
    temp = []
    # найдем для юзера только его покупки и только те, что соответствуют периоду - год
    for i in Buying.select().where(
            ((Buying.date <= dateFinish).bin_and(Buying.date >= dateStart).bin_and(Buying.person == user))):
        temp.append(i)

    # достанем из этого списка крайности и сумму для статистики
    maxBuying = max(temp, key=lambda item: item.price)
    minBuying = min(temp, key=lambda item: item.price)
    print('You,ve made', len(temp), ' buyings,',
          'the maximum price was', maxBuying.price, ' in category',
          maxBuying.category.title)
    print('')
    print('The minimum price was', minBuying.price, 'rubles. It was in the category ', minBuying.category.title)
    succ = 0
    mem = 0
    for i in temp:
        if (i.category.title == "preset") or (i.category.title == "course"):
            succ += i.price
        elif (i.category.title == "photoshoot") or (i.category.title == "certificat"):
            mem += i.price
    return(mem, succ)

def datahist(dateStart, dateFinish):
    dict = {}
    temp=[]
    # найдем для кажого юзера количество покупок за период (в нашем примере - год)
    #переделать поиск данных по- человечески!
    for j in Person.select():
        for i in Buying.select().where(
                ((Buying.date <= dateFinish).bin_and(Buying.date >= dateStart).bin_and(Buying.person == j))):
            temp.append(i)
        dict[j] = len(temp)
        temp = []
    return list(dict.values())


@app.route('/')
def hello_world():
    return render_template('index.html')


@app.route('/edges')
def edges():
    data = datahist(datetime.date(2020, 2, 1), datetime.date(2020, 2, 29))
    return render_template('edges.html', data = data)


@app.route('/', methods = ['POST'])
def getvalue():
    temp = []
    email = request.form['email']
    for i in Person.select().where(
            (Person.email == email)):
        temp.append(i)
    if temp == []:
        return render_template('pass.html', name='', mem= 0, succ=0)
    else:
        user = Person.get(Person.email == email)
        list = getGeneralStatistics(user, datetime.date(2020, 2, 1), datetime.date(2020, 2, 29))
        return render_template('pass.html', name = user.name, mem = list[0], succ = list[1])


if __name__ == '__main__':
    app.run()
