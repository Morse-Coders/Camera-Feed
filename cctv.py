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
from twilio.rest import Client
import datetime
import smtplib
import imghdr
from email.message import EmailMessage
# import pyrebase
import collections
import requests
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


url = "https://sarasmarg.ml/cctv"
obj = {"description": "By CCTV", "files": "https://firebasestorage.googleapis.com/v0/b/morsecoderscctv.appspot.com/o/img.png?alt=media&token=5d5c7a0e-c5a7-4710-ad75-71783a62ea97",
       "problem": "shallow", "status": "Pending", "coordinates": "13.012737,77.7038853", "location": "Cambridge Institute of Technology, K R Puram, Bangalore"}
x = requests.post(url, json=obj)


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


def checktime():
    return(time.localtime())


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

            cv.putText(frame, prediction.tag_name, (y, x-10),
                       cv.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2, cv.LINE_AA)
            cv.rectangle(frame, (y+10, x+10),
                         (y+w+10, x+h+10), (0, 255, 255), 5)

        cv.imshow("CCTV_1_FOOTAGE", frame)

    key = cv.waitKey(delay) & 0xFF
    if key == ord('q'):
        break  # press q to quit


vid.release()
cv.destroyAllWindows()
