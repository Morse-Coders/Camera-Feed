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
    # from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient
    ENDPOINT = "https://centralindia.api.cognitive.microsoft.com/"

    # Replace with a valid key
    # training_key = "<your training key>"
    # from azure.cognitiveservices.vision.customvision.prediction import CustomVisionPredictionClient

    prediction_key = "7054b38d3abd4d4aa8ebd277e93c5b48"
    prediction_resource_id = "/subscriptions/25b533ab-d3ed-49bf-b0ac-14f11d1add00/resourceGroups/Pothholes/providers/Microsoft.CognitiveServices/accounts/idealbits"
    prediction_credentials = ApiKeyCredentials(in_headers={"Prediction-key": prediction_key})
    predictor = CustomVisionPredictionClient(ENDPOINT, prediction_credentials)
    project_id = "92f7895d-68ec-42aa-9882-4035d152cf03"
    # "15d8e85f-3efe-4e32-a62c-8303c5b051a6"
    # publish_iteration_name = "Iteration1"
    publish_iteration_name = "Iteration4"
    # FOR IMAGE FILE
    # iteration_id="d8553fa6f7664beb89a582515860d199"
    iteration_id = "855ff99a-38ec-43a5-aade-bdfcf3c96808"
    results = predictor.detect_image(
        project_id, publish_iteration_name, test_data, iteration_id)
    return results

with open("3.jpg", "rb") as test_data:
    results = predictor_(test_data)
print(results)


