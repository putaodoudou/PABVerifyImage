#!/usr/bin/python
# coding utf8
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
import sys
import os
import sqlite3
import cPickle
import cv2
import warnings
import dataprocess as dp

warnings.filterwarnings("ignore")


def getdatabyid(idx):
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data,label1 from pic_table where id =%d''' % idx
    print sql
    cur = conn.cursor()
    cur.execute(sql)
    data = cur.fetchall()
    conn.close()
    return data[0]


def showpredicpic(idx, model):
    pic_data, label1 = getdatabyid(idx)
    print "id:%s label1====>%s" % (idx, label1)
    img = dp.pm(pic_data)
    xi = dp.pm3(dp.pm2(img))
    yi = model.predict(xi)[0]
    if int(yi) >= 10:
        yi = chr(yi + 55)
    print "id:%s pridict===>%s" % (idx, yi)
    cv2.namedWindow(str(yi), 0)
    cv2.resizeWindow(str(yi), 400, 400)
    cv2.moveWindow(str(yi), 400, 200)
    cv2.imshow(str(yi), img)
    cv2.waitKey(1500)
    cv2.destroyAllWindows()
    return yi


def showpredicbyfile(filename, model):
    data = dp.splitimg(filename)
    label = ''
    for i in data:
        x = dp.pm3(dp.pm2(i))
        yi = model.predict(x)[0]
        if int(yi) >= 10:
            yi = chr(yi + 55)
        label = label + str(yi)
    img = cv2.imread(filename)
    cv2.namedWindow(label, 0)
    cv2.resizeWindow(label, 400, 400)
    cv2.moveWindow(label, 400, 200)
    cv2.imshow(label, img)
    cv2.waitKey(1500)
    cv2.destroyAllWindows()
    return label


def trainmodel():
    conn = sqlite3.connect('picdata')
    sql = '''select pic_data,label2 from pic_table where label2 is not null'''
    cur = conn.cursor()
    cur.execute(sql)
    pic_data = cur.fetchall()
    conn.close()
    d = []
    t = []
    for k, v in pic_data:
        d.append(k)
        t.append(v)
    d = map(dp.procRGB2Data, d)
    t = map(lambda x: int(x), t)
    rf_model = RandomForestClassifier(n_estimators=100)
    rf_model.fit(d, t)
    svc_model = SVC(C=3)
    svc_model.fit(d, t)
    model = rf_model
    ty = model.predict(d)
    # con_matrix = confusion_matrix(t, ty)
    # classify_report = metrics.classification_report(t, ty)
    conn = sqlite3.connect('picdata')
    for idx in range(len(ty)):
        if ty[idx] >= 10:
            label3 = chr(55 + ty[idx])
        else:
            label3 = str(ty[idx])
        sql = '''update pic_table set label3 ='%s' where id = %d''' % (label3, idx + 1)
        conn.execute(sql)
    conn.commit()
    conn.close()
    return model

if __name__ == '__main__':
    if len(sys.argv) > 2:
        inx, iny = int(sys.argv[1]), int(sys.argv[2])
    else:
        inx, iny = 100, 101
    if os.path.exists('model.data'):
        pic_model = cPickle.load(open('model.data', 'r'))
    else:
        pic_model = trainmodel()
        cPickle.dump(pic_model, open('model.data', 'w'))
    for ii in range(inx, iny):
        # showpredicpic(ii, pic_model)
        filename = './pic/%08d.jpg' % ii
        piclabel = showpredicbyfile(filename, pic_model)
        print("%s====>%s" % (filename, piclabel))
