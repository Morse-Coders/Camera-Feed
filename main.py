import os
import sys
import time
from cv2 import cv2 as cv
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
import requests
import json
from twilio.rest import Client  # REST API
import datetime
import smtplib
import imghdr
from email.message import EmailMessage
# import pyrebase
import collections
import requests
# from pyowm import OWM
import sqlite3
from msrest.authentication import ApiKeyCredentials
import creds


def image_resize(img):
    # import numpy as np
    # from PIL import Image
    image = Image.fromarray(img, 'RGB')
    # print(type(image))
    if image.size > (1600, 1600):
        image = image.resize((1600, 1600))
    # image = image.save("./image.jpg") # where to temporarily save image
    return image


def predictor_(test_data):
    ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"
    prediction_key = "7054b38d3abd4d4aa8ebd277e93c5b48"
    prediction_resource_id = "/subscriptions/25b533ab-d3ed-49bf-b0ac-14f11d1add00/resourceGroups/Pothholes/providers/Microsoft.CognitiveServices/accounts/idealbits"
    prediction_credentials = ApiKeyCredentials(
        in_headers={"Prediction-key": prediction_key})
    predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)
    project_id = "92f7895d-68ec-42aa-9882-4035d152cf03"
    publish_iteration_name = "Iteration4"
    iteration_id = "855ff99a-38ec-43a5-aade-bdfcf3c96808"
    results = predictor.detect_image(
        project_id, publish_iteration_name, test_data)
    return results


def sms(tag, prob, loc, loc_, date, time, cam, to_tx):
    acc_sid = "AC7d67a6985ef6737676fbd66ae01f08b4"
    auth_token = "21f672c414f2ddb739f6180d81061b4a"

    client = Client(acc_sid, auth_token)
    for _ in range(len(tag)):
        tag1 = str(tag[_])
        prob1 = str(prob[_])
        msg = "Road deformation"+tag1+" is detected" + cam + " with a confidence of " + prob1 + \
            "at location" + loc + "on" + date + "at" + time + " Location Link: " + loc_
        message = client.messages.create(
            body=msg,
            to=to_tx,
            from_='+12517584980')
    print("SMS SENT")


def email(tag, prob, loc, loc_, date, time, cam, email_rx):
    email_tx = creds.secrets["email_tx"]
    pass_tx = creds.secrets["pass_tx"]
    msg = EmailMessage()
    msg['Subject'] = 'ROAD DEFORMATION!'
    msg['From'] = email_tx
    msg['To'] = email_rx
    for _ in range(len(tag)):
        tag1 = str(tag[_])
        prob1 = str(prob[_])
        msg_ = "Road deformation"+tag1+" is detected" + cam + " with a confidence of " + prob1 + \
            "at location" + loc + "on" + date + "at" + time + " Location Link: " + loc_
        msg.set_content(msg_)

    with open("./image.jpg", 'rb') as f:  # path where frame is saved temporarirly
        file_data = f.read()
        file_name = f.name
        file_type = imghdr.what(f.name)

    msg.add_attachment(file_data, maintype='image',
                       subtype=file_type, filename=file_name)

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(email_tx, pass_tx)
        smtp.send_message(msg)
    print("E-mail SENT")


def checktime():
    return(time.localtime())


def firestore(tags, prob, loc, date, time, cam_name):
    config = {
        "apiKey": "AIzaSyDienGaKvTKGuSgKIFsU1pupYC1DABpeYk",
        "authDomain": "aghanya-test-py.firebaseapp.com",
        "databaseURL": "https://aghanya-test-py.firebaseio.com",
        "projectId": "aghanya-test-py",
        "storageBucket": "aghanya-test-py.appspot.com",
        "messagingSenderId": "356482709357",
        "appId": "1:356482709357:web:eeb1790474348ca3660c64",
        "measurementId": "G-MGVHBRZDTV"
    }

    img_path = "./image.jpg"  # image of  currentframe

    firebase = pyrebase.initialize_app(config)

    # database for data, storage for storing
    storage = firebase.storage()
    db = firebase.database()
    # data ={} #data to be stored
    for _ in range(len(tags)):
        data = {}
        data.update({"Date": date})
        data.update({"Time": time})
        data.update({"tag": tags[_]})
        data.update({"Probability": round(prob[_], 3)})
        data.update({"S": 0})
        rslt = db.child(cam_name).push(data)
        x = str(rslt.get('name'))  # Name of child node created
        path_on_cloud = cam_name + x + ".jpg"  # token+.jpg
        storage.child(path_on_cloud).put(img_path)
        url1 = storage.child(path_on_cloud).get_url('token')  # Downurl
        print(url1)
        # url2 = storage.child(path_on_cloud).get_url('imgPath') # Downurl
        # print(url2)
        db.child(cam_name).child(str(rslt.get('name'))).update({"URL": url1})
    print("STORED in db")


