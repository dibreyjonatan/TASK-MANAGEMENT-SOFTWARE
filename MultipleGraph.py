from PyQt5.QtWidgets import QWidget,QVBoxLayout

import pyqtgraph as pg # type: ignore

class MultipleGraph(QWidget):
    def __init__(self,parent=None):
        super(MultipleGraph,self).__init__(parent)
        pg.setConfigOptions(antialias=True)
        
        
        self.graph = pg.GraphicsLayoutWidget(show=True, title="GRAPH OF SENSOR DATA")
        self.master=QVBoxLayout()
        self.master.addWidget(self.graph)
        self.setLayout(self.master)
       