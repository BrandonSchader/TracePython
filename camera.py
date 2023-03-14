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
scanned_qr_codes = {}
print("code started")
def scan_qr_code():
    triggerPIN = 23
    # Capture video from the webcam
    camera = cv2.VideoCapture(0)
    while True:
        # Read the frame from the webcam
        grabbed, frame = camera.read()
        # Decode the QR code from the frame
        barcodes = pyzbar.decode(frame)
        # Loop through all the QR codes detected
        for barcode in barcodes:
            # Get the QR code data
            qr_code_data = int(barcode.data.decode("utf-8"))
            # Get the status of the student from the database using the API
            current_time = time.time()
            if qr_code_data in scanned_qr_codes and current_time - scanned_qr_codes[qr_code_data] < 6:
                continue
            else:
                scanned_qr_codes[qr_code_data] = current_time
            url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/FilterStudentInfo?filterColumn=studentId&filterValue=" + str(qr_code_data)
            response = requests.get(url, headers=headers)
            if response.status_code == 200:
                    GPIO.setmode(GPIO.BCM)
                    current_time = time.time()
                    GPIO.setup(triggerPIN, GPIO.OUT, initial=GPIO.LOW)
                    buzzer = GPIO.PWM(triggerPIN, 8) # Set frequency to 8 Khz
                    buzzer.start(8) # set dutycycle to 10
                    time.sleep(1)
                    buzzer.stop()
                    GPIO.cleanup()
                    # Update the status of the student in the database
                    data = response.json()
                    if data:
                        data = data[0]
                        student_id = data['studentId']
                        first_name =  data['firstName']
                        last_name = data['lastName']
                        time_out = data['timeOut']
                        time_in = data['timeIn']
                        punch_outs = data['punchOuts' ]
                        in_class = data['inClass']
                        class_name = data['className']
                        teach = data['teacher']
                        para_pro = data['paraPro']
                        room_number = data['roomNumber']
                        url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/StudentsOut"
                        print("gotUrl")
                        response = requests.get(url, headers=headers)
                        data = response.json()
                        if data:
                            data = data[0]
                            num_out = data['numStudentsOut']
                            print("number of students out", num_out)
                        # Update the data in the API
                        if in_class == True:
                            num_out=(num_out + 1)
                            print(num_out)
                            punch_outs=(punch_outs + 1)
                            print(punch_outs)
                            time_out = (time.strftime("%H:%M:%S"))
                            print(time_out, "time out", in_class, punch_outs)
                            url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/UpdateStudentInfo"
                            updated_data = {"studentId": student_id,
                            "firstName": first_name,
                            "lastName": last_name,
                            "timeOut": time_out,
                            "timeIn": time_in,
                            "punchOuts": punch_outs,
                            "inClass": not in_class,
                            "className": class_name,
                            "teacher": teach,
                            "paraPro": para_pro,
                            "roomNumber": room_number,
                            }
                            print(time_out, "time out", in_class, punch_outs)
                            update_response = requests.post(url, headers=headers, json=updated_data)
                            print("def good")
                            print("b4 add payload")
                            url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/UpdateStudentsOut"
                            payload ={
                            "numStudentsOut": num_out,
                            }
                            print("after add payload")
                            if update_response.status_code != 200:
                                print("Failed to update the data:", update_response.text)
                            else:
                                print("secondary win lol?",first_name,punch_outs,in_class)
                        else:
                            num_out=(num_out - 1)
                            print(num_out)
                            time_in = (time.strftime("%H:%M:%S"))
                            print(time_in, "time in", in_class, punch_outs)
                            url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/UpdateStudentInfo"
                            updated_data = {"studentId": student_id,
                            "firstName": first_name,
                            "lastName": last_name,
                            "timeOut": time_out,
                            "timeIn": time_in,
                            "punchOuts": punch_outs,
                            "inClass": not in_class,
                            "className": class_name,
                            "teacher": teach,
                            "paraPro": para_pro,
                            "roomNumber": room_number,
                            }
                            print(time_in, "time in", in_class, punch_outs)
                            update_response = requests.post(url, headers=headers, json=updated_data)
                            print("def good")
                            print("b4 add payload")
                            url = "https://student-tracker-web-api-1.azurewebsites.net/api/controller/UpdateStudentsOut"
                            payload ={
                            "numStudentsOut": num_out,
                            }
                            print("after add payload")
                            if update_response.status_code != 200:
                                print("Failed to update the data:", update_response.text)
                            else:
                                print("secondary win lol?",first_name,punch_outs,in_class)
                            continue
                            print("got Herelol")
        # Display the frame
        cv2.imshow("QR Code Scanner", frame)
        # Break the loop if the 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    # Release the video capture object
    camera.release()
    # Close all windows
    cv2.destroyAllWindows()
if __name__ == "__main__":
    '''
    thread1 = threading.Thread(target=scan_qr_code)
    thread2 = threading.Thread(target=run_led)
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()
    '''
scan_qr_code()