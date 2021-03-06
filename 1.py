import os
import pickle
from os import listdir
from os.path import isfile, join
from tkinter import *
from tkinter import filedialog, messagebox

import bcrypt
import cv2
import dlib
import face_recognition
import pymongo

# 파일 날렸다가 복구함
data_path = 'users/'  # 사용자 파일이 저장될 기본 경로
encoding_file = os.path.join(os.path.abspath('../dnn/encodings'))
select_folder = ''  # 파일 탐색 초기화
print(dlib.DLIB_USE_CUDA)  # gpu 사용 확인
scaler = 0.35  # 원할한 이용을 위하여 동영상 크기를 줄이기 위해 사용
login_check = False
DB = pickle.loads(open("DBkey", "rb").read())  # 데이터베이스 비밀번호를 담고 있는 피클 파일을 연다
client = pymongo.MongoClient(DB)
print(client)


def load_data(path):  # 리스트 파일 로드 함수
    # 폴더가 있을때 파일이 없는경우 onlyfiles 폴더를 만들지 못함
    global onlyfiles
    try:  # 폴더가 있는경우
        onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]  # users 폴더에 존재하는 모든 파일을 배열로 저장한다
    except OSError:  # 폴더 없는 경우 에러 메시지
        onlyfiles = []


root = Tk()
root.title("detect one")


def open_folder():
    # users 폴더 없을때 생성할수 있게 수정 완료
    path = os.path.realpath('users/')
    createFolder(path)
    os.startfile(path)


def login():  # 로그인기능 구현

    def check_data():

        db = client["member"]
        collection = db["member"]

        x1 = str(user_id.get())
        x2 = str(user_pw.get())
        print(x1, x2)

        print(x2)
        a = collection.find_one({"name": x1})

        pw = a["password"]
        pw = pw.encode("utf-8")
        pw_check = bcrypt.checkpw(x2.encode("utf-8"), pw)  # 입력값과 해쉬값이 동일한지 확인
        admin_check = a['approved']  # 관리자가 승인했는지체크 bool
        admin = a['admin']

        if pw_check:
            if admin:
                admin_state()
                login_state()
                messagebox.showinfo("Admin", "환영합니다 관리자님")
            elif admin_check:  # 관리자 승인이 된경우 체크
                login_state()  # 정상 로그인 상태로 변환
                messagebox.showinfo("Success", "로그인 되었습니다!!!")
            else:  # 관리자 승인이 되지 않은경우
                messagebox.showinfo("Sorry", "아직 회원가입이 승인되지 않았습니다.")

        else:  # 아이디나 비밀번호가 틀린경우
            messagebox.showwarning("Failed", "ID나 PASSWORD 를 확인해 주세요")

        user_id.delete(0, END)
        user_pw.delete(0, END)

        Login.destroy()

    def login_state():  # 로그인시 버튼 상태 변경

        menu_login.entryconfig(2, state="disabled")  # 로그인시 login 버튼 비활성화
        menu_login.entryconfig(3, state="normal")  # 로그인시 logout 버튼 활성화

        menu_file.entryconfig(3, state="normal")  # 로그인시 download 버튼 활성화
        menu_file.entryconfig(4, state="normal")  # 로그인시 edit 버튼 활성화

        global login_check
        login_check = True

    def admin_state():
        menu_admin.entryconfig(1, state="normal")

    Login = Toplevel(root)
    label_id = Label(Login, text="Username : ")
    label_id.grid(row=0, column=0)

    user_id = Entry(Login)
    user_id.grid(row=0, column=1)

    label_pw = Label(Login, text="Password : ")
    label_pw.grid(row=1, column=0)

    user_pw = Entry(Login, show="*")
    user_pw.grid(row=1, column=1)

    btn_log = Button(Login, text="Login", command=check_data)
    btn_log.grid(row=2, column=1)


def logout():  # 로그아웃 기능 함수 실행 여부를 묻고 로그인 이전으로 버튼 상태를 되돌린다
    def logout_state():
        menu_login.entryconfig(2, state="normal")
        menu_login.entryconfig(3, state="disabled")
        menu_file.entryconfig(2, state="disabled")
        menu_file.entryconfig(3, state="disabled")
        menu_file.entryconfig(4, state="disabled")
        menu_admin.entryconfig(1, state="disabled")

    response = messagebox.askyesno(title="Logout", message="정말 로그아웃 하시겠습니까?")
    if response == 1:
        logout_state()
        messagebox.showinfo("INFO", "로그아웃 되었습니다")
        global login_check
        login_check = False

    else:
        messagebox.showinfo("CANCEL", "로그아웃 되지 않았습니다")


