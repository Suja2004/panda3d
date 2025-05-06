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

        # self.captureMouse()
        # self.setupControls()

        # taskMgr.add(self.update, 'update')

    def update(self,task):
        dt = globalClock.getDt()

        if self.cameraSwingActivated:
            md = self.win.getPointer(0)
            mouseX = md.getX()
            mouseY = md.getY()

            mouseChangeX = mouseX - self.lastMouseX
            mouseChangeY = mouseY - self.lastMouseY

            self.cameraSwingFactor = 18

            currentH = self.camera.getH()
            currentP = self.camera.getP()

            self.camera.setHpr(
                currentH - mouseChangeX * dt * self.cameraSwingFactor,
                min(90, max(-90, currentP - mouseChangeY * dt * self.cameraSwingFactor)),
                0
            )

            self.lastMouseX = mouseX
            self.lastMouseY = mouseY

        return task.cont

    def setupControls(self):
        self.accept('escape', self.releaseMouse)
        self.accept('mouse1', self.captureMouse)

    def captureMouse(self):
        self.cameraSwingActivated = True
        md = self.win.getPointer(0)
        self.lastMouseX = md.getX()
        self.lastMouseY = md.getY()

        properties = WindowProperties()
        properties.setCursorHidden(True)
        properties.setMouseMode(WindowProperties.M_relative)
        self.win.requestProperties(properties)

    def releaseMouse(self):
        self.cameraSwingActivated = False
        properties = WindowProperties()
        properties.setCursorHidden(False)
        properties.setMouseMode(WindowProperties.M_absolute)
        self.win.requestProperties(properties)

    def setupCamera(self):
        self.disableMouse()
        self.camera.setPos(0, -12, 5.25)
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
        for x in [-2, 0, 2]:
            for y in [-2, 0, 2]:
                block = loader.loadModel('grass-block.glb')
                block.setPos(x, y, -1)
                block.reparentTo(render)

        self.demo1 = loader.loadModel('char1.glb')
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
