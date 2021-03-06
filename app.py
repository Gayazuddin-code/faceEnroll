from flask import Flask, render_template, Response, request, redirect
import cv2
import os
import mysql.connector

# mydb = mysql.connector.connect(
#     host="gayazuddin.mysql.pythonanywhere-services.com",
#     user="gayazuddin",
#     password="Gayaz12377",
#     database="gayazuddin$attendance"
# )


mydb = mysql.connector.connect(
    host="remotemysql.com",
    port=3306,
    user="qT9Qw34w5T",
    password="sSsQzyM57n",
    database="qT9Qw34w5T"
)

print(mydb)

print("Connected to:", mydb.get_server_info())

mycursor = mydb.cursor()

# make shots directory to save pics
try:
    os.mkdir('./shots')
except OSError as error:
    pass

import faceFeatures

global capture, switch, name
capture = 0
switch = 1

# instantiate flask app
app = Flask(__name__)
camera = cv2.VideoCapture(0)


def gen_frames():  # generate frame by frame from camera
    global capture
    while True:
        success, frame = camera.read()
        if success:
            if capture:
                capture = 0
                print(name)
                p = os.path.sep.join(["shots", f"{name}.png"])
                cv2.imwrite(p, frame)
                features_list = str(faceFeatures.user())

                sql = "INSERT INTO student (name, usn, email, password, features) VALUES (%s, %s, %s, %s, %s)"
                val = (name, usn, email, password, features_list)
                mycursor.execute(sql, val)

                mydb.commit()

                print(mycursor.rowcount, "record inserted.")

            try:
                ret, buffer = cv2.imencode('.jpg', cv2.flip(frame, 1))
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            except Exception as e:
                pass


@app.route('/')
@app.route('/home')
def home():
    return render_template('home.html')


@app.route('/teacherLogin', methods=['POST', "GET"])
def teacherLogin():
    if request.method == 'POST':
        if request.form.get('register'):
            return redirect('teacherRegister')

        elif request.form.get('login'):
            login_details = dict()
            login_id = request.form.get('id')
            login_password = request.form.get('password')
            print(login_id, login_password)

            sql = "SELECT teacher_id FROM teacher"
            mycursor.execute(sql)
            id_list = []
            result = mycursor.fetchall()
            for x in result:
                id_list.append(x[0])
            print(id_list)

            sql = "SELECT password FROM teacher"
            mycursor.execute(sql)
            password_list = []
            result = mycursor.fetchall()
            for x in result:
                password_list.append(x[0])
            print(password_list)

            for i in range(len(id_list)):
                login_details[id_list[i]] = password_list[i]

            print(login_details)

            for key, vlaue in login_details.items():
                print(key, vlaue)

            while True:
                if login_id in id_list and login_password in password_list:
                    if login_details[login_id] == login_password:
                        sql = "select * from student"
                        mycursor.execute(sql)
                        data = mycursor.fetchall()
                        print(data)
                        return render_template('table.html', value=data)
                else:
                    continue
    return render_template(('TeacherLogin.html'))


@app.route('/teacherRegister', methods=['POST', 'GET'])
def teacherRegister():
    if request.form.get('SubmitTeacher'):
        if request.method == 'POST':
            global name, id, email, password
            if request.form.get('SubmitTeacher'):
                name = request.form.get('name')
                id = request.form.get('id')
                email = request.form.get('email')
                password = request.form.get('password')
                while True:
                    conform_password = request.form.get('conform_password')
                    if conform_password == password:
                        sql = "INSERT INTO teacher (teacher_id, name, email, password) VALUES (%s, %s, %s, %s)"
                        val = (id, name, email, password)
                        mycursor.execute(sql, val)
                        mydb.commit()
                        print(mycursor.rowcount, "record inserted.")
        return render_template('TeacherLogin.html')
    return render_template('TeacherRegister.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        if request.form.get('register'):
            return redirect('register')

        elif request.form.get('login'):
            login_details = dict()
            login_usn = request.form.get('usn')
            login_password = request.form.get('password')
            print(login_usn, login_password)

            sql = "SELECT usn FROM student"
            mycursor.execute(sql)
            usn_list = []
            result = mycursor.fetchall()
            for x in result:
                usn_list.append(x[0])
            print(usn_list)

            sql = "SELECT password FROM student"
            mycursor.execute(sql)
            password_list = []
            result = mycursor.fetchall()
            for x in result:
                password_list.append(x[0])
            print(password_list)

            for i in range(len(usn_list)):
                login_details[usn_list[i]] = password_list[i]

            print(login_details)

            for key, vlaue in login_details.items():
                print(key, vlaue)

            while True:
                if login_usn in usn_list and login_password in password_list:
                    print(login_usn)
                    if login_details[login_usn] == login_password:
                        sql = f"select * from student where usn = '{login_usn}'"
                        mycursor.execute(sql)
                        data = mycursor.fetchall()
                        print(data)
                        return render_template('table.html', value=data)
                else:
                    continue
    return render_template('student_login.html')


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == 'POST':
        global name, usn, email, password
        if request.form.get('photo'):
            name = request.form.get('name')
            usn = request.form.get('usn')
            email = request.form.get('email')
            password = request.form.get('password')
            while True:
                conform_password = request.form.get('conform_password')
                if conform_password == password:
                    break
            return redirect('camera')
    return render_template('student_register.html')


@app.route('/camera')
def camera_capture():
    return render_template('camera.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/requests', methods=['POST', 'GET'])
def tasks():
    global switch, camera
    if request.method == 'POST':
        if request.form.get('click') == 'Capture':
            global capture
            capture = 1

        elif request.form.get('stop') == 'Stop/Start':
            if switch == 1:
                switch = 0
                camera.release()
                cv2.destroyAllWindows()
            else:
                camera = cv2.VideoCapture(0)
                switch = 1

    elif request.method == 'GET':
        return render_template('camera.html')
    return render_template('camera.html')


# if __name__ == '__main__':
#     app.run(debug=False)


# start Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

camera.release()
cv2.destroyAllWindows()
