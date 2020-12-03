#!/usr/bin/env python3

from threading import Thread, Semaphore, Lock
import cv2, os, queue

class Queue:
    def __init__(self):
        self.queue = []
        self.semaphoreUsed = Semaphore(0)
        self.semaphoreCapacity = Semaphore(10)
        self.lock = Lock()

    def enqueue(self, item):
        self.semaphoreCapacity.acquire()
        self.lock.acquire()
        self.queue.append(item)
        self.lock.release()
        self.semaphoreUsed.release()

    def dequeue(self):
        self.semaphoreUsed.acquire()
        self.lock.acquire()
        item = self.queue.pop(0)
        self.lock.release()
        self.semaphoreCapacity.release()
        return item

def extract(clip, originalFrames):
    #Initialize frame count
    count =  0

    #load clip
    vidcap = cv2.VideoCapture(clip)

    success, image = vidcap.read()

    print(f'Reading frame {count} {success}')

    while success:
        #add frames
        originalFrames.enqueue(image)

        success, image = vidcap.read()
        print(f'Reading frame {count}')
        count += 1


    originalFrames.enqueue('!')


def convertGray(originalFrames, grayscaleFrames):

    count = 0


    while True:
        print('Converting frame {count}')

        getFrame = originalFrames.dequeue()
        if getFrame == '!':
            break

        # convert the image to grayscale
        grayscaleFrame = cv2.cvtColor(getFrame, cv2.COLOR_BGR2GRAY)
        #grayscale frames to queue
        grayscaleFrames.enqueue(grayscaleFrame)
        count += 1

    grayscaleFrames.enqueue('!')

def play(grayscaleFrames):
    #Initialize frame count
    count = 0

    #go through each of the gray frames
    while True:
        print(f'Displaying Frame{count}')

        #get tHe next frame
        frame = grayscaleFrames.dequeue()
        if frame == '!':
            break

        # display the image in a window called "video" and wait 42ms
                # before displaying the next frame
        cv2.imshow('Video', frame)
        if(cv2.waitKey(42) and 0xFF == ord("q")):
           break

        count += 1


    cv2.destroyAllWindows()

#clip to load
clip = 'clip.mp4'

#make queues
originalFrames = Queue()
grayscaleFrames = Queue()

#make each thread target each def with their parameters as the args
extractThread = Thread(target = extract, args = (clip, originalFrames)).start()
convertThread = Thread(target = convertGray, args = (originalFrames, grayscaleFrames)).start()
displayThread = Thread(target = play, args = (grayscaleFrames,)).start()
