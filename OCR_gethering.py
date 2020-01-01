# -*- coding:utf-8-*-
import base64
import json
import requests
import cv2
import numpy as np
import binascii
import csv
import pymysql

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
    body = {"username": "yangguanggroup", "pwd": "111111"}
    login_response = sess.post(fzlog, data=json.dumps(body), headers=headers)
    return login_response


# get page dbdata
def get_page(book_id, no):  # get dbdata
    cursor = db.cursor()
    cursor.execute("SELECT url FROM page WHERE book_id = " + str(book_id) + " AND no = " + str(no))
    dbdata = cursor.fetchone()
    return dbdata


# save img as png
def bs64trf(img):
    data = base64.b64decode(img)
    # show in new window
    nparr = np.fromstring(data, np.uint8)
    img_np = cv2.imdecode(nparr, cv2.COLOR_RGB2BGR)
    cv2.imshow("text", img_np)
    cv2.waitKey(0)


# get item json in FZ
def search_item(searchreq, itemid):
    respjs = []
    headers = {'content-type': "application/json"}
    fail = []
    save = []

    for it in itemid:
        flag = 0  # 标志本数据是否可用
        try:
            response = sess.get(url=searchreq + it)
            jsonload = json.loads(response.text)
            resultJson = {}
            book_id = jsonload['data']['book_id']
        except:
            try:
                response = sess.get(url=searchreq + it,headers=headers,proxies=proxies,timeout=5)
                jsonload = json.loads(response.text)
                resultJson = {}
                book_id = jsonload['data']['book_id']
                #print('backend error FZ,and need 5s'+it)
            except:
                print('backend broken')
                continue


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
                image_url = "http://wb0.cn" + page[0]
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
            body = json.dumps(resultJson)
            headers = {'content-type': "application/json"}
            try:
                rst = requests.post(coodntreq, data=body, headers=headers)
                finaljs = json.loads(rst.text)
                bs64img = finaljs['data']['img']
                print('suceess', json.loads(rst.text))
            except:
                try:
                    rst = requests.post(coodntreq, data=body, headers=headers,timeout=5)
                    finaljs = json.loads(rst.text)
                    bs64img = finaljs['data']['img']
                    #print('Zhubins api needs 5s '+it)
                except:
                    #print(it, 'no data！')
                    #print('finaljs', body)
                    continue




            # show in new window
            nparr = np.fromstring(base64.b64decode(bs64img), np.uint8)
            img_np = cv2.imdecode(nparr, cv2.COLOR_RGB2BGR)

            num = 0
            for k, v in finaljs['data']['regions'].items():  # i == content[n]
                regs = v['coordinate']  # get coordinates in content
                for i in regs:
                    # =coord  #
                    cv2.rectangle(img_np, (i['x'], i['y']), (i['x'] + i['width'] - 1, i['y'] + i['height'] - 1),
                                  (0, 255, 0), thickness=3, lineType=8)

            height, width = img_np.shape[:2]  # 获取原图像的水平方向尺寸和垂直方向尺寸。
            window = cv2.resize(img_np, (int(0.25 * width), int(0.25 * height)), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(r'C:\Users\admin\Desktop\zb_July_co\\' + str(it) + '.png',window)

                #cv2.imshow("item_id" + str(it), window)
                #keycode = cv2.waitKey(0)
                #if keycode == 13:
                 #   save.append(it)
                  #  cv2.destroyAllWindows()
                   # print(save, json.dumps(resultJson))
                #cv2.destroyAllWindows()

    return resultJson, fail


res = login(fzlog)
itemid = get_csv_data(filename)
resp = search_item(searchreq, itemid)
rj, fail = search_item(searchreq, itemid)
print("broken:", fail)
# quality
# from timeit import Timer
