import cv2
import face_recognition
import pickle
import time
import dlib
from imutils.video import FPS
from os import listdir
from os.path import isfile, join
from tkinter import *

print("[INFO] starting video stream...")
print(dlib.DLIB_USE_BLAS)
print(dlib.DLIB_USE_CUDA)
print(dlib.DLIB_USE_LAPACK)
vs = cv2.VideoCapture(0)
fps = FPS().start()

time.sleep(1.0)
scaler = 0.35
counter = 0;

root = Tk()
root.title("detect user")
root.geometry("200x210")
data_path = 'users/'

try:
    onlyfiles = [f for f in listdir(data_path) if isfile(join(data_path, f))]
except OSError:
    print('can\'t found Folder')
    exit()

list_frame = Frame(root)
list_frame.pack(fill="both")

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y")

listbox = Listbox(list_frame, selectmode="single")

for i in onlyfiles:
    listbox.insert(END, i)

listbox.pack()


def btncmd():
    global user
    i = listbox.curselection()
    num = listbox.index(i)
    user = onlyfiles[num]
    print(user)
    dec()


def dec():
    print("[INFO] loading encodings...")
    try:
        data = pickle.loads(open('users/' + user, "rb").read())
    except OSError:
        print('can\'t found ' + user)
        exit()

    while True:

        ret, image = vs.read()
        if not ret:
            break

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        rgb = cv2.resize(image, (int(image.shape[1] * scaler), int(image.shape[0] * scaler)))

        r = image.shape[1] / float(rgb.shape[1])

        boxes = face_recognition.face_locations(rgb, model='CNN')
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []  # for recognized faces

        start = time.time()

        for encoding in encodings:
            matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.3)
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
            print("time :", time.time() - start)

        for ((top, right, bottom, left), name) in zip(boxes, names):
            # rescale the face coordinates
            top = int(top * r)
            right = int(right * r)
            bottom = int(bottom * r)
            left = int(left * r)

            color = (255, 255, 0)
            if name == 'unknown':
                color = (255, 255, 255)
                # draw the predicted face name on the image
            cv2.rectangle(image, (left, top), (right, bottom),
                          color, 2)
            y = top - 15 if top - 15 > 15 else top + 15
            cv2.putText(image, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX,
                        0.75, color, 2)

        if ret:
            prev_time = time.time()
            cv2.imshow("PRESS 'q' is quit", image)
            key = cv2.waitKey(1) & 0xFF
            fps.update()

            if key == ord("q"):
                break

    fps.stop()
    print("Elapsed time: {:.2f}".format(fps.elapsed()))
    print("FPS: {:.2f}".format(fps.fps()))
    cv2.destroyAllWindows()


btn = Button(root, text="찾기", command=btncmd)
btn.pack()
root.resizable(False, False)
root.mainloop()
