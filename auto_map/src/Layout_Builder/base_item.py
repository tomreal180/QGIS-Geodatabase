from abc import ABC, abstractmethod
from qgis.core import QgsLayoutSize, QgsUnitTypes, QgsProperty, QgsLayoutPoint, QgsPrintLayout

class BaseLayoutItem(ABC):
    def __init__(self,item_id):
        self.id = item_id
        self.qgs_item = None
        self.positionX = 0.0
        self.positionY = 0.0
        self.itemWidth = 0.0
        self.itemHeight = 0.0
        
    def setPosition(self, x = None, y = None):
        if x:
            self.positionX = x
        if y:
            self.positionY = y
        if self.qgs_item and self.positionX and self.positionY:
            self.qgs_item.attemptMove(QgsLayoutPoint(self.positionX, self.positionY, QgsUnitTypes.LayoutMillimeters))
  
    def setSize(self, width = None, height = None):
        if width is not None:
            self.itemWidth = width
        if height is not None:
            self.itemHeight = height
        if self.qgs_item and self.itemWidth and self.itemHeight:
            self.qgs_item.attemptResize(QgsLayoutSize(self.itemWidth, self.itemHeight, QgsUnitTypes.LayoutMillimeters))
        
    def set_static(self, x, y, width, height):
        self.positionX = x
        self.positionY = y
        self.itemWidth = width
        self.itemHeight = height
        
        if self.qgs_item:
            self.qgs_item.attemptMove(QgsLayoutPoint(self.positionX, self.positionY, QgsUnitTypes.LayoutMillimeters))
            self.qgs_item.attemptResize(QgsLayoutSize(self.itemWidth, self.itemHeight, QgsUnitTypes.LayoutMillimeters))
            
    def set_dynamic(self, dynamic_promps: dict):
        if self.qgs_item:
            for prop, expr in dynamic_promps.items():
                self.qgs_item.dataDefinedProperties().setProperty(
                    prop, QgsProperty.fromExpression(expr)
                )
    
    def add_to_layout(self, layout:QgsPrintLayout):
        # if self.qgs_item and self.qgs_item.layout() is None:
        layout.addLayoutItem(self.qgs_item)
            
    @abstractmethod
    def create_item(self, layout: QgsPrintLayout):
        pass