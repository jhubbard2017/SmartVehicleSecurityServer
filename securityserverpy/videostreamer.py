# -*- coding: utf-8 -*-
#
# module for retrieving camera stream bytes to send from server to clients
#

import cv2

from securityserverpy import _logger


class VideoStreamer(object):
    """manages and controls camera stream data"""

    _STREAM_MIN_AREA = 500

    def __init__(self, camera=0):
        """set the video object from the camera number

        Default camera # is 0. This simply enables usb camera to be used by openCV
        """
        self._camera = camera
        self.stream = None
        self.firstframe = None
        self._stream_running = False

    def start_stream(self):
        """starts the stream for the camera"""
        self.stream = cv2.VideoCapture(self._camera)
        if not self._stream_running:
            self._stream_running = True

    def stop_stream(self):
        """stops the stream for the camera"""
        self.stream.release()
        if self._stream_running:
            self._stream_running = False

    def get_frame(self):
        """reads a frame from the camera stream and converts it to bytes to send

        returns:
            bytes
        """
        success, image = self.stream.read()
        gray_image = self.get_gray_frame(image)
        if self.firstframe is None:
            self.firstframe = gray_image
        else:
            motion_detected = self.motion_detected(gray_image)
        ret, image_jpeg = cv2.imencode('.jpg', image)
        return success, image_jpeg.tobytes(), motion_detected

    def get_gray_frame(self, frame):
        """converts frame to grayscale

        args:
            frame: image

        returns:
            image
        """
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        return gray

    def motion_detected(self, frame):
        """compares frames and determines of motion has been detected or not

        The first frame is considered a `no motion` frame. Comparing each of the new frames to the first frame
        will allow us to determine if motion has been detected.
            - If one of the contours in the threshold of the frame is greater than VideoStreamer._STREAM_MIN_AREA,
                    then motion has been detected
            - If one of the contours in the threshold of the frame is smaller than VideoStreamer._STREAM_MIN_AREA,
                    then motion has not been detected

        args:
            frame: image object

        returns:
            bool
        """
        detected = False
        # compute the absolute difference between the current frame and
        # first frame
        frameDelta = cv2.absdiff(self.firstframe, gray)
        thresh = cv2.threshold(frameDelta, 25, 255, cv2.THRESH_BINARY)[1]

        # dilate the thresholded image to fill in holes, then find contours
        # on thresholded image
        thresh = cv2.dilate(thresh, None, iterations=2)
        (cnts, _) = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL,
                                     cv2.CHAIN_APPROX_SIMPLE)

        # loop over the contours
        for c in cnts:
            # if the contour is too small, ignore it
            if cv2.contourArea(c) < VideoStreamer._STREAM_MIN_AREA:
                continue

            # compute the bounding box for the contour, draw it on the frame,
            # and update the text
            (x, y, w, h) = cv2.boundingRect(c)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
            detected = True

        return detected

    @property
    def camera(self):
        return self._camera

    @camera.setter
    def camera(self, value):
        self._camera = value

    @property
    def stream_running(self):
        return self._stream_running

    @stream_running.setter
    def stream_running(self, value):
        self._stream_running = value