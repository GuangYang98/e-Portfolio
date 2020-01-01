# -*- coding:utf-8-*-
import base64
import json
import requests
import cv2
import numpy as np
import binascii
import csv
import pymysql

# connect biaozhuQA database
host_ = 
database_ = 
username_ = 
password_ = 
biaozhuqa = pymysql.connect(user=username_, password=password_, host=host_, database=database_)


# connect matrixshengchan database
mhost_ = 
mdatabase_ = 
musername_ = 
mpassword_ = 
matrixshengchan = pymysql.connect(user=musername_, password=mpassword_, host=mhost_, database=mdatabase_)


filename = r"C:\Users\admin\Desktop\test2.csv"
# get csv data
def get_csv_data(filename):
    itemid = []
    csv_item = csv.reader(open(filename, 'rt'))
    for col in csv_item:
        itemid.append(col[0])
    return itemid



# get biaozhu data
def biaozhu(itemid):
    cursor = biaozhuqa.cursor()
    cursor.execute("SELECT l4_answers_base,main_point_id FROM kp_final_marks WHERE qid = " + str(itemid))
    bzdata,bzpoint = cursor.fetchone()
    return bzdata,bzpoint


# get matrix data
def matrix(itemid):
    cursor = matrixshengchan.cursor()
    cursor.execute("SELECT point_id FROM item_point WHERE item_id = " + str(itemid))
    matrixdata = cursor.fetchone()
    return matrixdata


def main():
    itemid = get_csv_data(filename)
    badcase=[]
    num=0
    for item in itemid:
        bzdata,bzpoint= biaozhu(item)
        matrixdata = matrix(item)
        #print (item,bzdata,bzpoint,matrixdata)

        if matrixdata is None:
            print(item, bzdata)
            continue
        elif bzdata == str(matrixdata[0]):
            print(item, bzdata, bzpoint, str(matrixdata[0]))
        else:
            badcase.append(item)
            num=num+1
            print(item, bzdata, str(matrixdata[0]))
            print (num)



if __name__ == '__main__':
    main()
