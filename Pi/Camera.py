import cv2
import math
import numpy as np
import threading
import time

import signal
import sys


def sharpen(frame):
    kernelC= cv2.getStructuringElement(cv2.MORPH_RECT,(21,21))
    kernelO = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(7,7))
    frame = cv2.morphologyEx(frame , cv2.MORPH_ERODE, kernelO)
    frame = cv2.morphologyEx(frame , cv2.MORPH_CLOSE, kernelC)
    frame = cv2.morphologyEx(frame , cv2.MORPH_OPEN, kernelO)
    #frame = cv2.morphologyEx(frame , cv2.MORPH_CLOSE, kernelC)
    return frame
    

class Camera(object):
    def __init__(self, num_regions, internet_cam=False, crop=False, show=False, area_needed=400):
        self.cam = cv2.VideoCapture(0)
        self.num_regions = num_regions
        self.internet_cam = internet_cam
        self.crop = crop
        self.show = show
        self.area_needed = area_needed

        self.internet_thread = None
        self.frame = None
        self.get_frame() # Fills in first frame
        self.height, self.width= self.frame.shape[:2]
        if not self.cam.isOpened():
            print("Cannot open camera")
            exit()

        if internet_cam and show:
            self.internet_thread = threading.Thread(target=self.show_internet, args=())
            self.internet_thread.setDaemon(True)
            self.internet_thread.start()

        self.running = True

        
        ## COLORS
        # RED1
        self.red_lower1 = np.array([0,120,50], np.uint8)
        self.red_upper1 = np.array([9,255,255], np.uint8)

        # RED2
        self.red_lower2 = np.array([167,120,50], np.uint8)
        self.red_upper2 = np.array([180,255,255], np.uint8)
        
        # BLUE
        self.blue_lower= np.array([90,70,50], np.uint8)
        self.blue_upper = np.array([120,255,255], np.uint8)

        # YELLOW
        self.yellow_lower = np.array([20,100,50], np.uint8)
        self.yellow_upper = np.array([40,255,255], np.uint8)


    def show_internet(self):
        import InternetCam
        InternetCam.run()
        while (self.running == True):
            if InternetCam.needs_frame == True:
                self.get_frame()
                ds_factor= 0.8
                frame=cv2.resize(self.frame,None,fx=ds_factor,fy=ds_factor, interpolation=cv2.INTER_AREA)
                ret, jpeg = cv2.imencode('.jpg', frame)
                frame = jpeg.tobytes()
                InternetCam.receive_frame(frame)
    
    def get_frame(self):
        ret, self.frame = self.cam.read()
        while ret is False:
            print("reading camera failed: Retrying")
            ret, self.frame = self.cam.read()
        if self.crop:
            self.frame = self.frame[int(len(self.frame)*0.35):int(len(self.frame)*0.65)]
        

        if cv2.waitKey(10) & 0xFF == ord('q'):
            return None
        else:
            return 1

    def get_buckets(self):
        self.get_frame()
        frame = self.frame
        blur_amt = 3
        #frame = cv2.GaussianBlur(self.frame, (blur_amt, blur_amt), 0)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        #                                        [  region1   ,  region2   ,  region3   ,...]   
        # will fill up with the following format [[size,color],[size,color],[size,color],...] one or zero objects in a region, the one most likely to be a bucket if there is one.
        objects = []
        for region in range(self.num_regions):
            objects.append([])

        red_mask = cv2.inRange(hsv_frame, self.red_lower1, self.red_upper1) + cv2.inRange(hsv_frame, self.red_lower2, self.red_upper2)
        red_mask = sharpen(red_mask)
        red_contours, hierarchy = cv2.findContours(red_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = self.add_objects(frame, objects, red_contours, "red")

        yellow_mask = cv2.inRange(hsv_frame, self.yellow_lower, self.yellow_upper)
        yellow_mask = sharpen(yellow_mask)
        yellow_contours, hierarchy = cv2.findContours(yellow_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = self.add_objects(frame, objects, yellow_contours, "yellow")

        blue_mask = cv2.inRange(hsv_frame, self.blue_lower, self.blue_upper)
        blue_mask = sharpen(blue_mask)
        blue_contours, hierarchy = cv2.findContours(blue_mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        frame = self.add_objects(frame, objects, blue_contours, "blue")


        if self.show:
            ### SHOW LINES
            #regions_size = self.width/self.num_regions
            #for region in range(self.num_regions-1):
            #    frame = cv2.line(frame, (int((region+1)*regions_size),0), (int((region+1)*regions_size),self.height), (255,255,255), 2)
            
            ### SHOW INDIVIDUAL COLOR
            #cv2.imshow('red', red_mask)
            #cv2.imshow('yellow', yellow_mask)
            #cv2.imshow('blue', blue_mask)

            cv2.imshow("my window", frame)

        return objects

    def add_objects(self, frame, objects, contours, color):
        regions_size = self.width/self.num_regions
        for contour in contours:
            area = cv2.contourArea(contour)
            if area > self.area_needed:
                x, y, w, h = cv2.boundingRect(contour)
                center = ( x+(w/2), y+(h/2) )
                obj_region = math.floor((center[0]/regions_size))
                objects[obj_region].append([area,color])

                if self.show:
                    frame = cv2.rectangle(frame, (x,y),(x+w,y+h), (255,200,200), 2)
                    cv2.putText(frame, color, (x, y), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (200, 200, 255), 2)
        return frame


if __name__ == "__main__":
    cam = Camera(5,show=True, internet_cam=False, area_needed=600, crop=False)
    print(cam.width)
    print(cam.width/cam.num_regions)

    while (True):
        if cam.get_frame() == None:
            break

        buckets = cam.get_buckets()
        print(buckets) 

    cam.cam.release()
    cv2.destroyAllWindows()
    sys.exit(0)