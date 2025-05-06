from PIL.ImageChops import offset
from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, DirectionalLight, AmbientLight, LVecBase3f
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import Sequence, Wait
from direct.task import Task
import json

loadPrcFile("settings.prc")

class MyDemo(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.loadModels()
        self.setupLights()
        self.setupCamera()
        self.setupSkybox()

        self.current_pose = "default"
        self.gesture_data = self.loadAllPoseData()
        self.loadSignPoses("default")

        taskMgr.doMethodLater(5, self.animateToPose, "SwitchToNextPose")

    def setupCamera(self):
        self.disableMouse()
        self.camera.setPos(0, -14, 3.25)

    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)

    def loadModels(self):
        self.torso = loader.loadModel('character/torso.glb')
        self.torso.setPos(0, 0, 0)
        self.torso.reparentTo(render)

        self.rarm = loader.loadModel('character/RArmX.glb')
        self.rarm.reparentTo(self.torso)

        self.larm = loader.loadModel('character/LArmX.glb')
        self.larm.reparentTo(self.torso)

    def setupLights(self):
        mainLight = DirectionalLight('main light')
        # mainLight.setShadowCaster(True)
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

        render.setShaderAuto()

    def loadAllPoseData(self):
        with open("sign_poses.json", "r") as f:
            return json.load(f)

    def loadSignPoses(self, name):
        poses = self.gesture_data.get(name)
        if isinstance(poses, list):
            pose = poses[0]  # Use first frame for setup
        else:
            pose = poses

        if pose:
            l = pose["leftHand"]
            r = pose["rightHand"]
            self.larm.setPos(*l["pos"])
            self.larm.setHpr(*l["hpr"])
            self.rarm.setPos(*r["pos"])
            self.rarm.setHpr(*r["hpr"])

    def animateToPose(self, task):
        next_pose = "hi" if self.current_pose == "default" else "default"
        poses = self.gesture_data.get(next_pose)

        if not poses:
            return Task.done

        sequence = []
        poseLen = len(poses)
        parts = 2
        delay = 0.05
        time = 5 / (poseLen * parts * 2) + delay

        if isinstance(poses, list):

            for pose in poses:
                sequence.extend([
                    LerpPosInterval(self.larm, time, LVecBase3f(*pose["leftHand"]["pos"])),
                    LerpHprInterval(self.larm, time, LVecBase3f(*pose["leftHand"]["hpr"])),
                    LerpPosInterval(self.rarm, time, LVecBase3f(*pose["rightHand"]["pos"])),
                    LerpHprInterval(self.rarm, time, LVecBase3f(*pose["rightHand"]["hpr"])),
                ])
        else:
            pose = poses
            sequence.extend([
                LerpPosInterval(self.larm, time, LVecBase3f(*pose["leftHand"]["pos"])),
                LerpHprInterval(self.larm, time, LVecBase3f(*pose["leftHand"]["hpr"])),
                LerpPosInterval(self.rarm, time, LVecBase3f(*pose["rightHand"]["pos"])),
                LerpHprInterval(self.rarm, time, LVecBase3f(*pose["rightHand"]["hpr"]))
            ])

        Sequence(*sequence).start()
        self.current_pose = next_pose
        return task.again

demox = MyDemo()
demox.run()
