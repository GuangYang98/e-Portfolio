# -*- coding:utf-8-*-
import json
import requests
import numpy as np
import csv
import urllib.request
from random import randint
import random

# related link
getItem33 = 
getWord34 = 
filename = 

# get csv data
def get_csv_data(filename):
    code = []
    csv_item = csv.reader(open(filename, 'rt'))
    for col in csv_item:
        code.append(col[0])
    return code

# get item recommendation
def getItem(getItem33, u):
    headers = {'content-type': "application/json"}
    pagesz = randint(1, 20)
    for id in [2,1]:
        body = {"app_id": "ma", "app_key": "mN7gLpa==", "school_id": "anhui_heifei_liuzhong","grade_name": "gz2017", "point_code": u, "scene_id": id, "page": 0, "page_size": pagesz}
        r = requests.post(getItem33, data=json.dumps(body), headers=headers)
        rjs = json.loads(r.text)
        itemid = []
        sum = rjs['total']
        if sum < pagesz:
            realcount = sum
        else:
            realcount = pagesz

        for i in rjs['items']:
            itemid.append(i['item_id'])

        # get some itemid
        pagesz2 = randint(1, realcount)
        itemid2 = random.sample(itemid, pagesz2)
    return realcount, itemid,pagesz2,itemid2

def getWord(getWord34, itemid2,u):
    headers = {'content-type': "application/json"}
    body = {"app_id": "mars","app_key": "mN7gXE9w==","grade_name": "gz2017","school_id": "anhui_heifei_liuzhong","point_code": u,"actual_recommend": itemid2}
    r = requests.post(getWord34, data=json.dumps(body), headers=headers)
    rjs = json.loads(r.text)
    word = rjs['file_url']
    return word

code=get_csv_data(filename)
for u in code:
    realcount, itemid, pagesz2, itemid2 = getItem(getItem33, u)
    try:
        word = getWord(getWord34, itemid2,u)
        print(realcount, itemid, pagesz2, itemid2, word)
    except:
        print ("badcase:"+ u + ";"+ realcount, itemid, pagesz2, itemid2)

