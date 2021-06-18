from tkinter import messagebox
import cv2
import face_recognition
import pickle
from tkinter import *
import os


encoding_file = os.path.join(os.path.abspath('../dnn/encodings'))
knownEncodings = []
knownNames = []

name = ""
cap = cv2.VideoCapture(0)
check = False


def createFolder(directory):
    try:
        if not os.path.exists(directory):
            os.makedirs(directory)
    except OSError:
        print('Error: Creating directory' + directory)


def enc():
    count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        boxes = face_recognition.api.face_locations(rgb, model='CNN')

        encodings = face_recognition.api.face_encodings(rgb, boxes)

        for encoding in encodings:
            global check
            check = True
            global name
            print(name, encoding)
            knownEncodings.append(encoding)
            knownNames.append(name)
            count += 1

        if check is False:
            cv2.putText(frame, "Face not Found", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
            pass

        for ((top, right, bottom, left), name) in zip(boxes, knownNames):
            # rescale the face coordinates
            top = int(top)
            right = int(right)
            bottom = int(bottom)
            left = int(left)

            color = (255, 255, 0)
            cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
            y = top - 15 if top - 15 > 15 else top + 15

            ename = name + str(count) + '%'
            if count == 100:
                ename = "complete"
            cv2.putText(frame, ename, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

        cv2.imshow('encoding', frame)
        check = False

        if cv2.waitKey(1) == 13 or count == 100:
            print('Colleting Samples Complete!!!')
            break

    data = {"encodings": knownEncodings, "names": knownNames}
    createFolder('./users')
    f = open('users/' + name, "ab")
    f.write(pickle.dumps(data))
    f.close()
    cap.release()
    cv2.destroyAllWindows()


def btncmd():
    print(e.get())
    if e.get():
        global name
        name = str(e.get())
        print(name)
        enc()
        messagebox.showinfo("complete", "사용자 등록이 완료되었습니다")
    else:
        print("Error")
        messagebox.showinfo("Error", "Error")
    root.destroy()


root = Tk()
root.title("encoding")
root.geometry("300x50")

e = Entry(root, width=200,)
e.pack()
e.insert(0, "write user name")


btn = Button(root, width=200, text="insert", command=btncmd)
btn.pack()


root.mainloop()

