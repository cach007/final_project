import pickle
from os import listdir
from os.path import isfile, join

import cv2
import threading
import sys

import face_recognition
from PyQt5 import QtWidgets
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5.QtWidgets import QDialog
from PyQt5.uic import loadUi

running = False
data_path = 'users/'  # 사용자 파일이 저장될 기본 경로


def load_data(path):  # 리스트 파일 로드 함수
    # 폴더가 있을때 파일이 없는경우 onlyfiles 폴더를 만들지 못함
    global onlyfiles
    try:  # 폴더가 있는경우
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]  # users 폴더에 존재하는 모든 파일을 배열로 저장한다
    except OSError:  # 폴더 없는 경우 에러 메시지
        onlyfiles = []


# 일단 얼굴 인식

class camera(QDialog):
    def __init__(self):
        super().__init__()
        loadUi("local.ui", self)
        self.setFixedWidth(800)
        self.setFixedHeight(700)
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)
        self.start()

    def __del__(self):
        self.onExit()
        print("소멸자")

    def run(self):
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

    def start(self):
        global running
        running = True
        th = threading.Thread(target=self.run)
        th.start()
        print("started..")

    def onExit(self):
        print("exit")
        self.stop()


app = QtWidgets.QApplication([])
home = camera()
widget = QtWidgets.QStackedWidget()
widget.addWidget(home)
widget.show()


sys.exit(app.exec_())
