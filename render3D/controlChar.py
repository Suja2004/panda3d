from direct.showbase.ShowBase import ShowBase
from direct.actor.Actor import Actor

class MyApp(ShowBase):
    def __init__(self):
        super().__init__()

        # Load the character as Actor
        self.model = Actor("GLTF_files/char2.gltf")
        self.model.reparent_to(self.render)
        self.model.set_scale(1.5)
        self.model.set_pos(0, 20, -7)

        # Move camera
        self.camera.set_pos(0, -20, 5)
        self.camera.look_at(self.model)

        # Print out all bone names in the console
        self.print_bone_hierarchy(self.model)

    def print_bone_hierarchy(self, model):
        # Iterate through each joint (bone) and print its name
        print("Bone hierarchy for the model:")
        for joint in model.get_joints():
            self.print_bone(joint)

    def print_bone(self, bone, depth=0):
        """Recursive function to print bone names and their children."""
        indent = "  " * depth
        print(f"{indent}{bone.get_name()}")

        # Recursively print all children of this bone
        for child in bone.get_children():
            self.print_bone(child, depth + 1)

app = MyApp()
app.run()
