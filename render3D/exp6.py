from direct.showbase.ShowBase import ShowBase
from panda3d.core import loadPrcFile, DirectionalLight, AmbientLight, LVecBase3f
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import Sequence
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

        self.current_pose = "a"
        self.gesture_data = self.loadAllPoseData()
        self.loadSignPoses(self.current_pose)

        # taskMgr.doMethodLater(5, self.animateToPose, "SwitchToNextPose")

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
        self.rthumb1 = self.rarm.find("**/t1")
        self.rthumb2 = self.rarm.find("**/t2")
        self.rindex1 = self.rarm.find("**/i1")
        self.rindex2 = self.rarm.find("**/i2")
        self.rindex3 = self.rarm.find("**/i3")
        self.rmiddle1 = self.rarm.find("**/m1")
        self.rmiddle2 = self.rarm.find("**/m2")
        self.rmiddle3 = self.rarm.find("**/m3")
        self.rring1 = self.rarm.find("**/r1")
        self.rring2 = self.rarm.find("**/r2")
        self.rring3 = self.rarm.find("**/r3")
        self.rpinky1 = self.rarm.find("**/p1")
        self.rpinky2 = self.rarm.find("**/p2")
        self.rpinky3 = self.rarm.find("**/p3")

        self.larm = loader.loadModel('character/LArmX.glb')
        self.larm.reparentTo(self.torso)
        self.lthumb1 = self.larm.find("**/t1")
        self.lthumb2 = self.larm.find("**/t2")
        self.lindex1 = self.larm.find("**/i1")
        self.lindex2 = self.larm.find("**/i2")
        self.lindex3 = self.larm.find("**/i3")
        self.lmiddle1 = self.larm.find("**/m1")
        self.lmiddle2 = self.larm.find("**/m2")
        self.lmiddle3 = self.larm.find("**/m3")
        self.lring1 = self.larm.find("**/r1")
        self.lring2 = self.larm.find("**/r2")
        self.lring3 = self.larm.find("**/r3")
        self.lpinky1 = self.larm.find("**/p1")
        self.lpinky2 = self.larm.find("**/p2")
        self.lpinky3 = self.larm.find("**/p3")

    def setupLights(self):
        mainLight = DirectionalLight('main light')
        mainLight.setShadowCaster(True)
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
            pose = poses[0]
        else:
            pose = poses

        if not pose:
            return

        l = pose["leftHand"]
        r = pose["rightHand"]
        self.larm.setPos(*l["pos"])
        self.larm.setHpr(*l["hpr"])
        self.rarm.setPos(*r["pos"])
        self.rarm.setHpr(*r["hpr"])

        def applyFingerPose(finger_parts, data):
            for part, pose_data in zip(finger_parts, data):
                part.setPos(*pose_data["pos"])
                part.setHpr(*pose_data["hpr"])

        if "fingers" in l:
            f = l["fingers"]
            if "thumb" in f:
                applyFingerPose([self.lthumb1, self.lthumb2], f["thumb"])
            if "index" in f:
                applyFingerPose([self.lindex1, self.lindex2, self.lindex3], f["index"])
            if "middle" in f:
                applyFingerPose([self.lmiddle1, self.lmiddle2, self.lmiddle3], f["middle"])
            if "ring" in f:
                applyFingerPose([self.lring1, self.lring2, self.lring3], f["ring"])
            if "pinky" in f:
                applyFingerPose([self.lpinky1, self.lpinky2, self.lpinky3], f["pinky"])

        if "fingers" in r:
            f = r["fingers"]
            if "thumb" in f:
                applyFingerPose([self.rthumb1, self.rthumb2], f["thumb"])
            if "index" in f:
                applyFingerPose([self.rindex1, self.rindex2, self.rindex3], f["index"])
            if "middle" in f:
                applyFingerPose([self.rmiddle1, self.rmiddle2, self.rmiddle3], f["middle"])
            if "ring" in f:
                applyFingerPose([self.rring1, self.rring2, self.rring3], f["ring"])
            if "pinky" in f:
                applyFingerPose([self.rpinky1, self.rpinky2, self.rpinky3], f["pinky"])

    def animateToPose(self, task):
        next_pose = "a" if self.current_pose == "default" else "default"
        poses = self.gesture_data.get(next_pose)

        if not poses:
            return Task.done

        sequence = []
        poseLen = len(poses) if isinstance(poses, list) else 1
        delay = 0.05
        time = 5 / (poseLen * 2 * 2) + delay

        def addFingerLerp(hand_data, finger_map):
            if "fingers" not in hand_data:
                return
            for name, parts in finger_map.items():
                if name in hand_data["fingers"]:
                    for part, pose_data in zip(parts, hand_data["fingers"][name]):
                        sequence.append(LerpPosInterval(part, time, LVecBase3f(*pose_data["pos"])))
                        sequence.append(LerpHprInterval(part, time, LVecBase3f(*pose_data["hpr"])))

        if isinstance(poses, list):
            for pose in poses:
                l = pose["leftHand"]
                r = pose["rightHand"]
                sequence.extend([
                    LerpPosInterval(self.larm, time, LVecBase3f(*l["pos"])),
                    LerpHprInterval(self.larm, time, LVecBase3f(*l["hpr"])),
                    LerpPosInterval(self.rarm, time, LVecBase3f(*r["pos"])),
                    LerpHprInterval(self.rarm, time, LVecBase3f(*r["hpr"]))
                ])
                addFingerLerp(l, {
                    "thumb": [self.lthumb1, self.lthumb2],
                    "index": [self.lindex1, self.lindex2, self.lindex3],
                    "middle": [self.lmiddle1, self.lmiddle2, self.lmiddle3],
                    "ring": [self.lring1, self.lring2, self.lring3],
                    "pinky": [self.lpinky1, self.lpinky2, self.lpinky3]
                })
                addFingerLerp(r, {
                    "thumb": [self.rthumb1, self.rthumb2],
                    "index": [self.rindex1, self.rindex2, self.rindex3],
                    "middle": [self.rmiddle1, self.rmiddle2, self.rmiddle3],
                    "ring": [self.rring1, self.rring2, self.rring3],
                    "pinky": [self.rpinky1, self.rpinky2, self.rpinky3]
                })
        else:
            l = poses["leftHand"]
            r = poses["rightHand"]
            sequence.extend([
                LerpPosInterval(self.larm, time, LVecBase3f(*l["pos"])),
                LerpHprInterval(self.larm, time, LVecBase3f(*l["hpr"])),
                LerpPosInterval(self.rarm, time, LVecBase3f(*r["pos"])),
                LerpHprInterval(self.rarm, time, LVecBase3f(*r["hpr"]))
            ])
            addFingerLerp(l, {
                "thumb": [self.lthumb1, self.lthumb2],
                "index": [self.lindex1, self.lindex2, self.lindex3],
                "middle": [self.lmiddle1, self.lmiddle2, self.lmiddle3],
                "ring": [self.lring1, self.lring2, self.lring3],
                "pinky": [self.lpinky1, self.lpinky2, self.lpinky3]
            })
            addFingerLerp(r, {
                "thumb": [self.rthumb1, self.rthumb2],
                "index": [self.rindex1, self.rindex2, self.rindex3],
                "middle": [self.rmiddle1, self.rmiddle2, self.rmiddle3],
                "ring": [self.rring1, self.rring2, self.rring3],
                "pinky": [self.rpinky1, self.rpinky2, self.rpinky3]
            })

        Sequence(*sequence).start()
        self.current_pose = next_pose
        return task.again

demox = MyDemo()
demox.run()
