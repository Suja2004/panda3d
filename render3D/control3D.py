from direct.showbase.ShowBase import ShowBase
from panda3d.core import NodePath

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Load the model directly
        self.model = self.loader.load_model("GLTF_files/char2.gltf")
        self.model.reparent_to(self.render)

        # Set scale and position
        self.model.set_scale(1.0)
        self.model.set_pos(0, 10, 0)

        # Set camera position
        self.camera.set_pos(0, -20, 5)
        self.camera.look_at(self.model)

        # Print out all bone names in the model
        self.print_bone_hierarchy(self.model)

        # Rotate specific bones (e.g., arm.L and leg.L)
        self.rotate_arm("arm.L")
        self.rotate_leg("leg.L")

    def print_bone_hierarchy(self, model):
        """Recursive function to print bone names and their children."""
        print("Bone hierarchy for the model:")
        for joint in model.get_children():
            self.print_bone(joint)

    def print_bone(self, bone, depth=0):
        """Recursive function to print bone names and their children."""
        indent = "  " * depth
        print(f"{indent}{bone.get_name()}")

        # Recursively print all children of this bone
        for child in bone.get_children():
            self.print_bone(child, depth + 1)

    def rotate_arm(self, arm_name):
        """Rotate the arm bone."""
        arm = self.model.find(f'**/{arm_name}')
        if arm:
            arm.set_hpr(45, 0, 0)  # Rotate 45 degrees around the X-axis (hpr = heading, pitch, roll)

    def rotate_leg(self, leg_name):
        """Rotate the leg bone."""
        leg = self.model.find(f'**/{leg_name}')
        if leg:
            leg.set_hpr(0, 0, 45)  # Rotate 45 degrees around the Z-axis (hpr = heading, pitch, roll)

app = MyApp()
app.run()
