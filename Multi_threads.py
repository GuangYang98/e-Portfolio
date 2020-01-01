#!/usr/bin/python3
# -*- coding: UTF-8 -*-
import re
from io import BytesIO
from queue import Queue
import pymysql
import requests
from PIL import Image
import threading
import queue
import json
import time

def databaseconct():
    host_ = 
    database_ = 
    port_ = 3306
    username_ = 
    password_ = 
    db = pymysql.connect(user=username_, password=password_, host=host_, database=database_, port=port_)
    cursor = db.cursor()
    return cursor

#用过访问url得到图片大小-->此处耗时较大
def measurementHW(Url: object) -> object:
    response = requests.get(Url)
    response = response.content
    BytesIOObj = BytesIO()
    BytesIOObj.write(response)
    img = Image.open(BytesIOObj)
    return img.width, img.height

#写线程，便于读写分开
class writeThread(threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        global writenum
        print("开始线程：" + self.name)
        #先让文件一直处于打开状态，且类型为a，追加数据，可以加快io进程
        writer1 = open(r"C:\Users\admin\Desktop\badUrl.txt", 'a')
        writer2 = open(r"C:\Users\admin\Desktop\badCase.txt", 'a')
        writer3 = open(r"C:\Users\admin\Desktop\Gap.txt", 'a')
        writer4 = open(r"C:\Users\admin\Desktop\result.txt", 'a')
        while not exitwriteFlag or not writeQueue.empty():
            writeLock.acquire()   #在写线程互斥锁中包含的数据均为if，加快处理速度
            if not writeQueue.empty():
                case, item, list = self.q.get()
                writeLock.release()
                writenum = writenum + 1
                if case == 1:
                    wr = writer1
                    wr.write(str(item) + '\n')
                    #wr.flush()  #缓冲机制，可以在运营过程中看到数据变化，缺点是减缓速度
                    #print("badUrl:", item)  #测试数据
                elif case == 2:
                    wr = writer2
                    wr.write(str(item) + '\n')
                    #wr.flush()
                    #print("badCase:", item)
                elif case == 3:
                    wr = writer3
                    wr.write(list + '\n')
                    #wr.flush()
                    #print("Gap:", list)
                elif case == 4:
                    wr = writer4
                    wr.write(list + '\n')
                    #wr.flush()
                    #print("result:", list)
            else:
                writeLock.release()
        print("退出线程：" + self.name)
        writer1.close()
        writer2.close()
        writer3.close()
        writer4.close()

def process(item: object):
    def write(data):
        while True:
            writeLock.acquire()
            if writeQueue.full():
                writeLock.release()
            else:
                writeQueue.put(data)
                writeLock.release()
                break

    item1 = re.sub(r'\\', '', str(item[1]))    #大坑，数据既有html格式也有json格式，前者读取数据转义字符不转义，后者转义
    #width,heigh,url正则精确匹配
    groundWidth = re.findall(r'width="(\d+\.?\d*)"', item1)
    groundHeight = re.findall(r'height="(\d+\.?\d*)"', item1)
    groundUrl = re.findall(r'src="([0-9a-zA-Z\.\_\/\:\-]+[\.jpg|\.png|\.jpeg])"', item1)

    for i, url in enumerate(groundUrl):  #拼接url，异常数据的处理
        if url[:4] == "edit":
            Url = "http://" + url
        elif url[:4] == "/edi":
            Url = "http://" + url
        else:
            Url = url

        #数据比对
        try:
            width, height = measurementHW(Url)  #便于分类错误
            try:
                rate2 = round(width / height, 2)
                rate1 = float(groundWidth[i]) / float(groundHeight[i])
                distance = abs(rate1 - rate2)
                list = str([item[0], Url, rate1, rate2])
                #result:4
                print("不吃药",list)
                write((4, item[0], list))
                if distance > 0.1:#Gap:3
                    write((3, item[0], list))
            except:#badCase:2
                print("huaidongxi")
                write((2, item[0], ''))
        except:#badUrl:1
            write((1, item[0], ''))
            print("youbing:",item[0],Url,item1)


class myThread(threading.Thread):  #读取线程
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print("开始线程：" + self.name)
        while not exitFlag or not workQueue.empty():
            queueLock.acquire()   #acquire和release一对互斥锁之间夹的内容越少效率越高
            if not workQueue.empty():
                item = self.q.get()
                #print("读取：", item[0])
                queueLock.release()  #数据得到中后立马释放，加速
                process(item)
            else:
                queueLock.release()
        print("退出线程：" + self.name)


def main():
    global exitFlag, exitwriteFlag
    threads = []
    threadID = 1
    for Name in ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5"]:
        thread = myThread(threadID, Name, workQueue)
        thread.start()
        threadID += 1
        threads.append(thread)

    thread = writeThread(threadID, "Thread-write", writeQueue)
    thread.start()

    fp = open(r"C:\Users\admin\Desktop\clean4.log")
    for it in fp.readlines():  # 读取log文件中的数据
        cursor = databaseconct()
        #cursor.execute("SELECT item_id, content from item_content where item_id=" + str(it) + " AND (content LIKE '%height=""%' or content LIKE '%width%=""' or  content like '%src=%' ) AND is_deleted = 'N';")
        #由于log文件中数据有转行符但并不能被识别为行，所以需要去掉转行符
        cursor.execute("SELECT item_id, content from item_content where item_id=" + it.strip('\n') + " AND (content LIKE '%height=""%' or content LIKE '%width%=""' or  content like '%src=%' ) AND is_deleted = 'N';")
        result = cursor.fetchall()
        for item in result:
            while True:
                queueLock.acquire()
                if workQueue.full():
                    queueLock.release()
                else:
                    #print('塞数据：',item)   #测试是否有访问结果
                    workQueue.put(item)
                    queueLock.release()
                    break
    exitFlag = 1    #结束后标志变成1告知子线程可以停止工作
    for t in threads:
        t.join()
    exitwriteFlag = 1   #写入线程有缓冲机制，会延迟写入，保证数据完整，flag标志要滞后 #若用 write.flush()去除缓冲，会影响速度

if __name__ == '__main__':
    #工作子线程
    exitFlag = 0
    queueLock = threading.Lock()
    workQueue = queue.Queue(20)

    #读写线程，保证快速读数的需要，读到数据后必须马上释放，所以写的工作只能交给写线程
    exitwriteFlag = 0
    writeLock = threading.Lock()
    writeQueue = queue.Queue(20)

    writenum = 0  #用于计算数据总量（条数，非item个数）
    start = time.clock()  #计时器，用于计算优化后的代码效率

    main()# 主函数

    elapsed = (time.clock() - start)
    print("Time used:", elapsed)
    print(writenum)
