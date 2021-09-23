import os
import pickle
import sys
import time

import dlib
import cv2
import face_recognition
from os import listdir
from os.path import isfile, join
import threading
from PyQt5 import uic, QtCore, QtGui, QtWidgets
from PyQt5.uic import loadUi
from PyQt5.QtWidgets import QMainWindow, QMessageBox, QDialog, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QLabel, \
    QStatusBar, QToolBar, QAction, QComboBox, QFileDialog, QListWidget, QTextEdit
from PyQt5.QtCore import QCoreApplication, pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import QPixmap, QImage
import pymongo
import bcrypt
import numpy as np
data_path = 'users/'  # 사용자 파일이 저장될 기본 경로
client = pymongo.MongoClient("mongodb://pjh0903:wlsghd19@cluster0-shard-00-00.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-01.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-02.xnjn4.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas"
                             "-8epj50-shard-0&authSource=admin&retryWrites=true&w=majority")


def load_data(path):  # 리스트 파일 로드 함수
    # 폴더가 있을때 파일이 없는경우 onlyfiles 폴더를 만들지 못함
    global onlyfiles
    try:  # 폴더가 있는경우
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]  # users 폴더에 존재하는 모든 파일을 배열로 저장한다
    except OSError:  # 폴더 없는 경우 에러 메시지
        onlyfiles = []


def createFolder(directory):  # 폴더 생성 함수
    if not os.path.exists(directory):  # 해당 디렉토리가
        os.makedirs(directory)  # 디렉토리를 생성한다


def open_folder():
    # users 폴더 없을때 생성할수 있게 수정 완료
    path = os.path.realpath('users/')
    createFolder(path)
    os.startfile(path)


def gotologin():
    login = Login_Screen()
    widget.addWidget(login)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotohome():
    home = Home_Screen()
    widget.addWidget(home)
    widget.setCurrentIndex(widget.currentIndex() + 1)

def gotodetect():
    detect = Detect()
    widget.addWidget(detect)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotolocal():
    local = Local_Menu()
    widget.addWidget(local)
    widget.setCurrentIndex(widget.currentIndex() + 1)




class Home_Screen(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("home.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.pushButton_2.clicked.connect(gotolocal)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton.clicked.connect(gotologin)


class Local_Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("localmenu.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.backButton.clicked.connect(gotohome)
        self.detectButton.clicked.connect(gotodetect)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)


class Detect(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("listest.ui", self)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.AddItem()
        self.backButton.clicked.connect(gotolocal)
        self.pushButton.clicked.connect(self.seleted)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

    def AddItem(self):
        load_data(data_path)
        for data in onlyfiles:
            self.listWidget.addItem(data)

    def seleted(self):
        user = self.listWidget.currentItem().text()
        print(user)

        cam = camera(user)
        cam.exec_()


class camera(QDialog):
    def __init__(self, user):
        super().__init__()
        loadUi("local.ui", self)
        self.user = user
        self.setFixedHeight(700)
        self.setFixedWidth(800)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.backButton.clicked.connect(self.stop)
        self.start()

    def run(self):
        knownEncodings = []
        knownNames = []

        try:
            data = pickle.loads(open('users/' + self.user, "rb").read())
        except OSError:
            print('can\'t found ' + self.user)

        for encoding in data["encodings"]:
            knownEncodings.append(encoding)
            knownNames.append(self.user)

        data = {"encodings": knownEncodings, "names": knownNames}
        global running
        cap = cv2.VideoCapture(0)
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.label.resize(width, height)
        while running:
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(img, model='CNN')
                encodings = face_recognition.face_encodings(img, boxes)
                names = []
                for encoding in encodings:
                    matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.35)
                    name = 'unknown'

                    if True in matches:
                        matchesIndxs = []
                        for (i, b) in enumerate(matches):
                            if b:
                                matchesIndxs.append(i)

                        counts = {}

                        for items in matchesIndxs:
                            name = data['names'][items]
                            counts[name] = counts.get(name, 0) + 1

                        for items in matchesIndxs:
                            counts[data['names'][items]] = counts.get(data['names'][items]) + 1
                        name = max(counts, key=counts.get)
                        print(counts)
                    names.append(name)

                for ((top, right, bottom, left), name) in zip(boxes, names):
                    # rescale the face coordinates

                    color = (255, 255, 0)
                    if name == 'unknown':
                        color = (255, 255, 255)
                        # draw the predicted face name on the image
                    cv2.rectangle(img, (left, top), (right, bottom),
                                  color, 2)
                    y = top - 15 if top - 15 > 15 else top + 15
                    cv2.putText(img, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                                0.75, color, 2)

                h,w,c = img.shape
                print(h,w,c)
                qImg = QtGui.QImage(img.data, w, h, w*c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
            else:
                QtWidgets.QMessageBox.about(widget, "Error", "Cannot read frame.")
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")

    def stop(self):
        global running
        running = False
        print("stoped..")
        self.close()

    def start(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        print("started..")


class Login_Screen(QMainWindow):
    def __init__(self):
        super(Login_Screen, self).__init__()
        loadUi("login.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.pushButton_2.clicked.connect(self.gotoregister)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton.clicked.connect(self.btnClick)
        self.backButton.clicked.connect(gotohome)

    def gotoregister(self):
        reg = Reg_Screen()
        widget.addWidget(reg)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def btnClick(self):
        db = client["member"]
        collection = db["member"]
        Id = self.lineEdit.text()
        Pass = self.lineEdit_2.text()

        a = collection.find_one({"name": Id})

        pw = a["password"]
        pw = pw.encode("utf-8")
        pw_check = bcrypt.checkpw(Pass.encode("utf-8"), pw)  # 입력값과 해쉬값이 동일한지 확인
        admin_check = a['approved']  # 관리자가 승인했는지체크 bool
        admin = a['admin']

        if pw_check:
            if admin:
                print("관리자")
                QMessageBox.about(self, "Admin", "관리자로 로그인되었습니다")

            elif admin_check:
                print('로그인')
                QMessageBox.about(self, "Success", "로그인되었습니다")
            else:
                print('승인안됨')
                QMessageBox.about(self, "Warning", "관리자 승인이 되지 않은 사용자입니다")
        else:
            print("확인요망")


class Reg_Screen(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("register.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.backButton.clicked.connect(gotologin)
        self.pushButton.clicked.connect(self.register)

    def register(self):
        db = client["member"]
        collection = db["member"]
        ID = self.lineEdit.text()
        Pass = self.lineEdit_2.text()
        print(type(ID))
        print(type(Pass))
        a = collection.find_one({"name": ID})

        if a:
            QMessageBox.about(self, "Warning", "이미 존재하는 아이디 입니다.")
        else:
            Pass = bcrypt.hashpw(Pass.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

            a = collection.insert_one({"name": ID, "password": Pass, "approved": False, "admin": False})
            print(a)
            if a:
                QMessageBox.about(self, "Success", "가입 되었습니다")
                gotologin()
            else:
                QMessageBox.about(self, "Failed", "다시 진행해주세요")

        gotologin()


app = QtWidgets.QApplication(sys.argv)
home = Home_Screen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.show()
app.exec_()
