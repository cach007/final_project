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
    QStatusBar, QToolBar, QAction, QComboBox, QFileDialog, QListWidget, QTextEdit, QInputDialog
from PyQt5.QtCore import QCoreApplication, pyqtSignal, pyqtSlot, Qt, QThread, QTimer
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimediaWidgets import *
from PyQt5.QtGui import QPixmap, QImage
import pymongo
import bcrypt
import numpy as np

data_path = 'users/'  # 사용자 파일이 저장될 기본 경로
Login = False
Admin = False
client = pymongo.MongoClient("mongodb://pjh0903:wlsghd19@cluster0-shard-00-00.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-01.xnjn4.mongodb.net:27017,"
                             "cluster0-shard-00-02.xnjn4.mongodb.net:27017/myFirstDatabase?ssl=true&replicaSet=atlas"
                             "-8epj50-shard-0&authSource=admin&retryWrites=true&w=majority")
user_name = 'none'
user = 'none'


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


def gotoregister():
    reg = Reg_Screen()
    widget.addWidget(reg)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotodb():
    db = DB_Download()
    widget.addWidget(db)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotoadmin():
    adm = Admin_Page()
    widget.addWidget(adm)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def gotomember():
    mbr = Member_Page()
    widget.addWidget(mbr)
    widget.setCurrentIndex(widget.currentIndex() + 1)


def loginstate():
    global Login
    Login = True


def adminstate():
    global Admin
    global Login
    Admin = True
    Login = True


def logoutstate():
    global Login
    global Admin
    Login = False
    Admin = False
    gotohome()


