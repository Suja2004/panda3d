from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import loadPrcFile, DirectionalLight, AmbientLight ,WindowProperties

# Load settings from external config (optional)
loadPrcFile("settings.prc")

class MyDemo(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.loadModels()
        self.setupLights()
        self.setupCamera()
        self.setupSkybox()

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
        rarm = loader.loadModel('character/rightHand.glb')
        rarm.setPos(-2.2, -1, 1.1)
        rarm.setH(90) #z
        rarm.setP(-90) #x
        rarm.setR(-90) #y
        rarm.reparentTo(render)

        larm = loader.loadModel('character/leftHand.glb')
        larm.setPos(2.2, -1, 1.1)
        larm.setH(90)
        larm.setP(-90)
        larm.setR(-90)
        larm.reparentTo(render)

        self.demo1 = loader.loadModel('character/torso.glb')
        self.demo1.setPos(0, 0, 0)
        self.demo1.reparentTo(render)

    def setupLights(self):
        # Directional light (sunlight)
        mainLight = DirectionalLight('main light')
        mainLight.setShadowCaster(True)
        mainLightNodePath = render.attachNewNode(mainLight)
        mainLightNodePath.setHpr(30, -60, 0)
        render.setLight(mainLightNodePath)

        # Ambient light for soft background illumination
        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.3, 0.3, 0.3, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)

        # Enable automatic shaders for better lighting effects
        render.setShaderAuto()

demox = MyDemo()
demox.run()
