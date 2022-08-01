#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@file Collect_evaluation_result.py
@author Yanwei Du (duyanwei0702@gmail.com)
@date 07-20-2022
@version 1.0
@license Copyright (c) 2022
@desc None
'''

import json
import numpy as np
import os
import zipfile


SeqNameList = [
    'MH_01_easy', 'MH_02_easy', 'MH_03_medium',
    'MH_04_difficult', 'MH_05_difficult',
    'V1_01_easy', 'V1_02_medium', 'V1_03_difficult',
    'V2_01_easy', 'V2_02_medium', 'V2_03_difficult']
RESULT_ROOT = os.path.join(
    os.environ['SLAM_RESULT'], 'ORB_SLAM2/EuRoC/Stereo/')
NumRepeating = 10
SleepTime = 1  # 10 # 25 # second
FeaturePool = [500, 800, 1200, 1500]
SpeedPool = [1.0, 2.0, 3.0, 4.0, 5.0]  # x
ResultFile = ['CameraTrajectory_tracking', 'CameraTrajectory', 'KeyFrameTrajectory']

# ----------------------------------------------------------------------------------------------------------------------


for feature in FeaturePool:

    feature_str = str(feature)
    result_1st_dir = os.path.join(RESULT_ROOT, feature_str)

    rmse_table = np.zeros((len(ResultFile), len(SpeedPool),
                           len(SeqNameList), NumRepeating))

    mean_timing_table = np.full((len(SpeedPool),
                           len(SeqNameList), NumRepeating), -1.0)
    median_timing_table = np.full_like(mean_timing_table, -1.0)

    # loop over play speed
    for j, speed in enumerate(SpeedPool):

        speed_str = str(speed)
        result_dir = os.path.join(result_1st_dir, 'Fast' + speed_str)

        # loop over num of repeating
        for l in range(NumRepeating):

            experiment_dir = os.path.join(result_dir, 'Round' + str(l + 1))

            # loop over sequence
            for k, sname in enumerate(SeqNameList):

                # collect rmse
                for i, result_name in enumerate(ResultFile):
                    result = os.path.join(
                        experiment_dir, sname + '_' + result_name + '.zip')
                    if not os.path.exists(result):
                        continue
                    # read
                    # print(result)
                    with zipfile.ZipFile(result, 'r') as z:
                        with z.open('stats.json') as f:
                            data = f.read()
                            rmse_table[i, j, k, l] = json.loads(data)['rmse']
                # @TODO: the following code can be optimized!!!
                # collect tracking failure info
                file_log = os.path.join(experiment_dir, sname + '_logging.txt')
                # wanted = ['Total', 'processed images:', 'frame count:']
                wanted = ['frame count:', 'median tracking time:', 'mean tracking time:']
                candidates = []
                with open(file_log, 'r') as log_f:
                    lines = log_f.read().splitlines()
                    for line in lines:
                        for word in wanted:
                            if line.startswith(word):
                                candidates.append(line)
                tracking_ratio = 0.0
                if len(candidates) == 0:
                    print(
                        f'tracking failed: Speed {speed}, Seq {sname}, Round {l+1}')
                else:
                    # read the image number in pool
                    # total_images = int(candidates[0].split()[1])
                    # read the processed image number
                    # processed_images = int(candidates[1].split()[2])
                    # read the camera trajectory status
                    # frame_count = int((candidates[2].split()[2]).split(',')[0])
                    # good_frame_count = int(
                    # (candidates[2].split()[6]).split(',')[0])
                    # read the camera real time tracking status
                    tracking_frame_count = int(
                        (candidates[2].split()[2]).split(',')[0])
                    tracking_good_frame_count = int(
                        (candidates[2].split()[6]).split(',')[0])
                    # print info
                    # print(total_images, processed_images, frame_count,
                    #   good_frame_count, tracking_frame_count, tracking_good_frame_count)
                    tracking_ratio = float(tracking_good_frame_count) / tracking_frame_count


                    # timing
                    median_timing_table[j, k, l] = float(candidates[0].split()[-1])
                    mean_timing_table[j, k, l] = float(candidates[1].split()[-1])
                if tracking_ratio < 0.6:
                    rmse_table[:, j, k, l] = -1
                    print(
                        f'tracking failed: Speed {speed}, Seq {sname}, Round {l+1}')

    mean_timing_table = mean_timing_table.reshape(-1, NumRepeating)
    median_timing_table = median_timing_table.reshape(-1, NumRepeating)
    # save rmse
    for i, result_name in enumerate(ResultFile):
        output = os.path.join(result_1st_dir, result_name + '.txt')
        mn, nn, pn, qn = rmse_table.shape
        # the extra two column stores mean and median
        cur_table = np.full((nn * pn, qn + 4), -1.0)
        cur_table[:, 0:qn] = rmse_table[i, :, :, :].reshape(nn * pn, qn)
        for row in range(cur_table.shape[0]):
            indices = cur_table[row, :] > 0.0
            if np.sum(indices) > 0:
                cur_table[row, qn] = np.mean(cur_table[row, indices])
                cur_table[row, qn + 1] = np.median(cur_table[row, indices])
                cur_table[row, qn + 2] = np.mean(mean_timing_table[row, indices[:-4]])
                cur_table[row, qn + 3] = np.median(median_timing_table[row, indices[:-4]])
            else:
                cur_table[row, qn] = -1
                cur_table[row, qn + 1] = -1
        np.savetxt(output, cur_table, fmt='%.6f', delimiter=',')
