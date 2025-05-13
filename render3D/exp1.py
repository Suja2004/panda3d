from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, Vec4, Point3, NodePath, LVecBase3f, DirectionalLight, AmbientLight
from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectLabel import DirectLabel
from direct.gui import DirectGuiGlobals as DGG
from direct.task import Task
from direct.interval.LerpInterval import LerpPosInterval, LerpHprInterval
from direct.interval.IntervalGlobal import Sequence
import json
import random
import sys
import time


class SignLanguageApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        # Set up the base window and camera
        self.disableMouse()
        self.camera.setPos(0, -15, 3.25)
        self.camera.lookAt(0, 0, 0)

        # Create title text
        self.title = OnscreenText(
            text="SignSynth",
            style=1, fg=(1, 1, 1, 1), pos=(0, 0.9),
            scale=0.1, mayChange=True
        )

        # Load 3D model and setup
        self.loadModels()
        self.setupLights()
        self.setupSkybox()

        # Load pose data
        try:
            self.current_pose = "default"
            self.gesture_data = self.loadAllPoseData()
            self.loadSignPoses(self.current_pose)
            self.expanded_sequence = []
            self.pose_index = 0
            self.is_animating = False
        except Exception as e:
            print(f"Could not load pose data: {e}")

        # Media control variables
        self.media_control_active = False
        self.play_interval = 10
        self.pause_interval = 5
        self.last_media_action_time = 0
        self.media_state = "paused"
        self.tabs_visible = False

        # Create UI elements
        self.setup_ui()

    def setup_ui(self):
        self.setup_sign_language_tab()
        self.create_media_control_tab()


    def setup_sign_language_tab(self):
        # Setup buttons for the sign language tab
        self.setup_buttons()
        self.setup_textbox()

    def toggle_tabs_visibility(self):
        # Toggle tabs visibility
        if self.tabs_visible:
            self.media_frame.hide()
            self.tabs_visible = False
        else:
            # Restore to previous state
            self.media_frame.show()
            self.tabs_visible = True


    def loadModels(self):
        self.torso = loader.loadModel('character/torso.glb')
        self.torso.setPos(0, 0, -1.5)
        self.torso.reparentTo(render)
        self.torso.setScale(0.7)

        # Load arms
        self.rarm = loader.loadModel('character/RArmX.glb')
        self.rarm.reparentTo(self.torso)

        self.larm = loader.loadModel('character/LArmX.glb')
        self.larm.reparentTo(self.torso)

        # Setup detailed arm parts
        self.setup_arm_details()

    def setup_arm_details(self):
        # Right arm
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

        # Left arm
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
        mainLightNodePath.setHpr(0, -70, 0)
        render.setLight(mainLightNodePath)

        ambientLight = AmbientLight('ambient light')
        ambientLight.setColor((0.2, 0.2, 0.2, 1))
        ambientLightNodePath = render.attachNewNode(ambientLight)
        render.setLight(ambientLightNodePath)
        render.setShaderAuto()

    def setupSkybox(self):
        try:
            skybox = loader.loadModel('skybox/skybox.egg')
            skybox.setScale(50)
            skybox.setBin('background', 1)
            skybox.setDepthWrite(0)
            skybox.setLightOff()
            skybox.reparentTo(render)
        except Exception as e:
            print(f"Could not load skybox: {e}")

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

    def expandPoseSequence(self, sequence):
        result = []
        for word in sequence:
            if word.lower() in self.gesture_data:
                result.append(word.lower())
            else:
                for letter in word.lower():
                    if letter in self.gesture_data:
                        result.append(letter)
        return result

    def setup_buttons(self):
        # Button to change model color
        self.color_button = DirectButton(
            text="Change Color",
            text_scale=0.5,
            pos=(0.8, 0, 0.7),
            scale=0.1,
            frameSize=(-2, 2, -0.5, 0.5),
            command=self.change_model_color
        )

        # Button to reset the model to default pose
        self.reset_button = DirectButton(
            text="Reset Pose",
            text_scale=0.5,
            scale=0.1,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0.8, 0, 0.3),
            command=self.reset_pose
        )

        # Media Control Tab Button
        self.media_tab_button = DirectButton(
            text="Media Control",
            text_scale=0.5,
            scale=0.1,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0.8, 0, 0),
            command=self.toggle_tabs_visibility
        )
    def change_model_color(self):
        # Change model color randomly
        r = random.random()
        g = random.random()
        b = random.random()
        self.torso.setColorScale(r, g, b, 1)

    def reset_pose(self):
        # Reset to default pose
        self.loadSignPoses("default")
        self.stopAnimation()

    def setup_textbox(self):
        # Create a text entry box
        self.text_entry = DirectEntry(
            text="",
            scale=0.08,
            pos=(-0.75, 0, -0.8),
            command=self.process_text,
            width=20,
            initialText="Type text here"
        )

        # Text display for entered text
        self.text_display = OnscreenText(
            text="",
            pos=(0, -0.9),
            scale=0.07,
            mayChange=True
        )

        # Instruction text
        self.instructions = OnscreenText(
            text="Enter text and click 'Sign It!' to animate",
            pos=(0, -0.7),
            scale=0.06,
            fg=(1, 1, 1, 1)
        )

        # Button to start animation
        self.animate_button = DirectButton(
            text="Sign It!",
            text_scale=0.5,
            scale=0.1,
            frameSize=(-2, 2, -0.5, 0.5),
            pos=(0.75, 0, -0.8),
            command=self.start_animation
        )

    def process_text(self, text):
        # Update text display when text is entered
        self.text_display.setText(f"Ready to sign: {text}")

        # Store the text but don't animate yet
        self.current_text = text.strip()

    def start_animation(self):
        # If there's already animation running, stop it
        self.stopAnimation()

        # Get text from entry if process_text hasn't been called
        self.current_text = self.text_entry.get().strip()

        # Split the text into words
        words = self.current_text.split()

        # Create an expanded sequence of poses
        self.expanded_sequence = self.expandPoseSequence(words)

        if not self.expanded_sequence:
            self.text_display.setText("No valid signs found in text")
            return

        self.text_display.setText(f"Signing: {self.current_text}")
        self.pose_index = 0
        self.is_animating = True

        # Start animation task
        taskMgr.add(self.animateNextPose, "SignAnimation")

    def stopAnimation(self):
        # Stop any running animation task
        if self.is_animating:
            taskMgr.remove("SignAnimation")
            self.is_animating = False

    def slideArms(self):
        slide_distance = 0.5
        time = 0.2  # Increased wait time between poses

        sequence = Sequence(
            LerpPosInterval(self.larm, time, self.larm.getPos()),
            LerpPosInterval(self.rarm, time, self.rarm.getPos() + LVecBase3f(-slide_distance, 0, 0)),
            LerpPosInterval(self.larm, time, self.larm.getPos()),
            LerpPosInterval(self.rarm, time, self.rarm.getPos())
        )
        sequence.start()

    def animateNextPose(self, task):
        if self.pose_index >= len(self.expanded_sequence):
            self.loadSignPoses("default")
            self.pose_index = 0
            self.is_animating = False
            self.text_display.setText("Animation Complete")
            self.current_pose = ""

            # Reset the text display after a short delay
            taskMgr.doMethodLater(2, self.reset_text_display, "ResetTextDisplay")

            return Task.done

        pose_name = self.expanded_sequence[self.pose_index]

        # Check for same as previous
        if self.current_pose == pose_name and len(pose_name) == 1:
            self.slideArms()
            self.pose_index += 1
            return task.again

        self.current_pose = pose_name
        poses = self.gesture_data.get(pose_name)

        if not poses:
            self.pose_index += 1
            return task.again

        sequence = []
        time = 0.05  # Slower movement between poses

        def addFingerLerp(hand_data, finger_map):
            if "fingers" not in hand_data:
                return
            for name, parts in finger_map.items():
                if name in hand_data["fingers"]:
                    for part, pose_data in zip(parts, hand_data["fingers"][name]):
                        sequence.append(LerpPosInterval(part, 0, LVecBase3f(*pose_data["pos"])))
                        sequence.append(LerpHprInterval(part, 0, LVecBase3f(*pose_data["hpr"])))

        def addHandAndFingers(pose):
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

        if isinstance(poses, list):
            for pose in poses:
                addHandAndFingers(pose)
        else:
            addHandAndFingers(poses)

        # Execute the sequence
        Sequence(*sequence).start()

        # Update display to show current pose
        self.text_display.setText(f"Signing: {self.current_text} ('{pose_name}')")

        # Move to next pose after a delay
        task.delayTime = 1.5  # Long pause between signs
        self.pose_index += 1

        # Schedule next pose animation
        return task.again

    def reset_text_display(self, task=None):
        # Reset text display and prepare for new input
        self.text_display.setText("")
        return Task.done

    def create_media_control_tab(self):
        """Create media control tab content"""
        # Main container for media control tab
        self.media_frame = DirectFrame(
            frameColor=(0.9, 0.9, 0.9, 0.7),
            frameSize=(-0.8, 0.8, -0.8, 0.8),
            pos=(-0.2, 0, 0)
        )
        # Initially hide media frame
        self.media_frame.hide()

        # Media tab title
        self.media_title = DirectLabel(
            parent=self.media_frame,
            text="YouTube/Video Media Controller",
            text_scale=0.07,
            frameColor=(0.9, 0.9, 0.9, 0),
            pos=(0, 0, 0.65)
        )

        # Instructions label
        instructions_text = (
            "This feature will automatically play and pause media (like YouTube videos).\n"
            "1. Click 'Start Media Control'\n"
            "2. Switch to your media tab within 3 seconds\n"
            "3. The controller will periodically play and pause the media"
        )

        self.instruction_text = OnscreenText(
            parent=self.media_frame,
            text=instructions_text,
            scale=0.04,
            wordwrap=30,
            pos=(0, 0.5)
        )

        # Interval settings
        self.interval_frame = DirectFrame(
            parent=self.media_frame,
            frameColor=(0.9, 0.9, 0.9, 0),
            frameSize=(-0.5, 0.5, -0.2, 0.2),
            pos=(0, 0, 0.1)
        )

        # Pause duration label
        self.pause_label = DirectLabel(
            parent=self.interval_frame,
            text="Pause Duration (seconds):",
            text_scale=0.05,
            text_align=TextNode.ARight,
            frameColor=(0.9, 0.9, 0.9, 0),
            pos=(-0.1, 0, 0.1)
        )

        # Pause duration entry
        self.pause_entry = DirectEntry(
            parent=self.interval_frame,
            initialText=str(self.pause_interval),
            width=5,
            scale=0.05,
            pos=(0.2, 0, 0.1),
            frameColor=(1, 1, 1, 1)
        )

        # Play duration label
        self.play_label = DirectLabel(
            parent=self.interval_frame,
            text="Play Duration (seconds):",
            text_scale=0.05,
            text_align=TextNode.ARight,
            frameColor=(0.9, 0.9, 0.9, 0),
            pos=(-0.1, 0, -0.1)
        )

        # Play duration entry
        self.play_entry = DirectEntry(
            parent=self.interval_frame,
            initialText=str(self.play_interval),
            width=5,
            scale=0.05,
            pos=(0.2, 0, -0.1),
            frameColor=(1, 1, 1, 1)
        )

        # Media control button
        self.media_toggle_button = DirectButton(
            parent=self.media_frame,
            text="Start Media Control",
            text_scale=0.05,
            frameSize=(-0.3, 0.3, -0.1, 0.1),
            relief=DGG.RAISED,
            command=self.toggle_media_control,
            pos=(0, 0, -0.2),
            frameColor=(0.3, 0.6, 0.9, 1)
        )

        # Media status label
        self.media_status = DirectLabel(
            parent=self.media_frame,
            text="Status: Idle",
            text_scale=0.05,
            frameColor=(0.9, 0.9, 0.9, 0),
            pos=(0, 0, -0.4)
        )

        # Add the media control task
        taskMgr.add(self.media_control_task, "MediaControlTask")

    def toggle_media_control(self):
        """Toggle media control on or off"""
        try:
            # Update intervals with user entries
            self.play_interval = float(self.play_entry.get())
            self.pause_interval = float(self.pause_entry.get())

            # Toggle state
            self.media_control_active = not self.media_control_active

            if self.media_control_active:
                # We're starting - update UI
                self.media_toggle_button["text"] = "Stop Media Control"
                self.media_toggle_button["frameColor"] = (0.9, 0.3, 0.3, 1)  # Red for stop
                self.media_status["text"] = "Status: Starting (switch to media tab)"

                # Initialize media control state
                self.last_media_action_time = time.time()
                self.media_state = "starting"

                # Alert user to switch tabs
                print("Media control starting - switch to your media tab within 3 seconds!")
            else:
                # We're stopping - update UI
                self.media_toggle_button["text"] = "Start Media Control"
                self.media_toggle_button["frameColor"] = (0.3, 0.6, 0.9, 1)  # Blue for start
                self.media_status["text"] = "Status: Idle"
                self.media_state = "paused"

                print("Media control stopped")

        except ValueError:
            # Validation error for input fields
            self.media_status["text"] = "Error: Please enter valid numbers"

    def media_control_task(self, task):
        """Task to control media playback"""
        if not self.media_control_active:
            return Task.cont

        current_time = time.time()
        elapsed = current_time - self.last_media_action_time

        # Handle startup delay
        if self.media_state == "starting" and elapsed >= 3:
            # Initial action after startup delay - simulate keyboard space bar
            self.simulate_space_press()
            self.last_media_action_time = current_time
            self.media_state = "playing"
            self.media_status["text"] = f"Status: Playing for {self.play_interval}s"

        # Handle play state
        elif self.media_state == "playing" and elapsed >= self.play_interval:
            # Time to pause
            self.simulate_space_press()
            self.last_media_action_time = current_time
            self.media_state = "paused"
            self.media_status["text"] = f"Status: Paused for {self.pause_interval}s"

        # Handle paused state
        elif self.media_state == "paused" and elapsed >= self.pause_interval:
            # Time to play again
            self.simulate_space_press()
            self.last_media_action_time = current_time
            self.media_state = "playing"
            self.media_status["text"] = f"Status: Playing for {self.play_interval}s"

        return Task.cont

    def simulate_space_press(self):
        """Simulate pressing the space bar for media control"""
        # This uses different methods depending on the platform
        if sys.platform == 'win32':
            try:
                # For Windows
                import win32com.client
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys(" ", 0)
                print("Space key pressed (Windows)")
            except ImportError:
                print("Could not import win32com.client - media control may not work properly")
        else:
            try:
                # For macOS and Linux
                import pyautogui
                pyautogui.press('space')
                print("Space key pressed (macOS/Linux)")
            except ImportError:
                print("Could not import pyautogui - media control may not work properly")


# Initialize and run the application
app = SignLanguageApp()
app.run()