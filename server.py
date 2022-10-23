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
  res_n = Log.select(fn.DISTINCT(Log.deptName),
                   fn.COUNT(
      Log.id).alias("cnt")).where(Log.ok == 'n').group_by(
      Log.deptName).order_by(fn.COUNT(Log.id).desc())
  res_all = Log.select(fn.DISTINCT(Log.deptName),
                   fn.COUNT(
      Log.id).alias("cnt")).group_by(
      Log.deptName).order_by(fn.COUNT(Log.id).desc())
  cnt_map = {hash(r.deptName): r.cnt for r in res_all}
  for r in res_n:
    k = hash(r.deptName)
    school_map[k] = r
    r.cnt_all = cnt_map.get(k) or 0

  return school_map


@app.route('/not_ok')
def not_ok():
  logs = {
      r.deptName: [f'http://lzwlkj.cn:5000/logs/{hash}', r.cnt, r.cnt_all]
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
