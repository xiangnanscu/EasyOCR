from flask import Flask
from flask import render_template
from flask import request
import hashlib
from models import Log, database
from peewee import fn

app = Flask(__name__)


def hash(s):
  return hashlib.md5(s.encode('utf-8')).hexdigest()


@app.before_request
def before_request():
  database.connect()
  pass


@app.after_request
def after_request(response):
  database.close()
  return response


def get_school_map():
  school_map = {}
  res = Log.select(fn.DISTINCT(Log.deptName),
                   fn.COUNT(
      Log.id).alias("cnt")).where(Log.ok == 'n').group_by(
      Log.deptName).order_by(fn.COUNT(Log.id).desc())
  for r in res:
    school_map[hash(r.deptName)] = r
  return school_map


@app.route('/not_ok')
def not_ok():
  logs = {
      r.deptName: [f'http://lzwlkj.cn:5000/logs/{hash}', r.cnt]
      for hash, r in get_school_map().items()
  }
  cnt_n = Log.select().where(Log.ok == 'n').count()
  cnt_y = Log.select().where(Log.ok == 'y').count()
  percent = str(cnt_n*100/(cnt_n+cnt_y))[:5]+'%'
  return render_template('not_ok.html', **locals())


@app.route('/logs/<hash>')
def hello_world(hash):
  logs = Log.select().where(Log.ok == 'n').where(
      Log.deptName == get_school_map()[hash].deptName).order_by(
      Log.deptName, Log.className)
  return render_template('index.html', **locals())
