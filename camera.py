import pypylon.pylon as pylon
from datetime import datetime
import time

import atexit

class ImageEventPrinter(pylon.ImageEventHandler):
    def OnImageGrabbed(self, camera, grabResult):
        # Image grabbed successfully?
        if grabResult.GrabSucceeded():
            print(grabResult.ChunkTimestamp.Value)

tl_factory = pylon.TlFactory.GetInstance()

camera = pylon.InstantCamera(pylon.TlFactory.GetInstance().CreateFirstDevice())

camera.Open()
atexit.register(camera.Close)

camera.RegisterImageEventHandler(ImageEventPrinter(), pylon.RegistrationMode_ReplaceAll, pylon.Cleanup_Delete)

camera.GevSCPD.SetValue(1000)
camera.GevIEEE1588.SetValue(True)
camera.ChunkModeActive.SetValue(True)
camera.ChunkSelector.SetValue("Timestamp")
camera.ChunkEnable.SetValue(True)
camera.TriggerSelector.SetValue("FrameStart")
camera.TriggerMode.SetValue("On")

camera.StartGrabbing(pylon.GrabStrategy_OneByOne, pylon.GrabLoop_ProvidedByInstantCamera)
atexit.register(camera.StopGrabbing)

while True:
    time.sleep(0.05)