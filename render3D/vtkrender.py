import sys
import vtk
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from vtk.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("GLB Viewer with VTK + PyQt5")
        self.setGeometry(100, 100, 800, 600)

        self.frame = QWidget()
        self.layout = QVBoxLayout()
        self.vtkWidget = QVTKRenderWindowInteractor(self.frame)

        self.layout.addWidget(self.vtkWidget)
        self.frame.setLayout(self.layout)
        self.setCentralWidget(self.frame)

        self.renderer = vtk.vtkRenderer()

        self.render_window = self.vtkWidget.GetRenderWindow()
        self.render_window.AddRenderer(self.renderer)

        self.interactor = self.render_window.GetInteractor()

        self.load_glb_model("C:/Users/DELL/Documents/GLBfiles/char2.gltf")  # <-- your model path

        self.renderer.SetBackground(0.1, 0.2, 0.4)
        self.show()
        self.interactor.Initialize()
        self.interactor.Start()

    def load_glb_model(self, path):
        reader = vtk.vtkGLTFReader()
        reader.SetFileName(path)
        reader.Update()

        output = reader.GetOutput()
        actors = []
        self.extract_polydata_blocks(output, actors)

        for actor in actors:
            self.renderer.AddActor(actor)

    def extract_polydata_blocks(self, multi_block, actor_list):
        for i in range(multi_block.GetNumberOfBlocks()):
            block = multi_block.GetBlock(i)
            if isinstance(block, vtk.vtkPolyData):
                mapper = vtk.vtkPolyDataMapper()
                mapper.SetInputData(block)
                actor = vtk.vtkActor()
                actor.SetMapper(mapper)
                actor_list.append(actor)
            elif isinstance(block, vtk.vtkMultiBlockDataSet):
                self.extract_polydata_blocks(block, actor_list)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
