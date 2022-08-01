#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@file Evaluate_EuRoC_Stereo.py
@author Yanwei Du (duyanwei0702@gmail.com)
@date 07-12-2022
@version 1.0
@license Copyright (c) 2022
@desc None
'''


# This script is to run all the experiments in one program

import os
import subprocess
import time

DATA_ROOT = '/mnt/DATA/Datasets/EuRoC/'
SeqNameList = [
    'MH_01_easy', 'MH_02_easy', 'MH_03_medium',
    'MH_04_difficult', 'MH_05_difficult',
    'V1_01_easy', 'V1_02_medium', 'V1_03_difficult',
    'V2_01_easy', 'V2_02_medium', 'V2_03_difficult']
RESULT_ROOT = os.path.join(
    os.environ['SLAM_RESULT'], 'ORB_SLAM2/EuRoC/Stereo/')
NumRepeating = 10
SleepTime = 1  # 10 # 25 # second
# FeaturePool = [500, 800, 1200, 1500]
FeaturePool = [1200]
SpeedPool = [1.0, 2.0, 3.0, 4.0, 5.0] # x
ORB_SLAM2_PATH = os.path.join(os.environ['SLAM_OPENSOURCE'], 'orb/ORB_SLAM2')
GT_ROOT = os.path.join(DATA_ROOT, 'gt_pose')
SENSOR = 'cam0'
SaveResult = 1

# ----------------------------------------------------------------------------------------------------------------------


def call_evaluation(eval, gt, est, options, save):
    cmd_eval = eval + ' ' + gt + ' ' + est + ' ' + options
    if save:
        result = os.path.splitext(est)[0] + '.zip'
        cmd_eval = cmd_eval + ' --save_results ' + result

    print(bcolors.WARNING + "cmd_eval: \n" + cmd_eval + bcolors.ENDC)
    print(bcolors.HEADER + os.path.basename(est))
    subprocess.call(cmd_eval, shell=True)


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    ALERT = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

for feature in FeaturePool:

    feature_str = str(feature)
    result_1st_dir = os.path.join(RESULT_ROOT, feature_str)

    # loop over play speed
    for speed in SpeedPool:

        speed_str = str(speed)
        result_dir = os.path.join(result_1st_dir, 'Fast' + speed_str)

        # loop over num of repeating
        for iteration in range(NumRepeating):

            experiment_dir = os.path.join(result_dir, 'Round' + str(iteration + 1))

            # loop over sequence
            for sn, sname in enumerate(SeqNameList):

                print(bcolors.ALERT + "====================================================================" + bcolors.ENDC)

                SeqName = SeqNameList[sn]
                print(bcolors.ALERT + '; Speed: ' + speed_str +
                    '; Round: ' + str(iteration + 1) + '; Seq: ' + SeqName)

                file_gt = os.path.join(GT_ROOT, SeqName + '_' + SENSOR + '.txt')
                file_camera_traj = os.path.join(
                    experiment_dir, SeqName+'_CameraTrajectory.txt')
                file_camera_traj_tracking = os.path.join(
                    experiment_dir, SeqName + '_CameraTrajectory_tracking.txt')
                file_keyframe_traj = os.path.join(
                    experiment_dir, SeqName + '_KeyFrameTrajectory.txt')
                file_eval = 'evo_ape tum'
                options = '-va'

                if not os.path.exists(file_gt) or not os.path.exists(file_camera_traj):
                    print('missing gt file or est file')
                    continue

                # evaluate
                call_evaluation(file_eval, file_gt,
                                file_camera_traj, options, SaveResult)
                call_evaluation(file_eval, file_gt,
                                file_camera_traj_tracking, options, SaveResult)
                call_evaluation(file_eval, file_gt,
                                file_keyframe_traj, options, SaveResult)

                print(bcolors.OKGREEN + "Finished" + bcolors.ENDC)
                time.sleep(SleepTime)
