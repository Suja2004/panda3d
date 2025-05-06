from direct.showbase.ShowBase import ShowBase
from direct.task import Task


class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Load model
        self.model = self.loader.load_model("GLTF_files/char2.gltf")
        self.model.reparent_to(self.render)

        # Adjust model scale and position
        self.model.set_scale(1.5)  # you can adjust to 0.1 or 10
        self.model.set_pos(0, 20,-7)  # Move a bit forward

        # Move the camera back and look at model
        self.camera.set_pos(0, -20, 5)
        self.camera.look_at(self.model)

        # Add rotation task
        # self.taskMgr.add(self.spin_model, "SpinModelTask")

    # def spin_model(self, task):
    #     # Rotate the model a bit every frame
    #     angle_degrees = task.time * 30.0  # 30 degrees per second
    #     self.model.set_h(angle_degrees)
    #     return Task.cont

        print(self.model)


app = MyApp()
app.run()
