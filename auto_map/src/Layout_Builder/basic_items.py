from .base_item import BaseLayoutItem
from qgis.core import (
    QgsLayoutItemMap, QgsPrintLayout, QgsLayoutMeasurement, QgsLayoutItemShape, 
    QgsLayoutItemLabel, QgsLayoutItemPicture, QgsLayoutItemScaleBar, QgsUnitTypes, 
    QgsLayoutItem, Qgis, QgsLayoutItemLegend, QgsLegendStyle
)
from PyQt5.QtGui import QFont, QColor
from qgis.PyQt.QtCore import Qt

class MapItem(BaseLayoutItem):
    def __init__(self, item_id, target_layer = None, stroke_width = 0.3):
        super().__init__(item_id)
        self.target_layer = target_layer
        self.stroke_width = stroke_width

    def create_item(self, layout: QgsPrintLayout):
        self.qgs_item = QgsLayoutItemMap(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setRect(10, 10, 10, 10)
        self.qgs_item.setFrameEnabled(True)
        self.qgs_item.setFrameStrokeWidth(QgsLayoutMeasurement(self.stroke_width))
        
        if self.target_layer:
            self.qgs_item.zoomToExtent(self.target_layer.extent())
        return self.qgs_item

class ShapeItem(BaseLayoutItem):
    def __init__(self, item_id, shape_type = QgsLayoutItemShape.Rectangle, stroke_width = 0.3):
        super().__init__(item_id)
        self.shape_type = shape_type
        self.stroke_width = stroke_width

    def create_item(self, layout: QgsPrintLayout):
        self.qgs_item = QgsLayoutItemShape(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setShapeType(self.shape_type)
        self.qgs_item.setFrameEnabled(True)
        self.qgs_item.setFrameStrokeWidth(QgsLayoutMeasurement(self.stroke_width))
        return self.qgs_item
    
class LabelItem(BaseLayoutItem):
    def __init__(self, item_id, text, font_family="Calibri", font_size= 7, is_Bold=False, middle = False, background=False):
        super().__init__(item_id)
        self.text = text
        self.font = QFont(font_family, font_size, QFont.Bold if is_Bold else QFont.Normal)
        self.middle = middle
        self.background = background

    def create_item(self, layout: QgsPrintLayout):
        self.qgs_item = QgsLayoutItemLabel(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setText(self.text)
        self.qgs_item.setFont(self.font)
        self.qgs_item.setMargin(0)
        if self.middle:
            self.qgs_item.setHAlign(Qt.AlignHCenter)
            self.qgs_item.setVAlign(Qt.AlignVCenter)
        if self.background:
            self.qgs_item.setMarginX(2.0)
            self.qgs_item.setMarginY(2.0)
            self.qgs_item.setBackgroundEnabled(True)
            self.qgs_item.setBackgroundColor(QColor(255, 255, 224))
            
            self.qgs_item.setFrameEnabled(True)
            self.qgs_item.setFrameStrokeWidth(QgsLayoutMeasurement(0.3))
            self.qgs_item.setFrameStrokeColor(QColor(0, 0, 0))
            
        return self.qgs_item
    

class PictureItem(BaseLayoutItem):
    def __init__(self, item_id, path, linked_map=None):
        super().__init__(item_id)
        self.path = path
        self.linked_map = linked_map

    def create_item(self, layout):
        self.qgs_item = QgsLayoutItemPicture(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setFrameEnabled(False)
        self.qgs_item.setPicturePath(self.path)
        self.qgs_item.setPictureAnchor(QgsLayoutItem.Middle)
        if self.linked_map:
            self.qgs_item.setLinkedMap(self.linked_map)
            self.qgs_item.setNorthMode(0) # For North Arrow
        return self.qgs_item

class ScaleBarItem(BaseLayoutItem):
    def __init__(self, item_id, linked_map, var, font_size):
        super().__init__(item_id)
        self.linked_map = linked_map
        self.var = var
        self.font_size = font_size

    def create_item(self, layout):
        self.qgs_item = QgsLayoutItemScaleBar(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setFrameEnabled(False)
        self.qgs_item.setStyle("Single Box")
        self.qgs_item.setBoxContentSpace(0)
        self.qgs_item.setFont(QFont("Calibri", self.font_size))
        self.qgs_item.setLabelBarSpace(self.var["custom_scale_label_space"])
        self.qgs_item.setLinkedMap(self.linked_map)
        self.qgs_item.setHeight(self.var["custom_scale_bar_height"])
        # self.qgs_item.setSegmentSizeMode(Qgis.ScaleBarSegmentSizeMode.Fixed)
        self.qgs_item.setSegmentSizeMode(Qgis.ScaleBarSegmentSizeMode.FitWidth)
        self.qgs_item.setMinimumBarWidth(15) 
        self.qgs_item.setMaximumBarWidth(40)
        self.qgs_item.setUnits(QgsUnitTypes.DistanceMeters)
        self.qgs_item.setMapUnitsPerScaleBarUnit(1)
        # self.qgs_item.setUnitsPerSegment(100)
        
        self.qgs_item.setNumberOfSegments(3)
        self.qgs_item.setNumberOfSegmentsLeft(0)
        self.qgs_item.setUnitLabel("m")
        self.qgs_item.setReferencePoint(QgsLayoutItem.LowerLeft)
        return self.qgs_item
    
class LegendContentItem(BaseLayoutItem):
    def __init__(self, item_id, linked_map,layer_names, project, font = "Calibri", font_size=5):
        super().__init__(item_id)
        self.linked_map = linked_map
        self.selected_layers = layer_names
        self.project = project
        self.font = font
        self.font_size = font_size
            
    def create_item(self, layout: QgsPrintLayout):
        legend_symbol_width = 5
        legend_symbol_height = 2
        legend_symbol_spacing_left = 0.4
        legend_symbol_spacing = 1
        legend_symbol_label_spacing = 2
        custom_legend_column_count = 1 
        self.qgs_item = QgsLayoutItemLegend(layout)
        self.qgs_item.setId(self.id)
        self.qgs_item.setLinkedMap(self.linked_map)
        self.qgs_item.setLegendFilterByMapEnabled(True)
        self.qgs_item.setAutoUpdateModel(False)
        self.qgs_item.model().rootGroup().removeAllChildren()
        
        for layer_name in self.selected_layers:
            layer = self.project.mapLayersByName(layer_name)
            if layer:
                layer_node = self.qgs_item.model().rootGroup().addLayer(layer[0])
                layer_node.setCustomProperty("legend/title-style", "hidden")
                    
        self.qgs_item.setResizeToContents(True)
        self.qgs_item.setResizeToContents(True)
        self.qgs_item.setWrapString("//")
    
        self.qgs_item.setStyleFont(QgsLegendStyle.Group, QFont(self.font, self.font_size))
        self.qgs_item.setStyleFont(QgsLegendStyle.Subgroup, QFont(self.font, self.font_size))
        self.qgs_item.setStyleFont(QgsLegendStyle.SymbolLabel, QFont(self.font, self.font_size))
    
        self.qgs_item.setSymbolWidth(legend_symbol_width)
        self.qgs_item.setSymbolHeight(legend_symbol_height)
    
        self.qgs_item.setColumnCount(custom_legend_column_count)
        self.qgs_item.setEqualColumnWidth(True)
        self.qgs_item.setSplitLayer(True)
        
        styles = [
                QgsLegendStyle.Title,
                QgsLegendStyle.Group,
                QgsLegendStyle.Subgroup,
            ]
        
        for style in styles:
            self.qgs_item.rstyle(style).setMargin(0)
        self.qgs_item.rstyle(QgsLegendStyle.Title).setMargin(0)
        
        self.qgs_item.setBoxSpace(0)
        self.qgs_item.setColumnSpace(0)
    
        self.qgs_item.rstyle(QgsLegendStyle.Symbol).setMargin(
            QgsLegendStyle.Left, legend_symbol_spacing_left
        )
        self.qgs_item.rstyle(QgsLegendStyle.Symbol).setMargin(
            QgsLegendStyle.Top, legend_symbol_spacing
        )
        self.qgs_item.rstyle(QgsLegendStyle.SymbolLabel).setMargin(legend_symbol_label_spacing)
        
        return self.qgs_item
        
        
