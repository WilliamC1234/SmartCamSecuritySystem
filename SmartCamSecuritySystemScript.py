import os
import serial
import time
import http.client, urllib
import tensorflow as tf
from keras.models import load_model  # TensorFlow is required for Keras to work
import cv2  # Install opencv-python
import numpy as np
from tensorflow.keras.layers import DepthwiseConv2D

#Variables that need to be adjusted

token = "Enter your token here"
user = "Enter user token here"
comPort = "Enter COM port here"

#Variables that can be adjusted

#Time to record if a person is detected
recordTime = 600  #Default is 10 minutes

#Disables the camera after a person isn't detected
waitTime = 1200 #Default is 20 minutes


# Initialize the serial connection to the Arduino
arduino = serial.Serial(comPort, 9600, timeout=1)
time.sleep(2)  # Give time for the serial connection to establish

# Disable scientific notation for clarity
np.set_printoptions(suppress=True)

class CustomDepthwiseConv2D(DepthwiseConv2D):
    def __init__(self, *args, **kwargs):
        kwargs.pop("groups", None)  # Ignore 'groups' argument
        super().__init__(*args, **kwargs)

# Load the model
model = load_model(
    "Model/keras_model.h5",
    compile=False,
    custom_objects={"DepthwiseConv2D": CustomDepthwiseConv2D}
)

# Load the labels
class_names = open("Model/labels.txt", "r").readlines()

# CAMERA can be 0 or 1 based on default camera of your computer
camera = cv2.VideoCapture(0)

# Sets up to send notification if detection from sensor
sendMessage1 = urllib.parse.urlencode({
    "token": token, "user": user,
    "message": "The Motion Sensor has Detected Motion!"
})

# Sets up to send notification if detection on camera
sendMessage2 = urllib.parse.urlencode({
    "token": token, "user": user,
    "message": "Person detected on your camera, a snapshot will be sent via email and a recording will be taken.",
}).encode("utf-8")

# Define recording parameters
video_file_path = "camera_output.avi"
frame_width, frame_height, fps = 224, 224, 20
codec = cv2.VideoWriter_fourcc(*"XVID")
video_writer = None

# Flag to track whether the camera is active
camera_active = False

while True:
    if not camera_active:  # Only check motion sensor if the camera is NOT running
        try:
            motionResult = arduino.readline().decode('utf-8').strip()
        except serial.serialutil.SerialException as e:
            print(f"Serial error: {e}")
            continue

        if motionResult == "Motion detected!":
            print("Motion detected, triggering camera processing...")
            conn = http.client.HTTPSConnection("api.pushover.net", 443)
            conn.request("POST", "/1/messages.json", sendMessage1, 
                         {"Content-type": "application/x-www-form-urlencoded"})
            time.sleep(2)

            camera_active = True  # Set flag to prevent motion sensor from triggering again

    while camera_active:  # Process camera input
        record_start_time = time.time()

        while True:
            conn = http.client.HTTPSConnection("api.pushover.net", 443)
            ret, image = camera.read()
            if not ret:
                break

            # Resize image and display
            image = cv2.resize(image, (224, 224), interpolation=cv2.INTER_AREA)
            cv2.imshow("Webcam Image", image)

            # Preprocess image
            image = np.asarray(image, dtype=np.float32).reshape(1, 224, 224, 3)
            image = (image / 127.5) - 1

            # Predict using model
            prediction = model.predict(image)
            index = np.argmax(prediction)
            class_name = class_names[index].strip()
            confidence_score = prediction[0][index]

            print("Class:", class_name[2: ], end=" ")
            print("Confidence Score:", str(np.round(confidence_score * 100))[:-2], "%")


            # Start recording if a person is detected
            if "Person" in class_name and confidence_score >= 0.90:
                record_start_time = time.time()
                conn.request("POST", "/1/messages.json", sendMessage2, 
                             {"Content-type": "application/x-www-form-urlencoded"})
                
                #Checks for matching file and adjusts accordingly
                if os.path.isfile(video_file_path):
                    i = 1
                    while os.path.isfile(f"camera_output({i}).avi"):
                        i += 1
                    video_file_path = f"camera_output({i}).avi"
                video_writer = cv2.VideoWriter(video_file_path, codec, fps, (frame_width, frame_height))
                

                # Starts recording for recordTime
                while time.time() - record_start_time <= recordTime:
                    ret, frame = camera.read()
                    if not ret:
                        print("Failed to capture frame, stopping recording.")
                        break                    
                    frame_resized = cv2.resize(frame, (224, 224))
                    video_writer.write(frame_resized)
                    

            # Stop camera after waitTime
            if time.time() - record_start_time >= waitTime:
                print("No detections, returning to motion detection mode.")
                
                # Flush any lingering messages from the motion sensor
                arduino.flushInput()
                
                camera_active = False
                break

            # Stop program if 'Esc' is pressed
            keyboard_input = cv2.waitKey(1)
            if keyboard_input == 27:
                camera_active = False
                break

# Cleanup
camera.release()
conn.close()
cv2.destroyAllWindows()
arduino.close()
