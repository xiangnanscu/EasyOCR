#!/usr/bin/python3
import requests
import re
import easyocr
import time
from models import Log, database


def find_trade_id(arr):
  for e in arr:
    if re.match(r'\d{28}$', e):
      return e
  return None


def find_amount(arr):
  for e in arr:
    if re.match(r'[一-]?\d+\.\d+$', e):
      return int(float(e[1:]))
  return None


def try_extract(text):
  text = re.sub(r'\s','',text)
  text = text.replace('|','1')
  m = re.match(r'.+[一-]?(\d+)\.\d\d[^\d].+(\d{28})', text)
  if m:
    return m.groups()
  else:
    m = re.match(r'.+(\d{28})', text)
    if m:
      return (0, m.groups()[0])



def get_token():
  r = requests.post(
      'http://36.170.93.77:14004/httplogin',
      # timeout=3000,
      json={
          'username': 'xiangnan',
          'password': 'xn123456'
      })
  return r.json()['token']


def get_by_sfzh(sfzh, token):
  r = requests.get(
      f'http://36.170.93.77:14004/system/charges/getInfobycarid/{sfzh}',
      headers={'Authorization': token})
  # print(parse(r.json()['data'][0]['imageurl']))
  return r


def write_back(data, token):
  url = "http://36.170.93.77:14004/system/charges/editorder"
  headers = {
      'Authorization': token,
  }
  payload = {
      'sfzh': data['carid'],
      'trade_id': data['remark'] if data['ok'] == 'y' else "",
      'amount': data['prices']
  }
  response = requests.request("POST", url, headers=headers, json=payload)
  return response


def main():
  with database:
    reader = easyocr.Reader([
        'ch_sim', 'en'
    ],verbose=False)  # this needs to run only once to load the model into memory
    print("ocr reader loaded.")

    def parse_trade_img(url: str):
      if not url.startswith("http"):
        return {'imageText': "", "imageurl":""}
      a = reader.readtext(url, detail=0)
      text = ''.join(a)
      m = try_extract(text)
      res = {'imageText': text}
      if m:
        res['prices'] = m[0]
        res['remark'] = m[1]
      return res

    cols = list(
        filter(lambda e: e not in ['id', 'imageText', 'ok'],
               Log._meta.columns))

    def extract_info(e):
      res = {}
      for c in cols:
        if e.get(c) is not None:
          res[c] = e.get(c)
      res['usrPrices'] = e.get('prices') or 0
      res['ok'] = 'n'
      return res

    def get_orders(token):
      url = "http://36.170.93.77:14004/system/charges/httplist?pageSize=10&pageNum=1&state2=1"
      headers = {
          'Authorization': token,
      }
      response = requests.request("GET", url, headers=headers)

      d = response.json()
      print("总任务数量:", d['total'])
      if d.get("code") == 200 and len(d.get("rows") or []) > 0:
        return [extract_info(e) for e in d['rows']]
      else:
        return []

    def work():
      token = get_token()
      print(f'总解析数量：{Log.select().count()}')
      max_n = 100000
      n = 0
      stop = 0
      already = {}
      while 1:
        if stop:
          break
        time.sleep(10)
        tasks = get_orders(token)
        if len(tasks) == 0:
          print("此轮已全部处理完")
          continue
        print(f"获取到{len(tasks)}个任务")
        for task in tasks:
          if n > max_n:
            stop = 1
            break
          n = n + 1
          print(f'处理第{n}张图片')
          try:
            if already.get(task['orderId']):
              print("已解析：", task)
              continue
          except Exception as e:
            print("查询出错：", e)
            continue
          try:
            ret = parse_trade_img(task['imageurl'])
            if ret.get('remark') is None:
              print("解析失败：", task['imageurl'], ret['imageText'])
              ret['prices'] = task.get('prices') or 0
            else:
              ret['ok'] = 'y'
          except Exception as e:
            print("orc错误：", e, task)
            continue
          data = {**task, **ret}
          if data['prices'] == 0:
            data['prices'] = task.get('prices') or 0
          # print("data", data)
          try:
            resp = write_back(data, token)
            d = resp.json()
            if d.get('code') == 500:
              print("回写反馈失败:", data)
            try:
              with database.atomic():
                data['prices_tmp'] = 0
                data['usrPrices_tmp'] = 0
                Log.create(**data)
              database.commit()
              already[data['orderId']] = 1
            except Exception as e:
              print("插入记录失败：", e, data)
          except Exception as e:
            print("回写异常:", e, data)

    work()


main()
# token = get_token()
# print(get_by_sfzh('511528201609200148', token).json())

# r = write_back({'carid':'511528201609200148', 'orderId': "4200001572202208318717629911", 'prices': 800, 'ok': 'y'}, token)
# print(r.status_code, r.json())

# a = ['H0B', '刈', '4', '', '众》0', '09:10', '全部账单', '江安县幼儿园', '一2420.00', '当前状态', '支付成功', '商品', '江安县幼儿园', '商户全称', '江安县幼儿园', '收单机构', '财付通支付科技有限公司', '支付时间', '2022年8月31日09:08:52', '支付方式', '零钱', '交易单号', '4200001548202208317912003295', '商户单号', '可在支持的商户扫码退款', 'RHGGIK-OOZPJMA - KOAR', '账单服务', '对订单有疑惑', '发起群收款']
