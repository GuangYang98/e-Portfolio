# -*- coding:utf-8-*-
import base64
import json
import requests
import cv2
import numpy as np
import binascii
import csv
import pymysql
import datetime
import time
import threading

# connect database
host_ = 
database_ = 
username_ = 
password_ = 

# related link
fzlog = 
searchreq = 
coodntreq = 
filename = 

sess = requests.session()
db = pymysql.connect(user=username_, password=password_, host=host_, database=database_)
headers = {'content-type': "application/json"}

class url_request():
    times = []
    error = []
    def req(self, coodntreq, resultJson):
        headers = {'content-type': "application/json"}
        myreq=url_request()
        r=requests.post(coodntreq, headers=headers, data=resultJson)
        rst=json.loads(r.text)
        ResponseTime = float(r.elapsed.microseconds)/1000 #get response time,ms
        myreq.times.append(ResponseTime)
        if r.status_code != 200:
            myreq.times.append("0")

# get csv data
def get_csv_data(filename):
    itemid = []
    csv_item = csv.reader(open(filename, 'rt'))
    for col in csv_item:
        itemid.append(col[0])
    return itemid

# login in FZ
def login(fzlog):
    headers = {'content-type': "application/json"}
    body = {"username": "", "pwd": ""}
    login_response = sess.post(fzlog, data=json.dumps(body), headers=headers)
    return login_response

# get page dbdata
def get_page(book_id, no):  # get dbdata
    cursor = db.cursor()
    cursor.execute("SELECT url FROM page WHERE book_id = " + str(book_id) + " AND no = " + str(no))
    dbdata = cursor.fetchone()
    return dbdata

if __name__ == '__main__':
    id= get_csv_data(filename)
    res = login(fzlog)
    ThinkTime = 0.5
    fail = []
    for it in id:
        flag = 0  # 标志本数据是否可用
        response = sess.get(url=searchreq + it)
        jsonload = json.loads(response.text)
        book_id = jsonload['data']['book_id']
        print(json.loads(response.text))

        resultJson = {}
        resultJson['regions'] = {};  # add regionsw m
        resultJson['img'] = [];  # add regions

        try:
            region_struct_content = jsonload['data']['region_struct']['content']  # array题干源
            region_struct_questions = jsonload['data']['region_struct']['questions']  # array小题
        except:
            print(it, '没有题干源！')
            fail.append(it)
            flag = 1
            continue

        region_img_content = jsonload['data']['region_img']['content']  # array:图片源
        num = 0
        for i in region_struct_content:  # i == content[n]
            page_no = i['no']
            coord = i['coordinate']  # get coordinates in content
            # =coord  #
            temp = {}
            temp['x'] = coord['x']
            temp['y'] = coord['y']
            temp['width'] = coord['width']
            temp['height'] = coord['height']
            temp['page_no'] = str(page_no)
            resultJson['regions'][str(num)] = {}
            resultJson['regions'][str(num)]['answer_type'] = 1
            resultJson['regions'][str(num)]['coordinate'] = []
            resultJson['regions'][str(num)]['coordinate'].append(temp)
            num = num + 1

        for i in region_struct_questions:  # i == content[n]
            questions_content = i['content']
            for j in questions_content:
                page_no = j['no']
                coord = j['coordinate']  # get coordinates in content
                # =coord  #
                temp = {}
                temp['x'] = coord['x']
                temp['y'] = coord['y']
                temp['width'] = coord['width']
                temp['height'] = coord['height']
                temp['page_no'] = str(page_no)

                resultJson['regions'][str(num)] = {}
                resultJson['regions'][str(num)]['answer_type'] = 1
                resultJson['regions'][str(num)]['coordinate'] = []
                resultJson['regions'][str(num)]['coordinate'].append(temp)
                num = num + 1

        for i in region_img_content:  # i == content[n]
            page_no = i['no']
            page = get_page(book_id, page_no)
            if page is None:
                print(it, '没有page！')
                fail.append(it)
                flag = 1
                break
            else:
                image_url = "" + page[0]
            coord = i['coordinate']  # get coordinates in content
            temp = {}
            temp['x'] = coord['x']
            temp['y'] = coord['y']
            temp['width'] = coord['width']
            temp['height'] = coord['height']
            temp['page_no'] = str(page_no)
            temp['page_url'] = image_url
            resultJson['img'].append(temp)

        if flag == 0:
            try:
                myreq = url_request()
                threads = []
                starttime = datetime.datetime.now()
                print("request start time %s" % starttime)
                nub = 40
                for i in range(1, nub + 1):
                    t = threading.Thread(target=myreq.req, args=(coodntreq, json.dumps(resultJson)))
                    threads.append(t)
                for t in threads:
                    time.sleep(ThinkTime)
                    print ("thread %s" %t) #print thread
                    t.setDaemon(True)
                    t.start()
                t.join()
                endtime = datetime.datetime.now()
                print("request end time %s" % endtime)
                time.sleep(3)
                AverageTime = "{:.3f}".format(float(sum(myreq.times)))  # 计算数组的平均值，保留三位小数
                print("Average Response Time %s ms" % AverageTime)
                usetime = str(endtime - starttime)
                hour = usetime.split(':').pop(0)
                minute = usetime.split(':').pop(1)
                second = usetime.split(':').pop(2)
                totaltime = float(hour) * 60 * 60 + float(minute) * 60 + float(second)

                print("concurrent processing %s" % nub)
                print("use total time %s s" % (totaltime - float(nub * ThinkTime)))
                print("fail request %s" % myreq.error.count("0"))

            except:
                print(it, 'no data！')
                print('final:',json.loads(rst.text))
                continue
