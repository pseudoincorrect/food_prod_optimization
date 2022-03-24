import os
import torch
import numpy as np
import lib.FCN_NetModel as FCN  # The net Class
import lib.CategoryDictionary as CatDic
import cv2
import time

# Use GPU or CPU  for prediction (GPU faster but demend nvidia GPU and CUDA
# installed else set USE_GPU to False)
USE_GPU = False
# wether to freeze the batch statics on prediction
# setting this true or false might change the prediction mostly False work better
FREEZE_BATCH_NORM_STATISTICS = False
# path to the pretrain model
TRAINED_MODEL_PATH = "../vision_model/model.torch"
# Amount of picture parts
PART_COUNT = 3


class Processing():

    def __init__(self, img_reader, push_msg):
        # Create net and load pretrained encoder path
        self._net = FCN.Net(CatDic.CatNum)
        if USE_GPU == True:
            print("Loading model usind GPU")
            self._net.load_state_dict(torch.load(TRAINED_MODEL_PATH))
        else:
            print("Loading model usind CPU")
            self._net.load_state_dict(torch.load(TRAINED_MODEL_PATH,
                                                 map_location=torch.device('cpu')))
        self.img_reader = img_reader
        self.push_msg = push_msg

    def sendData(self, heights):
        timeStamp = str(time.time())
        height = ",".join(str(item) for item in heights)
        data_point = str(timeStamp)+","+str(height)+'\n'
        self.push_msg(data_point)

    def getTopBottom(self, matrix: np.matrix):
        '''
        we start from the bottom
        if we get a high value, we store it as first bottom
        and only if we get a high value do we continue
        then we keep on moving until we get a row with no high
        values in them
        '''
        bottom = matrix.shape[0]-1
        while bottom > 0:
            if any(matrix[bottom]) == 1:
                break
            bottom -= 1

        top = bottom
        while top > 0:
            if all(matrix[top] == 0):
                break
            top -= 1

        return top, bottom

    def process_frame(self):
        '''
        Process a frame by resizing it and run ML model to output command
        '''
        # Capture frame-by-frame
        frame = self.img_reader()

        Im = frame
        h, w, d = Im.shape

        # Image Formatting
        widthSm = w//PART_COUNT
        newImgs = []
        for i in range(PART_COUNT):
            newImg = Im[:, i*widthSm:(i+1)*widthSm]
            newImgs.append(newImg)

        heights = []
        counter = 0
        for Im in newImgs:
            h, w, _ = Im.shape

            # Image larger then 840X840 are shrinked (this is not essential, but the
            #  net results might degrade when using to large images
            r = np.max([h, w])
            if r > 840:
                fr = 840/r
                Im = cv2.resize(Im, (int(w*fr), int(h*fr)))
            Imgs = np.expand_dims(Im, axis=0)
            if not (type(Im) is np.ndarray):
                continue

            # Make Prediction
            with torch.autograd.no_grad():
                # Run net inference and get prediction
                OutProbDict, OutLabelsDict = self._net.forward(
                    Images=Imgs,
                    TrainMode=False,
                    UseGPU=USE_GPU,
                    FreezeBatchNormStatistics=FREEZE_BATCH_NORM_STATISTICS)

            for nm in OutLabelsDict:
                Lb = OutLabelsDict[nm].data.cpu().numpy()[0].astype(np.uint8)

                if Lb.mean() < 0.001:
                    continue
                if nm == 'Ignore':
                    continue
        #         if nm!="Filled": continue
                # Lb is a 2d matrix which is made 1 where the
                # material is present

                ImOverlay1 = Im.copy()
                ImOverlay1[:, :, 0][Lb == 1] = 255
                ImOverlay1[:, :, 1][Lb == 1] = 0
                ImOverlay1[:, :, 2][Lb == 1] = 255

                height = 0
                if nm == "Granular":
                    # print("nm is ", nm)
                    t, b = self.getTopBottom(Lb)
                    # print("top:", t, "bottom", b)
                    print("container ", counter, "height :", b-t)
                    height = b-t
                    heights.append(height)
                    # heights[counter] = height
            counter += 1

        if len(heights) == PART_COUNT:
            self.sendData(heights)
        else:
            print("not all containers have been recognized")

        # display frames on the screen
        # for i in range(len(newImgs)):
        #     cv2.imshow('frame'+str(i), newImgs[i])

        # Waits for a user input to quit the application
        if cv2.waitKey(1) & 0xFF == ord('q'):
            return 1

        return 0