def SQL(tags, prob, loc, date_, time_, cam_name, result):
    from pyowm import OWM
    import sqlite3
    # WEATHER
    key = "d94f854d7176226f1fc9f8d2f2d64fcc"
    owm = OWM(key)  # You MUST provide a valid API key
    mgr = owm.weather_manager()
    x = loc.index(',')
    lat = float(loc[:x])
    lon = float(loc[x+1:])

    observation_list = mgr.weather_around_coords(lat, lon)
    observation = observation_list[1]
    w = observation.weather
    wind = w.wind()
    w_speed = float(wind['speed'])
    w_deg = float(wind['deg'])
    humid = float(w.humidity)
    stats = str(w.status)
    details = str(w.detailed_status)
    temp_file = w.temperature('celsius')
    temp = float(temp_file['temp'])

    # SQLite

    try:
        sqliteConnection = sqlite3.connect('../AGHNYA_SQLite.db')
        cursor = sqliteConnection.cursor()
        print(" Successfully Connected to SQLite")

        cursor = sqliteConnection.cursor()
        print("Successfully Connected to SQLite")

        for _ in range(len(tags)):
            cursor.execute("""INSERT INTO AGHNYA_KURUKSHETRA
                            (Id,User,CAM, Date_, Time_, Tag, Probability, Humidity, Temperature, Weather_stats, Detail_stats, Wind_speed, Wind_deg) 
                            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""", (result, 'ANKUR', cam_name, date_, time_, tags[_], round(prob[_], 3), humid, temp, stats, details, w_speed, w_deg))

            print("SAVED IN SQL")
            sqliteConnection.commit()
        cursor.close()

    except sqlite3.Error as error:
        print("Error while working with SQLite", error)
    finally:
        if (sqliteConnection):
            print("Total Rows affected since the database connection was opened: ",
                  sqliteConnection.total_changes)
            sqliteConnection.close()
            print("sqlite connection is closed")


# #Test Video
# vid_path = "./Test images/Stray Animals in India - A great concern __VET For PET__.mp4"
vid_path = "18515048-preview.mp4"
# vid_path = "./Test images/sec5_vid.mp4"
# fps = 25
vid = cv.VideoCapture(vid_path)
# vid.set(cv.CAP_PROP_FPS,fps)
delay = 500  # millisec
currentFrame = 0

loc = "29.964275,76.865226"  # predefined location here
cam_name = "cam4"  # predefined cam name
loc_link = "https://www.google.com/maps/place/29%C2%B057'51.4%22N+76%C2%B051'54.8%22E/@29.964275,76.8630373,17z/data=!3m1!4b1!4m5!3m4!1s0x0:0x0!8m2!3d29.964275!4d76.865226"


# MAIN
while(True):
    tags = []
    prob = []
    ret, frame = vid.read()
    if ret == False:
        continue
    currentFrame += 1
    frame = cv.cvtColor(frame, cv.COLOR_BGR2RGB)  # BGR to RGB
    image = image_resize(frame)
    image = image.save("./image.jpg")  # temp save of image

    with open("./image.jpg", mode='rb') as test_data:  # test images has all images
        results = predictor_(test_data)

    test_img_h, test_img_w, test_img_ch = np.array(frame).shape
    for prediction in results.predictions:

        if int(prediction.probability * 100) >= 25:  # thresold
            print("\t" + prediction.tag_name + ": {0:.2f}% bbox.left = {1:.2f}, bbox.top = {2:.2f}, bbox.width = {3:.2f}, bbox.height = {4:.2f}".format(
                prediction.probability * 100, prediction.bounding_box.left, prediction.bounding_box.top, prediction.bounding_box.width, prediction.bounding_box.height))
            tags.append(prediction.tag_name)
            prob.append(prediction.probability * 100)
            x = int(prediction.bounding_box.top * test_img_h)
            y = int(prediction.bounding_box.left * test_img_w)
            w = int(prediction.bounding_box.width * test_img_w)
            h = int(prediction.bounding_box.height * test_img_h)
            # cv.imshow("Video",frame)
            cv.putText(frame, prediction.tag_name, (y, x-10),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            cv.rectangle(frame, (y+10, x+10),
                         (y+w+10, x+h+10), (0, 255, 255), 5)
            # animal = frame[x+10:x+h+10, y+10:y+w+10, :]
            # cv.imshow("animal", animal)  # Animal Cutout
            # cv.imshow("Video",frame)
        cv.imshow("CCTV_1_FOOTAGE", frame)

    # if (tags != [] and prob != []):  # if some animal detected
    #     print(tags, prob)
    #     date = str(datetime.date.today())
    #     t = checktime()
    #     timex = time.strftime("%H:%M:%S", t)
    #     # # sending sms alert
    #     to = '+919996492589'

    #     sms(tags, prob, loc, loc_link, date, timex, cam_name, to)

    #     # # sending email alert with pic
    #     to_ = ["ankurvermaaxz@gmail.com"]  # mail to send alert
    #     email(tags, prob, loc, loc_link, date, timex, cam_name, to_)

    #     # Save image and data in firebase
    #     result = firestore(tags, prob, loc, date, timex, cam_name)
    #     SQL(tags, prob, loc, date, timex, cam_name, result)

    key = cv.waitKey(delay) & 0xFF
    if key == ord('q'):
        break  # press q to quit


vid.release()
cv.destroyAllWindows()
