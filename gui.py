import os
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
    QStatusBar, QToolBar, QAction, QComboBox, QFileDialog
from PyQt5.QtCore import QCoreApplication, pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import QPixmap, QImage
import pymongo
import bcrypt
import numpy as np

client = pymongo.MongoClient("mongodb://pjh0903:wlsghd19@cluster0-shard-00-00.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-01.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-02.xnjn4.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas"
                             "-8epj50-shard-0&authSource=admin&retryWrites=true&w=majority")


def gotologin():
    login = Login_Screen()
    widget.addWidget(login)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotohome():
    home = Home_Screen()
    widget.addWidget(home)
    widget.setCurrentIndex(widget.currentIndex() + 1)

def gotodetect():
    detect = list_test()
    widget.addWidget(detect)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotolocal():
    local = Local_Menu()
    widget.addWidget(local)
    widget.setCurrentIndex(widget.currentIndex() + 1)



class Home_Screen(QDialog):
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


class Local_Menu(QDialog):
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


class list_test(QDialog):
    def __init__(self):
        super.__init__()
        loadUi("listest.ui", self)
        self.listWidget.item

    def insertListWidget(self):



class Login_Screen(QDialog):
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


class Reg_Screen(QDialog):
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
            else:
                QMessageBox.about(self, "Failed", "다시 진행해주세요")

        gotologin()


app = QtWidgets.QApplication(sys.argv)
home = Home_Screen()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.show()
app.exec_()
