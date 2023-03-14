import sys
import RPi.GPIO as GPIO
import pyzbar.pyzbar as pyzbar
import cv2
from gpiozero import LED
import requests
import time
from datetime import datetime
import threading
import math
headers = {
    'ApiKey': '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'
}
#print("code started")
led_red = LED(18)
led_blue = LED(24)
def run_led():
    while True:
        print("hello")
        url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/StudentsOut"
        print("gotUrl")
        response = requests.get(url, headers=headers)
        data = response.json()
        if data:
            data = data[0]
            num_out = data['numStudentsOut']
            if in_class == True:
                num_out=(num_out + 1)
                print(num_out)
            else:
                num_out=(num_out - 1)
                url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/UpdateStudentsOut"
                "numStudentsOut": num_out
                print(num_out)
                GPIO.setmode(GPIO.BCM)
                if num_out >= 2:
                    print("red led on")
                    led_blue.off()
                    led_red.on()
                if num_out < 2:
                    print("blue led on")
                    led_red.off()
                    led_blue.on()
                else:
                    print("bad boi")
                    # Break the loop if the 'q' key is pressed
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
if __name__ == "__main__":
     run_led()