class Home_Screen(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("home.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.pushButton_2.clicked.connect(gotolocal)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton.clicked.connect(gotologin)
        self.pushButton_4.clicked.connect(gotomember)


class Local_Menu(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("localmenu.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.backButton.clicked.connect(gotohome)
        self.detectButton.clicked.connect(gotodetect)
        self.userButton.clicked.connect(self.gotoedit)
        self.pushButton_4.clicked.connect(gotologin)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

    def gotoedit(self):
        edit = User_Edit()
        widget.addWidget(edit)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class User_Edit(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("useredit.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.AddItem()
        self.label.setAlignment(Qt.AlignCenter)
        self.backButton.clicked.connect(gotolocal)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton_2.clicked.connect(self.Deleteuser)
        self.pushButton.clicked.connect(self.Adduser)

    def AddItem(self):
        load_data(data_path)
        for data in onlyfiles:
            self.listWidget.addItem(data)

    def Uplist(self):  # 리스트에 사용자를 추가하거나 삭제할시 리스트를 갱신해주는 함수
        self.listWidget.clear()
        load_data(data_path)
        for data in onlyfiles:
            self.listWidget.addItem(data)

    def Adduser(self):
        add = Add_User()
        widget.addWidget(add)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def Deleteuser(self):  # 사용자를 삭제하는 함수
        user = self.listWidget.currentItem().text()
        if user:
            print(user)
        else:
            QtWidgets.QMessageBox.about(widget, "Error", "삭제할 사용자를 선택하세요.")

        file = 'users/' + user

        if os.path.isfile(file):  # 선택한 파일이 존재할경우에
            response = QMessageBox.question(self, 'Message', 'Are you sure to quit?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            print(response)
            if response == QMessageBox.Yes:
                os.remove(file)  # 파일을 삭제한다
                self.Uplist()
                QtWidgets.QMessageBox.about(widget, "INFO", "파일" + user + "의 삭제가 완료 되었습니다")  # 삭제완료 메세지 박스로 알려준다
            else:
                QtWidgets.QMessageBox.about(widget, "CANCEL", "파일" + user + "의 삭제를 취소하였습니다")
        else:
            QtWidgets.QMessageBox.about(widget, "Error",
                                        "삭제할 파일이 존재하지 않습니다다")  # 파일이 존재하지 않을 경우에 메세지박스로 알려준다(정상적인 상황에서 발생할수 없는 오류)


class Add_User(QMainWindow):  # 사용자 추가 방식 고르는 페이지
    def __init__(self):
        super().__init__()
        loadUi("adduser.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.detectButton.clicked.connect(self.getname)
        self.backButton.clicked.connect(self.gotoedit)
        self.pushButton_4.clicked.connect(self.runimage)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

    def getname(self):
        cam = Get_Name()
        cam.exec_()
        print(user)
        if user != 'none':
            addcam = Add_Cam(user)
            addcam.exec_()

    def gotoedit(self):
        edit = User_Edit()
        widget.addWidget(edit)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def dest_folder(self):  # 찾아보기 버튼  파일경로읽어오기
        files = QtWidgets.QFileDialog.getExistingDirectory(self, 'select image directory')

        global select_folder  # 선택 파일 경로
        select_folder = files + '/'
        print(select_folder)

    def runimage(self):
        cam = Get_Name()
        cam.exec_()

        if user != 'none':
            self.dest_folder()
            if select_folder != '/':
                knownEncodings = []
                knownNames = []

                onlyfile = [f for f in listdir(select_folder) if isfile(join(select_folder, f))]
                for i, files in enumerate(onlyfile):
                    filename = select_folder + onlyfile[i]
                    print(filename)
                    print(onlyfile[i])
                    images = cv2.imread(filename)
                    assert images is not None, ' can\'t open file as img'

                    rgb = cv2.cvtColor(images, cv2.COLOR_BGR2RGB)
                    boxes = face_recognition.face_locations(rgb, model='CNN')
                    encodings = face_recognition.face_encodings(rgb, boxes)

                    if not boxes:  # 이미지에 얼굴이 없을겨우 종료
                        print("인식 실패")
                        QtWidgets.QMessageBox.about(widget, "Error", "식별이 안되는 이미지가 있습니다.")
                        return 0

                    for encoding in encodings:
                        knownEncodings.append(encoding)
                        knownNames.append(user)
                        print(encoding)

                data = {"encodings": knownEncodings, "names": knownNames}
                createFolder('./users')
                f = open(data_path + user, 'wb')
                print(data)
                f.write(pickle.dumps(data))
                f.close()
                QtWidgets.QMessageBox.about(widget, "INFO", "사용자 등록 완료.")


class Get_Name(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("getname.ui", self)
        self.setFixedHeight(300)
        self.setFixedHeight(200)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.pushButton_2.clicked.connect(self.close)
        self.pushButton.clicked.connect(self.getback)

    def getback(self):
        global user
        user = self.lineEdit.text()
        print(user)
        self.close()


class Add_Cam(QDialog):
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
        global check
        check = False
        global running
        cap = cv2.VideoCapture(0)
        count = 0
        width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
        height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
        self.label.resize(width, height)
        while running:
            ret, img = cap.read()
            if ret:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                boxes = face_recognition.face_locations(img, model='CNN')
                encodings = face_recognition.face_encodings(img, boxes)
                for encoding in encodings:
                    check = True
                    print(self.user, encoding)
                    knownEncodings.append(encoding)
                    knownNames.append(self.user)
                    count += 1

                if check is False:
                    cv2.putText(img, "Face not Found", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pass

                for ((top, right, bottom, left), name) in zip(boxes, knownNames):
                    # rescale the face coordinates

                    color = (255, 255, 0)
                    cv2.rectangle(img, (left, top), (right, bottom), color, 2)

                    y = top - 15 if top - 15 > 15 else top + 15

                    ename = user + str(count) + '%'
                    if count == 100:
                        ename = "complete"
                    cv2.putText(img, ename, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                h, w, c = img.shape
                print(h, w, c)
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
                check = False

                if count == 100:
                    print("collecting samples complete")
                    break
        data = {"encodings": knownEncodings, "names": knownNames}
        createFolder('./users')
        f = open('users/' + self.user, "ab")
        f.write(pickle.dumps(data))
        f.close()

        cap.release()
        print("Thread end.")
        self.stop()

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


class Choose_One(QMainWindow):
    def __init__(self, user):
        super().__init__()
        loadUi("choose.ui", self)
        self.user = user
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.detectButton.clicked.connect(self.webone)
        self.backButton.clicked.connect(self.goback)
        self.userButton.clicked.connect(self.imgone)

    def goback(self):
        back = Detect()
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def webone(self):
        cam = Camera(self.user)
        cam.camstart()
        cam.exec_()

    def imgone(self):
        image_file = QtWidgets.QFileDialog.getOpenFileName(self, 'select image')
        img = image_file[0]
        if img:
            cam = Camera(self.user, img)
            cam.imgstart()
            cam.exec_()
        else:
            pass


class Choose_All(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("choose.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.detectButton.clicked.connect(self.findall)
        self.backButton.clicked.connect(self.goback)

    def findall(self):
        find = FindAll()
        find.exec_()

    def goback(self):
        back = Detect()
        widget.addWidget(back)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class Detect(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("listest.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.AddItem()
        self.label.setAlignment(Qt.AlignCenter)
        self.backButton.clicked.connect(gotolocal)
        self.pushButton.clicked.connect(self.findone)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton_2.clicked.connect(self.findall)

    def AddItem(self):
        self.listWidget.clear()
        load_data(data_path)
        for data in onlyfiles:
            self.listWidget.addItem(data)

    def findall(self):
        all = Choose_All()
        widget.addWidget(all)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def findone(self):
        user = self.listWidget.currentItem().text()
        one = Choose_One(user)
        widget.addWidget(one)
        widget.setCurrentIndex(widget.currentIndex() + 1)


class FindAll(QDialog):     # 사용자 전체
    def __init__(self):
        super().__init__()
        loadUi("local.ui", self)
        self.setFixedHeight(700)
        self.setFixedHeight(800)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.backButton.clicked.connect(self.stop)
        self.start_all()

    def run_all(self):
        knownEncodings = []
        knownNames = []

        load_data(data_path)  # 리스트에 들어가 파일이 있는 폴더를 스캔해준다
        for i in onlyfiles:  # 리스트에 존재하는 파일 순서대로 입력
            u_data = pickle.loads(open('users/' + i, "rb").read())
            for encoding in u_data["encodings"]:
                knownEncodings.append(encoding)
                knownNames.append(i)

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

                h, w, c = img.shape
                print(h, w, c)
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
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

    def start_all(self):
        global running
        running = True
        th = threading.Thread(target=self.run_all)
        th.start()
        print("started All..")


class Camera(QDialog):
    def __init__(self, user, url):
        super().__init__()
        loadUi("local.ui", self)
        self.user = user
        self.url = url
        self.setFixedHeight(700)
        self.setFixedWidth(800)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.backButton.clicked.connect(self.stop)

    def webcam(self):
        cap = cv2.VideoCapture(0)
        self.run(cap)

    def image(self):
        img = cv2.imread(self.url)
        self.img_run(img)

    def run(self, cap):
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

                h, w, c = img.shape
                print(h, w, c)
                qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
                pixmap = QtGui.QPixmap.fromImage(qImg)
                self.label.setPixmap(pixmap)
            else:
                QtWidgets.QMessageBox.about(widget, "Error", "Cannot read frame.")
                print("cannot read frame.")
                break
        cap.release()
        print("Thread end.")

    def img_run(self, img):
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

        scaler = 0.5
        img = cv2.resize(img, (int(img.shape[1] * scaler), int(img.shape[0] * scaler)))

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

        h, w, c = img.shape
        print(h, w, c)
        qImg = QtGui.QImage(img.data, w, h, w * c, QtGui.QImage.Format_RGB888)
        pixmap = QtGui.QPixmap.fromImage(qImg)
        self.label.setPixmap(pixmap)

    def stop(self):
        global running
        running = False
        print("stoped..")
        self.close()

    def camstart(self):
        global running
        running = True
        th = threading.Thread(target=self.webcam)
        th.start()
        print("started..")

    def imgstart(self):
        global running
        running = True
        th = threading.Thread(target=self.image)
        th.start()
        print("started..")


class Login_Screen(QMainWindow):
    def __init__(self):
        super(Login_Screen, self).__init__()
        loadUi("login.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.pushButton_2.clicked.connect(gotoregister)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)
        self.pushButton.clicked.connect(self.btnClick)
        self.backButton.clicked.connect(gotohome)

    def btnClick(self):
        global user_name
        db = client["member"]
        collection = db["member"]
        Id = self.lineEdit.text()
        Pass = self.lineEdit_2.text()
        user_name = Id
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
                adminstate()
                gotoadmin()

            elif admin_check:
                print('로그인')
                QMessageBox.about(self, "Success", "로그인되었습니다")
                loginstate()
                gotomember()
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
        self.backButton.clicked.connect(gotologin)
        self.pushButton.clicked.connect(self.register)
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

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


class Admin_Page(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("adminpage.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.label.setText(user_name)
        self.label.setAlignment(Qt.AlignCenter)
        self.pushButton.clicked.connect(gotodetect)
        self.pushButton_2.clicked.connect(logoutstate)  # 로그아웃 버튼
        self.pushButton_4.clicked.connect(gotodb)  # 데이터 베이스 접근 버튼 -> 업로드 다운로드
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)


class Member_Page(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("memberpage.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.label.setText(user_name)
        self.label.setAlignment(Qt.AlignCenter)
        self.pushButton.clicked.connect(gotodetect)
        self.pushButton_2.clicked.connect(logoutstate)  # 로그아웃 버튼
        self.pushButton_4.clicked.connect(gotodb)  # 데이터 베이스 접근 버튼 -> 업로드 다운로드
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)


class DB_Download(QMainWindow):  # 로그인후 db 접근 페이지
    def __init__(self):
        super().__init__()
        loadUi("memberdb.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.db = client["test"]
        self.label.setText(user_name)
        self.label.setAlignment(Qt.AlignCenter)
        self.pushButton_2.clicked.connect(logoutstate)  # 로그아웃 버튼
        self.pushButton.clicked.connect(self.download)  # 다운로드 버튼
        self.pushButton_5.clicked.connect(self.switch)  # 업로드 버튼
        self.pushButton_4.clicked.connect(self.delete)  # db 삭제 버튼
        self.backButton.clicked.connect(self.back)
        self.listset()
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

    def listset(self):
        self.listWidget.clear()
        a = self.db.list_collection_names()
        for data in a:
            self.listWidget.addItem(data)

    def back(self):
        mem = Member_Page()
        widget.addWidget(mem)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def download(self):

        db_user = self.listWidget.currentItem().text()
        print(db_user)

        knownEncodings = []
        knownNames = []

        if db_user in listdir(data_path):
            pass

        collection = self.db[db_user]
        result = collection.find({"name": db_user},{"_id": False})

        for r in result:
            knownEncodings.append((r["128d"]))
            knownNames.append(db_user)

        data = {"encodings": knownEncodings, "names": knownNames}
        createFolder(data_path)
        f = open(data_path + db_user, 'wb')
        print(data)
        f.write(pickle.dumps(data))
        f.close()
        print(db_user + 'download 완료')

    def switch(self):
        dbup = DB_Upload()
        widget.addWidget(dbup)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def delete(self):
        user = self.listWidget.currentItem().text()
        print(user)
        collection = self.db[user]
        collection.drop()
        print(user + '삭제완료')
        self.listset()


class DB_Upload(QMainWindow):
    def __init__(self):
        super().__init__()
        loadUi("dbupload.ui", self)
        self.setFixedHeight(600)
        self.setFixedWidth(400)
        self.db = client["test"]
        self.label.setText(user_name)
        self.label.setAlignment(Qt.AlignCenter)
        self.pushButton_2.clicked.connect(logoutstate)  # 로그아웃 버튼
        self.pushButton.clicked.connect(self.upload)  # 다운로드 버튼
        self.pushButton_5.clicked.connect(self.switch)  # 업로드 버튼
        self.pushButton_4.clicked.connect(self.delete)  # db 삭제 버튼
        self.backButton.clicked.connect(self.back)
        self.listset()
        self.pushButton_3.clicked.connect(QCoreApplication.instance().quit)  # quit 버튼 (종료)

    def listset(self):
        self.listWidget.clear()
        load_data(data_path)
        for data in onlyfiles:
            self.listWidget.addItem(data)

    def back(self):
        mem = Member_Page()
        widget.addWidget(mem)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def upload(self):
        user = self.listWidget.currentItem().text()
        print(user)
        data = pickle.loads(open('users/' + user, "rb").read())
        collection = self.db[user]
        for encoding in data["encodings"]:
            collection.insert_one({"128d": list(encoding), "name": user})

        print("upload완료")

    def switch(self):   # download 로 바꿔줌
        dbdown = DB_Download()
        widget.addWidget(dbdown)
        widget.setCurrentIndex(widget.currentIndex() + 1)

    def delete(self):
        user = self.listWidget.currentItem().text()
        if user:
            print(user)
        else:
            QtWidgets.QMessageBox.about(widget, "Error", "삭제할 사용자를 선택하세요.")

        file = 'users/' + user

        if os.path.isfile(file):  # 선택한 파일이 존재할경우에
            response = QMessageBox.question(self, 'Message', 'Are you sure to delete?',
                                            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            print(response)
            if response == QMessageBox.Yes:
                os.remove(file)  # 파일을 삭제한다
                self.listset()
                QtWidgets.QMessageBox.about(widget, "INFO", "파일" + user + "의 삭제가 완료 되었습니다")  # 삭제완료 메세지 박스로 알려준다
            else:
                QtWidgets.QMessageBox.about(widget, "CANCEL", "파일" + user + "의 삭제를 취소하였습니다")
        else:
            QtWidgets.QMessageBox.about(widget, "Error",
                                        "삭제할 파일이 존재하지 않습니다다")  # 파일이 존재하지 않을 경우에 메세지박스로 알려준다(정상적인 상황에서 발생할수 없는 오류)



class Detect_Member(QMainWindow):
    def __init__(self):
        pass
    # 여기에 detect 완료된거 받아쓰기


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    home = Home_Screen()
    widget = QtWidgets.QStackedWidget()
    widget.addWidget(home)
    widget.show()
    app.exec_()
