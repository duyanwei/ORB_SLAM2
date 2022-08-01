#!/usr/bin/env python
# -*-coding:utf-8 -*-
'''
@file Run_EuRoC_Stereo_Ubuntu20.04.py
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
SleepTime = 5  # 10 # 25 # second
FeaturePool = [1200]
SpeedPool = [1.0, 2.0, 3.0, 4.0, 5.0] # x
EnableViewer = 0
EnableLogging = 1
ORB_SLAM2_PATH = os.path.join(os.environ['SLAM_OPENSOURCE'], 'orb/ORB_SLAM2')

# ----------------------------------------------------------------------------------------------------------------------


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

        # create result dir first level
        cmd_mkdir = 'mkdir -p ' + result_dir
        subprocess.call(cmd_mkdir, shell=True)

        # loop over num of repeating
        for iteration in range(NumRepeating):

            # create result dir second level
            experiment_dir = os.path.join(result_dir, 'Round' + str(iteration + 1))
            cmd_mkdir = 'mkdir -p ' + experiment_dir
            subprocess.call(cmd_mkdir, shell=True)

            # loop over sequence
            for sn, sname in enumerate(SeqNameList):

                print(bcolors.ALERT + "====================================================================" + bcolors.ENDC)

                SeqName = SeqNameList[sn]
                print(bcolors.ALERT + '; Speed: ' + speed_str +
                      '; Round: ' + str(iteration + 1) + '; Seq: ' + SeqName)

                file_Setting = os.path.join(
                    ORB_SLAM2_PATH, 'Examples/Stereo/EuRoC_' + feature_str + '.yaml')
                file_Vocab = os.path.join(ORB_SLAM2_PATH, 'Vocabulary/ORBvoc.txt')
                file_data = os.path.join(DATA_ROOT, SeqName)
                file_timestamp = os.path.join(file_data, 'times.txt')
                file_traj = os.path.join(experiment_dir, SeqName)
                file_log = '> ' + file_traj + '_logging.txt' if EnableLogging else ''

                # compose cmd
                cmd_slam = \
                    ORB_SLAM2_PATH + '/Examples/Stereo/stereo_euroc' + \
                    ' ' + file_Vocab + \
                    ' ' + file_Setting + \
                    ' ' + file_data + \
                    ' ' + file_timestamp + \
                    ' ' + file_traj + \
                    ' ' + speed_str + \
                    ' ' + str(EnableViewer) + \
                    ' ' + file_log
                print(bcolors.WARNING + "cmd_slam: \n" + cmd_slam + bcolors.ENDC)

                print(bcolors.OKGREEN + "Launching SLAM" + bcolors.ENDC)
                # proc_slam = subprocess.Popen(cmd_slam, shell=True) # starts a new shell and runs the result
                subprocess.call(cmd_slam, shell=True)

                print(bcolors.OKGREEN + "Finished" + bcolors.ENDC)
                subprocess.call('pkill stereo_euroc', shell=True)
                time.sleep(SleepTime)
