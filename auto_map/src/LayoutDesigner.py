from qgis.core import *
from PyQt5.QtGui import QFont, QFontMetricsF
from .Layout_Builder.base_item import BaseLayoutItem
from .Layout_Builder.basic_items import *

import os
# class Item:
#     def __init__(self, positionX : int = None, positionY: int = None, itemWidth: int = None, itemHeight: int = None, item: QgsLayoutItem = None):
#         self.positionX = positionX
#         self.positionY = positionY
#         self.itemWidth = itemWidth
#         self.itemHeight = itemHeight
#         self.item = item
    
#     def initializeMap(self, extent):
#         if self.item and isinstance(self.item, QgsLayoutItemMap):
#             self.item.setRect(10, 10, 10, 10)
#             self.item.setFrameEnabled(True)
#             self.item.setId("map")
#             self.item.zoomToExtent(extent)
#             self.item.setFrameStrokeWidth(QgsLayoutMeasurement(0.3, QgsUnitTypes.LayoutMillimeters))
#     def getItem(self):
#         return self.item
    
#     def setPositionX(self, positionX):
#             self.positionX = positionX
    
#     def setPositionY(self, positionY):
#         self.positionY = positionY

#     def setItemWidth(self, itemWidth):
#         self.itemWidth = itemWidth

#     def setItemHeight(self, itemHeight):
#         self.itemHeight = itemHeight

#     def checkAddCondition(self):
#         if self.positionX and self.positionY and self.itemWidth and self.itemHeight:
#             return True
#         return False
    
#     def setPosition(self):
#         if self.positionX and self.positionY:
#             self.item.attemptMove(QgsLayoutPoint(self.positionX, self.positionY, QgsUnitTypes.LayoutMillimeters))
#         else:
#             raise ValueError("PositionX and PositionY must be set before calling setPosition()")
        
#     def setSize(self):
#         if self.itemWidth and self.itemHeight:
#             self.item.attemptResize(QgsLayoutSize(self.itemWidth, self.itemHeight, QgsUnitTypes.LayoutMillimeters))
#         else:
#             raise ValueError("ItemWidth and ItemHeight must be set before calling setSize()")


# class LayoutDesigner:
#     def __init__(self, project, Layout_Name):
#         self.layout = QgsPrintLayout(project)
#         self.layout.setName(Layout_Name)
#         self.layout.initializeDefaults()
#         self.items = []
    
#     def getLayout(self):
#         return self.layout
    
#     def setUpPage(self, width, height):
#         ## Page Setup
#         page = self.layout.pageCollection().page(0)
#         #Static Set Up
#         custom_size = QgsLayoutSize(width, height, QgsUnitTypes.LayoutMillimeters)
#         page.setPageSize(custom_size)
        
#         #Dynamic Set Up
#         page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{width}"))
#         page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{height}"))
        
#     def createMapItem(self):
#         map_item = Item(item= QgsLayoutItemMap(self.layout))
#         map_item.initializeMap(self.layout.extent())
        
#         self.items.append(map_item)
    
class LayoutDesigner:
    def __init__(self, project, layout_Name, variables, user_inputs):
        self.project = project
        self.layout_Name = layout_Name
        self.variables = variables
        self.inputs = user_inputs
        self.items = {}
        
        self.layout = QgsPrintLayout(project)
        self.layout.setName(self.layout_Name)
        self.layout.initializeDefaults()
        
    def add_item(self, item: BaseLayoutItem):
        self.items[item.id] = item
        item.create_item(self.layout)
        return item
    
    def get_item(self, item_id):
        return self.items.get(item_id)
    
    def build(self):
        for item in self.items.values():
            item.add_to_layout(self.layout)
            
        return self.layout
        