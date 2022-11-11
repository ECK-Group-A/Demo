# -- coding: utf-8 --

from ast import And
import sys
import copy
import os
import termios

from ctypes import *

sys.path.append("MvImport")
from MvCameraControl_class import *

winfun_ctype = CFUNCTYPE

stEventInfo = POINTER(MV_EVENT_OUT_INFO)
pData = POINTER(c_ubyte)
EventInfoCallBack = winfun_ctype(None, stEventInfo, c_void_p)

def event_callback(pEventInfo, pUser):
	stPEventInfo = cast(pEventInfo, POINTER(MV_EVENT_OUT_INFO)).contents
	nTimestamp = stPEventInfo.nTimestampHigh
	nTimestamp = (nTimestamp << 32) + stPEventInfo.nTimestampLow
	if stPEventInfo and nTimestamp > 10e15:
		print ("Timestamp[%d]" % (nTimestamp))
		log = open("camera.log", "a")
		log.write(str(nTimestamp) + '\n')
		log.close()

CALL_BACK_FUN = EventInfoCallBack(event_callback)

def press_any_key_exit():
	fd = sys.stdin.fileno()
	old_ttyinfo = termios.tcgetattr(fd)
	new_ttyinfo = old_ttyinfo[:]
	new_ttyinfo[3] &= ~termios.ICANON
	new_ttyinfo[3] &= ~termios.ECHO
	#sys.stdout.write(msg)
	#sys.stdout.flush()
	termios.tcsetattr(fd, termios.TCSANOW, new_ttyinfo)
	try:
		os.read(fd, 7)
	except:
		pass
	finally:
		termios.tcsetattr(fd, termios.TCSANOW, old_ttyinfo)

def PrintDeviceInfo(deviceList):
	for i in range(0, deviceList.nDeviceNum):
		mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
		if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
			print ("\ngige device: [%d]" % i)
			strModeName = ""
			for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chModelName:
				strModeName = strModeName + chr(per)
			print ("device model name: %s" % strModeName)

			nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
			nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
			nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
			nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
			print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
		elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
			print ("\nu3v device: [%d]" % i)
			strModeName = ""
			for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chModelName:
				if per == 0:
					break
				strModeName = strModeName + chr(per)
			print ("device model name: %s" % strModeName)

			strSerialNumber = ""
			for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
				if per == 0:
					break
				strSerialNumber = strSerialNumber + chr(per)
			print ("user serial number: %s" % strSerialNumber)

if __name__ == "__main__":

	deviceList = MV_CC_DEVICE_INFO_LIST()
	tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
	
	# Enum device
	ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
	if ret != 0:
		print ("enum devices fail! ret[0x%x]" % ret)
		sys.exit()

	if deviceList.nDeviceNum == 0:
		print ("find no device!")
		sys.exit()

	print ("find %d devices!" % deviceList.nDeviceNum)

	PrintDeviceInfo(deviceList)


	nConnectionNum = 0 #this is the index of the camera. if there is only one it's 0 otherwise just count

	if int(nConnectionNum) >= deviceList.nDeviceNum:
		print ("intput error!")
		sys.exit()
	
	#Creat Camera Object
	cam = MvCamera()

	#Select device and create handle
	stDeviceList = cast(deviceList.pDeviceInfo[int(nConnectionNum)], POINTER(MV_CC_DEVICE_INFO)).contents

	ret = cam.MV_CC_CreateHandle(stDeviceList)
	if ret != 0:
		print ("create handle fail! ret[0x%x]" % ret)
		sys.exit()

	#Open device
	ret = cam.MV_CC_OpenDevice(MV_ACCESS_Exclusive, 0)
	if ret != 0:
		print ("open device fail! ret[0x%x]" % ret)
		sys.exit()

	print ("start importing the camera properties to the file")
	print ("wait......")

	#Import the camera properties from the file
	ret = cam.MV_CC_FeatureLoad("FeatureFile.ini")
	if MV_OK != ret:
		print ("load feature fail! ret [0x%x]" % ret)
	print ("finish import the camera properties from the file")

#Detection network optimal package size(It only works for the GigE camera)
	if stDeviceList.nTLayerType == MV_GIGE_DEVICE:
		nPacketSize = cam.MV_CC_GetOptimalPacketSize()
		if int(nPacketSize) > 0:
			ret = cam.MV_CC_SetIntValue("GevSCPSPacketSize",nPacketSize)
			if ret != 0:
				print ("Warning: Set Packet Size fail! ret[0x%x]" % ret)
		else:
			print ("Warning: Get Packet Size fail! ret[0x%x]" % nPacketSize)

	#Set trigger mode as on
	ret = cam.MV_CC_SetEnumValue("TriggerMode", MV_TRIGGER_MODE_ON)
	if ret != 0:
		print ("set trigger mode fail! ret[0x%x]" % ret)
		sys.exit()

	#set trigger source as hardware
	ret = cam.MV_CC_SetEnumValue("TriggerSource", MV_TRIGGER_SOURCE_LINE0)
	if ret != 0:
		print ("set trigger source fail! ret[0x%x]" % ret)
		sys.exit()

	#Set Event of FrameStart On
	ret = cam.MV_CC_SetEnumValueByString("EventSelector","FrameStart")
	if ret != 0:
		print ("set enum value by string fail! ret[0x%x]" % ret)
		sys.exit()

	ret = cam.MV_CC_SetEnumValueByString("EventNotification","On")
	if ret != 0:
		print ("set enum value by string fail! ret[0x%x]" % ret)
		sys.exit()

	#Register event callback
	ret = cam.MV_CC_RegisterEventCallBackEx("FrameStart", CALL_BACK_FUN,None)
	if ret != 0:
		print ("register event callback fail! ret [0x%x]" % ret)
		sys.exit()

	#Start grab image
	cam.MV_CC_StartGrabbing()
	if ret != 0:
		print ("start grabbing fail! ret[0x%x]" % ret)
		sys.exit()

	print ("press a key to stop grabbing.")
	press_any_key_exit()

	#Stop grab image
	ret = cam.MV_CC_StopGrabbing()
	if ret != 0:
		print ("stop grabbing fail! ret[0x%x]" % ret)
		sys.exit()

	#Close device
	ret = cam.MV_CC_CloseDevice()
	if ret != 0:
		print ("close deivce fail! ret[0x%x]" % ret)
		sys.exit()

	#Destroy handle
	ret = cam.MV_CC_DestroyHandle()
	if ret != 0:
		print ("destroy handle fail! ret[0x%x]" % ret)
		sys.exit()
