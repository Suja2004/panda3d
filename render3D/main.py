import sys
import math
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QPushButton
from PyQt5.QtOpenGL import QGLWidget
from OpenGL.GL import *


class GLWidget(QGLWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.rotate_angle = 0
        self.timer = self.startTimer(10)  # Timer for animation

    def initializeGL(self):
        glClearColor(0.0, 0.0, 0.0, 1.0)
        glEnable(GL_DEPTH_TEST)

    def resizeGL(self, width, height):
        glViewport(0, 0, width, height)
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        aspect_ratio = width / height
        fov_degrees = 45.0
        near_clip = 0.1
        far_clip = 100.0

        # Calculate perspective projection matrix manually
        top = near_clip * math.tan(math.radians(fov_degrees / 2.0))
        bottom = -top
        left = bottom * aspect_ratio
        right = top * aspect_ratio

        glFrustum(left, right, bottom, top, near_clip, far_clip)
        glMatrixMode(GL_MODELVIEW)

    def paintGL(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        glLoadIdentity()
        glTranslatef(0.0, 0.0, -5.0)
        glRotatef(self.rotate_angle, 1, 1, 1)

        glBegin(GL_QUADS)
        glColor3f(1.0, 0.0, 0.0)  # Red
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(1.0, 1.0, 1.0)

        glColor3f(0.0, 1.0, 0.0)  # Green
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(1.0, -1.0, -1.0)

        glColor3f(0.0, 0.0, 1.0)  # Blue
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)

        glColor3f(1.0, 1.0, 0.0)  # Yellow
        glVertex3f(1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, -1.0)

        glColor3f(0.0, 1.0, 1.0)  # Cyan
        glVertex3f(-1.0, 1.0, 1.0)
        glVertex3f(-1.0, 1.0, -1.0)
        glVertex3f(-1.0, -1.0, -1.0)
        glVertex3f(-1.0, -1.0, 1.0)

        glColor3f(1.0, 0.0, 1.0)  # Magenta
        glVertex3f(1.0, 1.0, -1.0)
        glVertex3f(1.0, 1.0, 1.0)
        glVertex3f(1.0, -1.0, 1.0)
        glVertex3f(1.0, -1.0, -1.0)
        glEnd()

        self.rotate_angle += 1

    def timerEvent(self, event):
        self.update()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setGeometry(100, 100, 800, 600)
        self.setWindowTitle('3D Modeling & Animation App')

        layout = QVBoxLayout()
        central_widget = QWidget(self)
        central_widget.setLayout(layout)
        self.setCentralWidget(central_widget)

        self.glWidget = GLWidget()
        layout.addWidget(self.glWidget)

        btn_create_object = QPushButton('Create Object', self)
        btn_create_object.clicked.connect(self.create_object)
        layout.addWidget(btn_create_object)

        self.show()

    def create_object(self):
        print('Creating 3D object...')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    mainWindow = MainWindow()
    sys.exit(app.exec_())
