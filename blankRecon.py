# -*- coding:utf-8-*-
import base64
import json
import requests
import cv2
import numpy as np
import binascii
import csv
import urllib.request

# related link
blank_recog = 
filename = r"C:\Users\admin\.csv"


# get csv data
def get_csv_data(filename):
    pageurl = []
    pagelist = csv.reader(open(filename, 'rt'))
    for col in pagelist:
        pageurl.append(col)
    return pageurl


# get item json in FZ
def main():
    pageurl = get_csv_data(filename)
    num = 1
    for url in pageurl:
        if url[0][0] == '/':
            body = {"img_url": "http://wbarn100.cn" + str(url[0])}
        else:
            body = {"img_url": "http://wbn100.cn/" + str(url[0])}
        headers = {'content-type': "application/json"}
        try:
            response = urllib.request.urlopen(body['img_url'])
            pgurl = np.asarray(bytearray(response.read()), dtype="uint8")
            # cv2.imdecode()函数将数据解码成Opencv图像格式
            image = cv2.imdecode(pgurl, cv2.IMREAD_COLOR)
            r = requests.post(blank_recog, data=json.dumps(body), headers=headers)
            rjs = json.loads(r.text)
            for i in rjs['data']['regions']:
                # =coord  #
                cv2.rectangle(image, (i['x'], i['y']), (i['x'] + i['width'] - 1, i['y'] + i['height'] - 1),
                              (0, 255, 0), thickness=2, lineType=8)
            height, width = image.shape[:2]  # 获取原图像的水平方向尺寸和垂直方向尺寸。
            window = cv2.resize(image, (int(1 * width), int(1 * height)), interpolation=cv2.INTER_CUBIC)
            cv2.imwrite(r"C:\Users\admin\Desktop\z\" + str(num) + ".png", window)
            num = num + 1
        except:
            num = num + 1
            print("badcase: ", url[0])
            continue


if __name__ == '__main__':
    main()