def register():  # 회원가입 기능
    db = client["member"]
    collection = db["member"]

    def id_check():

        Id = Uname.get()

        print(Id)

        a = collection.find_one({"name": Id})

        if a:
            messagebox.showinfo(message="이미 있는 아이디")
        else:
            ask = messagebox.askyesno(message=Id + "로 가입하시겠습니까?")
            if ask == 1:
                Uname.configure(state='readonly')
                c_btn['state'] = DISABLED
                r_btn['state'] = NORMAL
            else:
                Uname.delete(0, END)

    def check_key():

        x1 = str(Uname.get())
        x2 = str(Upass.get())
        x2 = bcrypt.hashpw(x2.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        print(x1, x2)
        # 관리자 승인이 되지 못한 상태로 가입 진행됨
        a = collection.insert_one({"name": x1, "password": x2, "approved": False, "admin": False})
        print(a)
        if a:
            messagebox.showinfo("Success", "가입 되었습니다!!!")

        else:
            messagebox.showwarning("Failed", "다시 진행해주세요")

        Uname.delete(0, END)
        Upass.delete(0, END)
        Register.destroy()

    Register = Toplevel(root)
    Register.wm_attributes("-topmost", 1)
    label_name = Label(Register, text="Username : ")
    label_name.grid(row=0, column=0, padx=10, pady=10)
    label_pass = Label(Register, text="Password : ")
    label_pass.grid(row=1, column=0, padx=10, pady=10)

    Uname = Entry(Register)
    Uname.grid(row=0, column=1, padx=10, pady=10)
    Upass = Entry(Register, show="*")
    Upass.grid(row=1, column=1, padx=10, pady=10)

    c_btn = Button(Register, text="ID_check", command=id_check)
    c_btn.grid(row=2, column=0, padx=10, pady=10)

    r_btn = Button(Register, text="Register", command=check_key, state=DISABLED)
    r_btn.grid(row=2, column=1, padx=10, pady=10)


def upload_file():  # 사용자 파일을 데이터베이스에 업로드 하는 함수
    if list_name:  # 리스트에서 현재 선택한 파일 받아오기
        user = list_name()
        print(user)
        # 업로드 할 파일명이 이미 존재할 경우 자동으로 합쳐저 버리는 상황 발생
        # 합칠건지 이름을 바꿔서 업로드 할건지 선택 하는 부분 추가할것
        db = client["test"]
        a = db.list_collection_names()

        db_user = []
        for i in a:
            db_user.append(str(i))

        print(db_user)
        if user in db_user:
            # 여기에 창띄어서 계속할지 중단할지 물어봄 (이름 바로 변경하는 기능 뺌)
            response = messagebox.askyesno("warning", "db에 같은 이름의 사용자가 존재하여 \n기존파일에 추가됩니다 계속하시겠습니까?")
            if response == 1:
                pass
            else:
                messagebox.showinfo("CANCEL", "업로드를 중단하였습니다.")
                return 0
    else:
        messagebox.showwarning("Error", "업로드할 사용자를 선택하여 주세요!!!")
    try:
        data = pickle.loads(open('users/' + user, "rb").read())

    except OSError:
        print('can\'t found ' + user)

    db = client["test"]
    collection = db[user]

    for encoding in data["encodings"]:
        collection.insert_one({"128d": list(encoding), "name": user})

    messagebox.showinfo("INFO", user + " 의 데이터 업로드 완료!!")


def download_file():

    db = client["test"]
    a = db.list_collection_names()

    def list_set():
        list_box.delete(0, END)
        for i in a:
            val = str(i)
            list_box.insert(END, val)

    def list_user():
        if list_box.curselection():
            i = list_box.curselection()
            num = list_box.index(i)
            user = a[num]
            return user
        else:
            return ''

    def download():
        knownEncodings = []
        knownNames = []

        db_user = list_user()

        if db_user in listdir(data_path):
            response = messagebox.askyesno("warning", "컴퓨터에 같은 이름의 사용자가 존재 합니다 \n덮어쓰시겠습니까?")
            if response == 1:
                pass
            else:
                messagebox.showinfo("CANCEL", "다운로드 취소.")
                return 0

        collection = db[db_user]

        result = collection.find({"name": db_user}, {"_id": False})

        for r in result:
            knownEncodings.append(r["128d"])
            knownNames.append(db_user)

        data = {"encodings": knownEncodings, "names": knownNames}
        createFolder(data_path)
        f = open(data_path + db_user, 'wb')
        print(data)
        f.write(pickle.dumps(data))
        f.close()
        refresh_list()
        messagebox.showinfo("Complete", db_user + "데이터 다운로드 완료")

    Download = Toplevel(root)

    DL_frame = Frame(Download)
    DL_frame.pack(fill="both")

    DL_scroll = Scrollbar(DL_frame)
    DL_scroll.pack(side="right", fill="y", )

    DL_file = Listbox(DL_frame, selectmode="extended", height=8, yscrollcommand=DL_scroll.set)
    DL_file.pack(side="left", fill="both", expand=True)
    DL_scroll.config(command=DL_file.yview)

    list_box = Listbox(DL_file, selectmode="single")
    list_set()
    list_box.pack(fill="both")

    btn_frame = Frame(Download)
    btn_frame.pack(fill="both")
    down_btn = Button(btn_frame, text="사용자 다운로드", command=download, state="disable")
    down_btn.pack(fill="x")

    def refresh(event):
        selection = event.widget.curselection()
        if selection:
            down_btn['state'] = NORMAL
        else:
            pass

    Download.resizable(False, False)
    list_box.bind("<<ListboxSelect>>", refresh)


def edit_file():  # 메뉴바 File 에서 edit 버튼 누르면 실행 ( db에 저장된 사용자 정보 삭제에 이용)

    db = client["test"]
    a = db.list_collection_names()

    def list_set():
        user_box.delete(0, END)
        for i in a:
            val = str(i)
            user_box.insert(END, val)

    def list_user():
        if user_box.curselection():
            i = user_box.curselection()
            num = user_box.index(i)
            user = a[num]
            return user
        else:
            return ''

    def delete():
        db_user = list_user()
        collection = db[db_user]
        collection.drop()
        messagebox.showinfo("Complete", db_user + "데이터 삭제 완료")
        Edit_File.destroy()

    # edit 버튼 프레임
    Edit_File = Toplevel(root)

    user_frame = Frame(Edit_File)
    user_frame.pack(fill="both")

    user_scroll = Scrollbar(user_frame)
    user_scroll.pack(side="right", fill="y", )

    user_file = Listbox(user_frame, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
    user_file.pack(side="left", fill="both", expand=True)
    user_scroll.config(command=user_file.yview)

    user_box = Listbox(user_file, selectmode="single")
    list_set()
    user_box.pack(fill="both")

    btn_frame = Frame(Edit_File)
    btn_frame.pack(fill="both")
    delete_btn = Button(btn_frame, text="사용자 삭제", command=delete, stat="disable")
    delete_btn.pack(fill="x")

    def refresh(event):
        selection = event.widget.curselection()
        if selection:
            delete_btn['state'] = NORMAL
        else:
            pass

    Edit_File.resizable(False, False)
    user_box.bind("<<ListboxSelect>>", refresh)


def approval():
    db = client["member"]
    collection = db["member"]

    def list_set():  # 초기 리스트 세팅

        a = collection.find({"approved": False})
        b = collection.find({"approved": True, "admin": False})

        Unsign_file.delete(0, END)  # 승인안된 회원리스트
        signed_file.delete(0, END)  # 승인된 회원리스트

        for i in a:
            val = str(i['name'])
            Unsign_file.insert(END, val)

        for i in b:
            val = str(i['name'])
            signed_file.insert(END, val)

    def app_user():  # 승인 안된 회원 리스트에서 선택하여 승인 시켜주는 함수

        col = collection.find({"approved": False})
        if Unsign_file.curselection():
            i = Unsign_file.curselection()
            num = Unsign_file.index(i)
            sel = col[num]
            print(sel['name'])
            user = sel['name']
            collection.update({"name": user}, {"$set": {"approved": True}})
            list_set()
        else:
            pass

    def un_user():
        col = collection.find({"approved": True, "admin": False})
        if signed_file.curselection():
            i = signed_file.curselection()
            num = signed_file.index(i)
            sel = col[num]
            print(sel['name'])
            user = sel['name']
            collection.update({"name": user}, {"$set": {"approved": False}})
            list_set()
        else:
            pass

    Users = Toplevel(root)
    Users.wm_attributes("-topmost", 1)

    Unsign_frame = Frame(Users)
    Unsign_frame.pack(side="left", fill="both")
    Label(Unsign_frame, text="승인대기중인 사용자").pack(side="top")

    signed_frame = Frame(Users)
    signed_frame.pack(side="right", fill="both")
    Label(signed_frame, text="승인된 사용자").pack(side="top")

    control_frame = Frame(Users)
    control_frame.pack(fill="both")

    Unsign_scroll = Scrollbar(Unsign_frame)
    Unsign_scroll.pack(side="right", fill="y", )

    Unsign_file = Listbox(Unsign_frame, selectmode="single", height=8, yscrollcommand=Unsign_scroll.set)
    Unsign_file.pack(side="left", fill="both", expand=True)
    Unsign_scroll.config(command=Unsign_file.yview)

    signed_scroll = Scrollbar(signed_frame)
    signed_scroll.pack(side="right", fill="y", )

    signed_file = Listbox(signed_frame, selectmode="single", height=8, yscrollcommand=signed_scroll.set)
    signed_file.pack(side="left", fill="both", expand=True)
    signed_scroll.config(command=signed_file.yview)

    Label(control_frame, text="").pack(side="top")

    unsign_button = Button(control_frame, text=">", command=app_user, )
    unsign_button.pack()

    signed_button = Button(control_frame, text="<", command=un_user, )
    signed_button.pack()

    list_set()


menu = Menu(root)

# File 메뉴
menu_file = Menu(menu, tearoff=0)
menu_file.add_command(label="Open Folder", command=open_folder)
menu_file.add_separator()
menu_file.add_command(label="Upload", command=upload_file, state="disable")
menu_file.add_command(label="Download", command=download_file, state="disable")
menu_file.add_command(label="Edit", command=edit_file, state="disable")
menu.add_cascade(label="File", menu=menu_file)

# Login 메뉴
menu_login = Menu(menu, tearoff=0)
menu_login.add_command(label="Register", command=register)
menu_login.add_separator()
menu_login.add_command(label="Login", command=login, state="normal")
menu_login.add_command(label="Logout", command=logout, state="disable")
menu.add_cascade(label="User", menu=menu_login)

# 관리자 메뉴
menu_admin = Menu(menu, tearoff=0)
menu_admin.add_command(label="Users", command=approval, state="disable")  # 관리자가 회원가입 승인하는 버튼
menu.add_cascade(label="Admin", menu=menu_admin)

root.config(menu=menu)
Label(root, text="실행하실 작업을 선택해주세요").pack(side="top")

file_frame1 = Frame(root)
file_frame2 = Frame(root)
file_frame1.pack(fill='both')
file_frame2.pack(fill='both')


def refresh_list():  # 리스트를 업데이트 해주는 함수 사용자 추가나 삭제시에 리스트 순서에 변화가 생기므로 계속 갱신을 해줘야함
    load_data(data_path)  # 리스트에 들어가 파일이 있는 폴더를 스캔해준다
    listbox.delete(0, END)  # 전체 리스트를 지운다
    for i in onlyfiles:  # 리스트에 존재하는 파일 순서대로 입력
        listbox.insert(END, i)


def createFolder(directory):  # 폴더 생성 함수
    if not os.path.exists(directory):  # 해당 디렉토리가 존재 하지 않으면
        os.makedirs(directory)  # 디렉토리를 생성한다


def bt1cmd():  # 사용자 등록 버튼  선택사항 1.웹캠으로 등록 2.사진 한장으로 등록
    global check
    check = False

    def btncmd():  # 이름 입력받고 얼굴등록 함수 호출
        print(e.get())
        if e.get():
            global g_name
            g_name = str(e.get())
            print(g_name)
            e.delete(0, END)
            encoding_image(g_name)
            getName.destroy()
            global select_folder
            select_folder = ''

        else:
            print("Error")

    def encoding_image(g_name):
        print("select:" + select_folder)
        knownEncodings = []
        knownNames = []

        if select_folder == '':  # 파일 경로가 없을경우 웹캠으로 사용자 등록
            cap = cv2.VideoCapture(0)
            count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                boxes = face_recognition.face_locations(rgb, model='CNN')

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                    global check
                    check = True
                    print(g_name, encoding)
                    knownEncodings.append(encoding)
                    knownNames.append(g_name)
                    print(encoding)
                    count += 1

                if check is False:
                    cv2.putText(frame, "Face not Found", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pass

                for ((top, right, bottom, left), g_name) in zip(boxes, knownNames):
                    # rescale the face coordinates
                    top = int(top)
                    right = int(right)
                    bottom = int(bottom)
                    left = int(left)

                    color = (255, 255, 0)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    y = top - 15 if top - 15 > 15 else top + 15

                    ename = g_name + str(count) + '%'
                    if count == 100:
                        ename = "complete"
                    cv2.putText(frame, ename, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                cv2.imshow('encoding', frame)
                check = False

                if cv2.waitKey(1) == 13:
                    messagebox.showerror("Error", "사용자 등록을 중단 합니다")
                    cap.release()
                    cv2.destroyAllWindows()
                    return

                elif count == 100:
                    print('Collecting Samples Complete!!!')
                    break

            data = {"encodings": knownEncodings, "names": knownNames}
            createFolder('./users')
            f = open('users/' + g_name, "ab")
            f.write(pickle.dumps(data))
            f.close()
            cap.release()
            cv2.destroyAllWindows()

        else:  # 파일 경로가 주어져서 이미지 파일로 사용자를 등록
            txt_dest_path.delete(0, END)
            txt_dest_path.insert(END, '')
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
                    messagebox.showerror("Error", "얼굴인식에 실패했습니다. 파일을 확인해주세요")
                    return 0

                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(g_name)
                    print(encoding)

        data = {"encodings": knownEncodings, "names": knownNames}
        createFolder('./users')
        f = open(data_path + g_name, 'wb')
        print(data)
        f.write(pickle.dumps(data))
        f.close()
        refresh_list()
        print(select_folder)
        messagebox.showinfo("complete", "사용자 등록이 완료되었습니다")

    getName = Toplevel(root)  # 새 창띄워서 이름 입력받기
    label = Label(getName, text="이름을 입력하세요")
    e = Entry(getName)
    btn = Button(getName, text="사용자 등록", command=btncmd)

    label.pack()
    e.pack()
    btn.pack(fill='x')  # 사용자 등록 버튼  선택사항 1.웹캠으로 등록 2.사진 한장으로 등록


def bt2cmd():  # 사용자 탐색 버튼  선택사항 1.웹캠에서 찾기 2.주어진 이미지에서 찾기 3.영상에서 찾기
    if list_name:
        user = list_name()
        print(user)
    else:
        messagebox.showwarning("Warning", "찾을 사용자를 선택해주세요")

    try:
        data = pickle.loads(open('users/' + user, "rb").read())
    except OSError:
        print('can\'t found ' + user)

    def cam():
        vs = cv2.VideoCapture(0)
        detected(vs)

    def video():
        video_files = filedialog.askopenfilenames(title="파일을 선택하세요", \
                                                  filetypes=(("MP4 파일", "*.mp4"), ("모든 파일", "*.*")), \
                                                  initialdir="C:/")
        if video_files == '':
            return
        temp.delete(0, END)
        temp.insert(0, video_files)

        global select_video  # 선택 파일 경로
        select_video = temp.get()
        print(select_video)
        print(user)
        vs = cv2.VideoCapture(select_video)
        detected(vs)

    def img():
        img_files = filedialog.askopenfilenames(title="파일을 선택하세요", \
                                                filetypes=(("JPG 파일", "*.jpg"), ("모든 파일", "*.*")), \
                                                initialdir="C:/")
        if img_files == '':
            return
        temp.delete(0, END)
        temp.insert(0, img_files)

        global select_img  # 선택 파일 경로
        select_img = temp.get()
        print(select_img)
        print(user)
        image = cv2.imread(select_img)
        detect_img(image)

    def detected(vs):
        while True:
            temp.delete(0, END)
            ret, image = vs.read()
            if not ret:
                break

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(image, (int(image.shape[1] * scaler), int(image.shape[0] * scaler)))

            r = image.shape[1] / float(rgb.shape[1])

            boxes = face_recognition.face_locations(rgb, model='CNN')
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []  # for recognized faces

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
                        counts[name] = counts.get(name, 0)

                    for items in matchesIndxs:
                        counts[data['names'][items]] = counts.get(data['names'][items]) + 1
                    name = max(counts, key=counts.get)
                    print(counts)
                names.append(name)

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
                cv2.imshow("video", image)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    cv2.destroyAllWindows()
                    ori_set()
                    User_detect.destroy()
                    return

    def detect_img(image):
        temp.delete(0, END)

        rgb = cv2.resize(image, (int(image.shape[1] * scaler), int(image.shape[0] * scaler)))

        r = image.shape[1] / float(rgb.shape[1])

        boxes = face_recognition.face_locations(rgb, model='CNN')
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []  # for recognized faces

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

        cv2.imshow("img", image)
        ori_set()
        User_detect.destroy()

    User_detect = Toplevel(root)  # 새 창띄워서 이름 입력받기
    btn1 = Button(User_detect, text="Web Cam", command=cam)
    btn2 = Button(User_detect, text="Video file", command=video)
    btn3 = Button(User_detect, text="Image file", command=img)

    temp = Entry(User_detect)

    btn1.pack(fill='x')
    btn2.pack(fill='x')
    btn3.pack(fill='x')


def bt3cmd():  # 사용자 삭제 버튼
    if list_name:  # 리스트에서 현재 선택한 파일 받아오기
        user = list_name()
        print(user)
    else:
        messagebox.showwarning("Error", "삭제할 사용자를 선택해주세요")  # 리스트에서 사용자가 선택되지 않았을경우 메세지박스로 알려줌 버튼 비활성화로 작동할일 없음

    file = 'users/' + user

    if os.path.isfile(file):  # 선택한 파일이 존재할경우에
        response = messagebox.askyesno(title="ASK", message=user + "파일을 삭제하시겠습니까?")
        if response == 1:
            os.remove(file)  # 파일을 삭제한다
            refresh_list()  # 파일이 삭제되어 순서에 변화가 생겼기에 리스트를 갱신해준다
            messagebox.showinfo("INFO", "파일" + user + "의 삭제가 완료 되었습니다")  # 삭제완료 메세지 박스로 알려준다
        else:
            messagebox.showinfo("CANCEL", "파일" + user + "의 삭제를 취소하였습니다")
    else:
        messagebox.showerror("Error", "삭제할 파일이 존재하지 않습니다")  # 파일이 존재하지 않을 경우에 메세지박스로 알려준다(정상적인 상황에서 발생할수 없는 오류)

    ori_set()


def bt4cmd():  # 리스트에 있는 모든 사용자를 탐색

    knownEncodings = []
    knownNames = []

    load_data(data_path)  # 리스트에 들어가 파일이 있는 폴더를 스캔해준다
    for i in onlyfiles:  # 리스트에 존재하는 파일 순서대로 입력
        u_data = pickle.loads(open('users/' + i, "rb").read())
        for encoding in u_data["encodings"]:
            knownEncodings.append(encoding)
            knownNames.append(i)

    data = {"encodings": knownEncodings, "names": knownNames}

    def cam():
        vs = cv2.VideoCapture(0)
        detected(vs)

    def video():
        video_files = filedialog.askopenfilenames(title="파일을 선택하세요", \
                                                  filetypes=(("MP4 파일", "*.mp4"), ("모든 파일", "*.*")), \
                                                  initialdir="C:/")
        if video_files == '':
            return
        temp.delete(0, END)
        temp.insert(0, video_files)

        global select_video  # 선택 파일 경로
        select_video = temp.get()
        print(select_video)
        vs = cv2.VideoCapture(select_video)
        detected(vs)

    def img():
        img_files = filedialog.askopenfilenames(title="파일을 선택하세요", \
                                                filetypes=(("JPG 파일", "*.jpg"), ("모든 파일", "*.*")), \
                                                initialdir="C:/")
        if img_files == '':
            return
        temp.delete(0, END)
        temp.insert(0, img_files)

        global select_img  # 선택 파일 경로
        select_img = temp.get()
        print(select_img)
        image = cv2.imread(select_img)
        detect_img(image)

    def detected(vs):
        while True:
            temp.delete(0, END)
            ret, image = vs.read()
            if not ret:
                break

            rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            rgb = cv2.resize(image, (int(image.shape[1] * scaler), int(image.shape[0] * scaler)))

            r = image.shape[1] / float(rgb.shape[1])

            boxes = face_recognition.face_locations(rgb, model='CNN')
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []  # for recognized faces

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
                cv2.imshow("video", image)
                key = cv2.waitKey(1) & 0xFF

                if key == ord("q"):
                    cv2.destroyAllWindows()
                    User_detect.destroy()
                    return

    def detect_img(image):
        temp.delete(0, END)

        rgb = cv2.resize(image, (int(image.shape[1] * scaler), int(image.shape[0] * scaler)))

        r = image.shape[1] / float(rgb.shape[1])

        boxes = face_recognition.face_locations(rgb, model='CNN')
        encodings = face_recognition.face_encodings(rgb, boxes)
        names = []  # for recognized faces

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

        cv2.imshow("img", image)
        User_detect.destroy()

    User_detect = Toplevel(root)  # 새 창띄워서 이름 입력받기
    btn1 = Button(User_detect, text="Web Cam", command=cam)
    btn2 = Button(User_detect, text="Video file", command=video)
    btn3 = Button(User_detect, text="Image file", command=img)

    temp = Entry(User_detect)

    btn1.pack(fill='x')
    btn2.pack(fill='x')
    btn3.pack(fill='x')


def bt5cmd():  # 사용자 파일 추가 및 이름 변경
    if list_name:  # 리스트에서 현재 선택한 파일 받아오기
        user = list_name()
        print(user)
    else:
        messagebox.showwarning("Error", "수정할 사용자를 선택해주세요")  # 리스트에서 사용자가 선택되지 않았을경우 메세지박스로 알려줌 버튼 비활성화로 작동할일 없음

    file = 'users/' + user

    def rename():

        def get_name():  # 이름 입력받고 얼굴등록 함수 호출
            print(e.get())
            if e.get():
                g_name = str(e.get())
                print(g_name)
                e.delete(0, END)
                response = messagebox.askyesno(title="ReName", message=user + " 에서 " + g_name + " 으로 변경하시겠습니까?")
                if response == 1:
                    change_name(g_name)
                    messagebox.showinfo("INFO", "이름이 변경 되었습니다")
                else:
                    messagebox.showinfo("CANCEL", "이름이 변경되지 않았습니다.")

                ori_set()
                User_detect.destroy()
            else:
                print("Error")

        def change_name(g_name):
            new_file = 'users/' + g_name
            change = []
            encodings = []
            os.rename(file, new_file)  # 폴더의 파일명 변경

            try:
                data = pickle.loads(open(new_file, "rb").read())
            except OSError:
                print('can\'t found ' + user)

            for i in data["encodings"]:
                encodings.append(i)
                change.append(g_name)

            change_file = {"encodings": encodings, "names": change}

            files = open(new_file, 'wb')
            files.write(pickle.dumps(change_file))
            files.close()

            refresh_list()

        getName = Toplevel(User_detect)  # 새 창띄워서 이름 입력받기
        label = Label(getName, text="변경할 이름을 입력하세요")
        e = Entry(getName)
        btn = Button(getName, text="사용자 이름 변경", command=get_name)

        label.pack()
        e.pack()
        btn.pack(fill='x')

    def add():
        global check
        check = False

        knownEncodings = []
        knownNames = []
        u_data = pickle.loads(open(file, "rb").read())
        for encoding in u_data["encodings"]:
            knownEncodings.append(encoding)
            knownNames.append(user)

        def add_cam():

            user = list_name()
            cap = cv2.VideoCapture(0)
            count = 0

            while True:
                ret, frame = cap.read()
                if not ret:
                    break

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

                boxes = face_recognition.face_locations(rgb, model='CNN')

                encodings = face_recognition.face_encodings(rgb, boxes)

                for encoding in encodings:
                    global check
                    check = True
                    print(user, encoding)
                    knownEncodings.append(encoding)
                    knownNames.append(user)
                    print(encoding)
                    count += 1

                if check is False:
                    cv2.putText(frame, "Face not Found", (0, 25), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
                    pass

                for ((top, right, bottom, left), user) in zip(boxes, knownNames):
                    # rescale the face coordinates
                    top = int(top)
                    right = int(right)
                    bottom = int(bottom)
                    left = int(left)

                    color = (255, 255, 0)
                    cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
                    y = top - 15 if top - 15 > 15 else top + 15

                    ename = user + str(count) + '%'
                    if count == 100:
                        ename = "complete"
                    cv2.putText(frame, ename, (left, y), cv2.FONT_HERSHEY_SIMPLEX, 0.75, color, 2)

                cv2.imshow('encoding', frame)
                check = False

                if cv2.waitKey(1) == 13:
                    messagebox.showerror("Error", "사용자 추가를 중단 합니다")
                    cap.release()
                    cv2.destroyAllWindows()
                    User_detect.destroy()
                    return

                elif count == 100:
                    print('Collecting Samples Complete!!!')
                    break

            data = {"encodings": knownEncodings, "names": knownNames}
            f = open(file, "wb")
            f.write(pickle.dumps(data))
            f.close()
            cap.release()
            cv2.destroyAllWindows()
            User_detect.destroy()
            messagebox.showinfo("complete", "사용자 추가 등록이 완료되었습니다")

        def add_image():

            img_files = filedialog.askdirectory(title="파일을 선택하세요", \
                                                initialdir="C:/")
            if img_files == '':
                return
            temp.delete(0, END)
            temp.insert(0, img_files)

            global select_folder  # 선택 파일 경로
            select_folder = temp.get() + '/'
            print(select_folder)

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
                    messagebox.showerror("Error", "얼굴인식에 실패했습니다. 파일을 확인해주세요")
                    return 0

                for encoding in encodings:
                    knownEncodings.append(encoding)
                    knownNames.append(user)
                    print(encoding)

            data = {"encodings": knownEncodings, "names": knownNames}
            f = open(file, "wb")
            f.write(pickle.dumps(data))
            f.close()
            messagebox.showinfo("complete", "사용자 추가 등록이 완료되었습니다")
            cv2.destroyAllWindows()
            User_detect.destroy()

        User_detect2 = Toplevel(User_detect)  # 새 창띄워서 이름 입력받기
        btn1 = Button(User_detect2, text="웹캡으로 추가", command=add_cam)
        btn2 = Button(User_detect2, text="이미지로 추가", command=add_image)

        temp = Entry(User_detect)

        btn1.pack(fill='x')
        btn2.pack(fill='x')

    User_detect = Toplevel(root)  # 새 창띄워서 이름 입력받기
    btn1 = Button(User_detect, text="이름 바꾸기", command=rename)
    btn2 = Button(User_detect, text="사용자 파일 추가", command=add)

    btn1.pack(fill='x')
    btn2.pack(fill='x')


bt1 = Button(file_frame2, text="사용자 등록", padx=5, pady=5, width=9, command=bt1cmd)
bt2 = Button(file_frame1, text="사용자 탐색", padx=5, pady=5, width=15, command=bt2cmd, state=DISABLED)
bt3 = Button(file_frame2, text="사용자 삭제", padx=5, pady=5, width=9, command=bt3cmd, state=DISABLED)
bt4 = Button(file_frame1, text="모든 등록 탐색", padx=5, pady=5, width=15, command=bt4cmd)
bt5 = Button(file_frame2, text="사용자 수정", padx=5, pady=5, command=bt5cmd, state=DISABLED)

bt1.grid(row=0, column=0)
bt2.grid(row=0, column=0)
bt3.grid(row=0, column=2)
bt4.grid(row=0, column=1)
bt5.grid(row=0, column=1)

list_frame = Frame(root)
list_frame.pack(fill="both",)

scrollbar = Scrollbar(list_frame)
scrollbar.pack(side="right", fill="y", )

list_file = Listbox(list_frame, selectmode="extended", height=15, yscrollcommand=scrollbar.set)
list_file.pack(side="left", fill="both", expand=True)
scrollbar.config(command=list_file.yview)

listbox = Listbox(list_file, selectmode="single")
refresh_list()
listbox.pack(fill="both")

path_frame = LabelFrame(root, text="파일위치")
path_frame.pack(fill="x",)

txt_dest_path = Entry(path_frame)
txt_dest_path.pack(side="left", fill="x", expand=True, ipady=4)


def ori_set():  # 초기 버튼 상태 비활성화
    bt3['state'] = DISABLED
    bt2['state'] = DISABLED
    bt5['state'] = DISABLED


def switchButtonState():  # 리스트가 선택되면 버튼 상태를 활성화 시켜주는 함수
    if bt3['state'] == DISABLED and bt2['state'] == DISABLED and bt5['state'] == DISABLED:
        bt3['state'] = NORMAL
        bt2['state'] = NORMAL
        bt5['state'] = NORMAL
    else:
        pass


def list_name():
    if listbox.curselection():
        i = listbox.curselection()
        num = listbox.index(i)
        user = onlyfiles[num]
        return user
    else:
        return ''


def callback(event):  # 리스트클릭 이벤트 발생시 switch 함수를 불러와서 버튼을 활성화 시켜줌
    selection = event.widget.curselection()
    if selection:
        switchButtonState()
        if login_check:
            menu_file.entryconfig(2, state="normal")
    else:
        pass


listbox.bind("<<ListboxSelect>>", callback)


def dest_folder():  # 찾아보기 버튼  파일경로읽어오기
    files = filedialog.askdirectory(title="폴더를 선택하세요", \
                                    initialdir="C:/")

    if files == '':
        return
    txt_dest_path.delete(0, END)
    txt_dest_path.insert(0, files)

    global select_folder  # 선택 파일 경로
    select_folder = txt_dest_path.get() + '/'
    print(select_folder)


btn_dest_path = Button(path_frame, text="찾아보기", width=10, command=dest_folder)
btn_dest_path.pack(side="right")

root.resizable(False, False)
root.mainloop()
