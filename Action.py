# -*- coding: utf-8 -*-
"""
Created on Sun Jun 30 10:51:08 2019

@author: 11712
"""

# !/usr/bin/python
# _*_ coding:utf-8  -*-
import time
import os
import RobotApi

RobotApi.ubtRobotInitialize()
gIPAddr = ""
robotinfo = RobotApi.UBTEDU_ROBOTINFO_T()

robotinfo.acName = "Yanshee_65CE"
ret = RobotApi.ubtRobotDiscovery("SDK", 15, robotinfo)

if 0 != ret:
    print("Return value: %d" % ret)
    exit(1)
gIPAddr = robotinfo.acIPAddr
ret = RobotApi.ubtRobotConnect("SDK", "1", gIPAddr)
if 0 != ret:
    print("Can not connect to robot %s" % robotinfo.acNme)
    exit(1)


def action(action_name, times):
    ret = RobotApi.ubtStartRobotAction(action_name, times)


def end():
    RobotApi.ubtRobotDisconnect("SDK", "1", gIPAddr)
    RobotApi.ubtRobotDeinitialize()
