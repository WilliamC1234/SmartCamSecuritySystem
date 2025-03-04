# SmartCamSecuritySystem
Uses a motion sensor to activate an image model that detects a person and starts a recording and pushes out a notification

Description:

This script is designed to work with an Arduino connected with a motion sensor. When motion is detected, the script will activate the camera and the image model which is trained to detect whether there is a person or not on the camera. The motion sensor allows for the model to more accurately determine whether or not a person is actually on the camera, as the image model is not 100% accurate, and can have issues with detecting animals as people, although it has been trained to detect the difference.


IMPORTANT:

To have notifications properly send, you need to make an account on Pushover, which is an app that allows for you to receive and send push notifications to your devices. A license is $5, but there is a 30 day trial if you are only using this temporarily.

These variables need to be adjusted before running the script.

token - This token should be obtained from Pushover

user - This is the user key, which can be obtained from Pushover

Variables that can be adjusted

recordTime - This sets the length of time to record, which defaults to 600 seconds (10 minutes)

waitTime - This sets the length of time that the script will wait to stop the camera if it doesn't detect a person, which is default 1200 seconds (20 minutes)


Instructions:

1. Install Python and Arduino IDE.

2. Install the required dependencies using pip:
	
	pyserial, tensorflow, http, numpy, opencv-python.

3. Make an account on Pushover and install the application to your device.

4. Get the token for your device and the user key from Pushover.

5. Set Arduino up with motion sensor and adjust pins as necessary in IDE.

6. Input your token and user key into SmartCamSecuritySystemScript.py.

7. Set the correct COM port on the comPort variable.

8. Adjust the timings as needed.

9. Run the script.




