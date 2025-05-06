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
        self.camera.setPos(0, -16, 5.25)
        # self.camera.lookAt(0, 0, 0)

    def setupSkybox(self):
        skybox = loader.loadModel('skybox/skybox.egg')
        skybox.setScale(500)
        skybox.setBin('background', 1)
        skybox.setDepthWrite(0)
        skybox.setLightOff()
        skybox.reparentTo(render)

    def loadModels(self):
        # Create a 3x3 grid of grass blocks
        head = loader.loadModel('grass-block.glb')
        head.setPos(0, 0, 7.5)
        head.reparentTo(render)

        head = loader.loadModel('grass-block.glb')
        head.setPos(0, -1, 7)
        # head.setHpr(0,-45,45)
        head.setScale(.5, 0.5, .5)
        head.reparentTo(render)

        lchest = loader.loadModel('grass-block.glb')
        lchest.setPos(1, 0, 5)
        lchest.set_p(90)
        lchest.reparentTo(render)

        rchest = loader.loadModel('grass-block.glb')
        rchest.setPos(-1, 0, 5)
        rchest.set_p(90)
        rchest.reparentTo(render)

        lsholder = loader.loadModel('grass-block.glb')
        lsholder.setPos(2.5, 0, 5)
        lsholder.setScale(0.5, 1, 1)
        lsholder.reparentTo(render)

        rsholder = loader.loadModel('grass-block.glb')
        rsholder.setPos(-2.5, 0, 5)
        rsholder.setScale(0.5, 1, 1)
        rsholder.reparentTo(render)

        larm = loader.loadModel('grass-block.glb')
        larm.setPos(2.5, 0, 3)
        larm.setScale(0.5, 1, 1)
        larm.reparentTo(render)

        rarm = loader.loadModel('grass-block.glb')
        rarm.setPos(-2.5, 0, 3)
        rarm.setScale(0.5, 1, 1)
        rarm.reparentTo(render)

        stomach = loader.loadModel('grass-block.glb')
        stomach.setPos(0, 0, 3)
        stomach.set_p(90)
        stomach.reparentTo(render)

        # self.demo1 = loader.loadModel('char1.glb')
        # self.demo1.setPos(0, 0, 0)
        # self.demo1.reparentTo(render)

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
