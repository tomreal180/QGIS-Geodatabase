# from qgis.core import (
#     QgsLayoutExporter, QgsPrintLayout, QgsLayoutItemMap, QgsProject, 
#     QgsLayoutPoint, QgsLayoutSize, QgsUnitTypes, QgsLayoutItemLabel, 
#     QgsLayoutItemLegend, QgsProperty, QgsLayoutItemPage, QgsLayoutMeasurement,
#     QgsLayoutObject
# )
from qgis.core import *
from PyQt5.QtGui import QFont, QFontMetricsF

from .dynamicTools import register_functions

import os



class LayoutGenerator:

    def __init__(self,project,user_inputs):
        self.project = project
        self.user_inputs = user_inputs
        self.manager = self.project.layoutManager()
        register_functions()  # Register the functions when the module is imported
        self.setup()  # Call the setup method to initialize configurations

    def setup(self):

        # self.project.setCustomVariables(
           
        # )

        self.variables ={
            "custom_page_dist_left_vq": 3,
            "custom_page_dist_right_vq": 3,
            "custom_page_dist_top_vq": 3,
            "custom_page_dist_bottom_vq": 3,
            "custom_item_dist_left_vq": 3,
            "custom_item_dist_right_vq": 3,
            "custom_item_dist_top_vq": 3,
            "custom_item_dist_bottom_vq": 3,
            "custom_frame_line_width_vq": 0.3,
            "custom_dist_title_text_vq": 2,
            "custom_frame_width_vq": 60,
            "custom_north_arrow_width_vq": 9,
            "custom_north_arrow_height_vq": 15,
            "custom_scale_width_vq": 35,
            "custom_scale_height_vq": 9,
            "custom_scale_label_space_vq": 2,
            "custom_scale_bar_height_vq": 2,
            "custom_page_size_width_vq": 297,
            "custom_page_size_height_vq": 210,
        }




    def _remove_existing_layouts(self,layout_name):
        existing_layout = self.manager.layoutByName(layout_name)
        if existing_layout:
            self.manager.removeLayout(existing_layout)

    def export_layout(self,layout,output_path):
        exporter = QgsLayoutExporter(layout)
        settings = QgsLayoutExporter.PdfExportSettings()
        exporter.exportToPdf(output_path, settings)

    def getDynamicItemPositionX(self, item):
        """
        Returns the X position of a layout item in millimeters.
        Usage: getDynamicItemPositionX('LayoutName', 'Item')
        """
        position = item.positionWithUnits()
        return position.x()

    def getDynamicItemPositionY(self, item):
            """
            Returns the Y position of a layout item in millimeters.
            Usage: getDynamicItemPositionY('LayoutName', 'Item')
            """
            position = item.positionWithUnits()
            return position.y()

    def GetDynamicItemHeight(self, item):
        """
        Returns the height of a layout item in millimeters.
        Usage: GetDynamicItemHeight('LayoutName', 'Item')
        """
        size = item.sizeWithUnits()
        return size.height()

    def GetDynamicItemWidth(self, item):
        """
        Returns the width of a layout item in millimeters.
        Usage: GetDynamicItemWidth('LayoutName', 'Item')
        """
        size = item.sizeWithUnits()
        return size.width()
    
    def calculateHeight(self, item, line_spacing=1.0):
        """
        Returns the height of a layout item in millimeters.
        Usage: calculateHeight('Item')
        """
        # Text, Font und Breite des Labels
        text = item.text()
        font = item.font()
        width_mm = item.sizeWithUnits().width()
        if not text.strip():
            return 0

        # Umrechnung mm - Pixel (96 dpi)
        width_px = width_mm * 96 / 25.4
        metrics = QFontMetricsF(font)

        lines = []

        # Text in Abschnitte trennen (Absatz = Zeilenumbruch)
        paragraphs = text.split('\n')

        for para in paragraphs:

            # harte Leerzeile - als echte Zeile zaehlen
            if para.strip() == "":
                lines.append(" ")
                continue

            words = para.split(" ")
            current_line = ""

            for word in words:
                test_line = word if current_line == "" else current_line + " " + word

                # boundingRect statt horizontalAdvance
                if metrics.boundingRect(test_line).width() > width_px:
                    # alte Zeile abschliessen
                    if current_line != "":
                        lines.append(current_line)
                    current_line = word
                else:
                    current_line = test_line

            if current_line != "":
                lines.append(current_line)

        # Gesamthoehe berechnen
        total_height_px = 0
        for line in lines:
            h = metrics.boundingRect(line).height()
            total_height_px += h * line_spacing

        # Sicherheitsabstand
        total_height_px *= 1.025

        # zurueck in mm
        height_mm = total_height_px * 25.4 / 96
        return height_mm
        
    def create_standard_layout(self):
        # Font
        font = "Calibri"
        font_size = 10
        font_size_title = 10
        font_size_metadata = 7
        #################################################################
        layout_name = "Standard Layout"
        self._remove_existing_layouts(layout_name)
        var = self.variables  
        layout = QgsPrintLayout(self.project)
        layout.initializeDefaults()
        layout.setName(layout_name)
        self.manager.addLayout(layout)
        ## Static Set Up
        page = layout.pageCollection().page(0)
        custom_size = QgsLayoutSize(var["custom_page_size_width_vq"], var["custom_page_size_height_vq"], QgsUnitTypes.LayoutMillimeters)
        page.setPageSize(custom_size)

        #Dynamic Set Up
        page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_vq']}"))
        page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_page_size_height_vq']}"))



        ########################################################################
        ### Map Frame

        map_item = QgsLayoutItemMap(layout)
        map_item.setRect(10, 10, 10, 10)
        map_item.setFrameEnabled(True)
        map_item.setId("map")
        target_layer = self.user_inputs.get('target_layer')
        map_item.zoomToExtent(target_layer.extent())
        ##static Set Up
        map_item.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))
        map_positionX = var["custom_frame_line_width_vq"]/2 + var["custom_page_dist_left_vq"]
        map_positionY = var["custom_frame_line_width_vq"]/2 + var["custom_page_dist_top_vq"]

        map_item.attemptMove(QgsLayoutPoint(map_positionX, map_positionY, QgsUnitTypes.LayoutMillimeters))

        map_itemHeight = var["custom_page_size_height_vq"] - var["custom_page_dist_top_vq"] - var["custom_frame_line_width_vq"] - var["custom_page_dist_bottom_vq"]

        ##dynamic Set Up
        map_item.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(f"{var['custom_frame_line_width_vq']/2 + var['custom_page_dist_left_vq']}"),
        )

        map_item.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(f"{var['custom_frame_line_width_vq']/2 + var['custom_page_dist_top_vq']}"),
        )
        
        map_item.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression(
                f"{var['custom_page_size_height_vq'] - var['custom_frame_line_width_vq'] - var['custom_page_dist_top_vq'] - var['custom_page_dist_bottom_vq']}"
            ),
        )
        ########################################################################
        ### Legend Frame
        legend_frame = QgsLayoutItemShape(layout)
        legend_frame.setShapeType(QgsLayoutItemShape.Rectangle)
        legend_frame.setId("legend_frame")
        legend_frame.setFrameEnabled(True)
        legend_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))
        ## Static Set Up
        lf_positionX = var["custom_page_size_width_vq"] - var["custom_page_dist_left_vq"] - var["custom_frame_width_vq"] - var["custom_frame_line_width_vq"]/2
        lf_positionY = var["custom_page_dist_top_vq"] + var["custom_frame_line_width_vq"]/2
        legend_frame.attemptMove(QgsLayoutPoint(lf_positionX, lf_positionY, QgsUnitTypes.LayoutMillimeters))

        lf_itemWidth = var["custom_frame_width_vq"] 
        legend_frame.attemptResize(QgsLayoutSize(lf_itemWidth, 47, QgsUnitTypes.LayoutMillimeters))

        map_itemWidth = lf_positionX - var["custom_item_dist_left_vq"] - var["custom_frame_line_width_vq"] - map_positionX
        map_item.attemptResize(QgsLayoutSize(map_itemWidth, map_itemHeight, QgsUnitTypes.LayoutMillimeters))

        ##Dynamic Set Up
        legend_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(f"{var['custom_page_size_width_vq'] - var['custom_page_dist_left_vq'] - var['custom_frame_width_vq'] - var['custom_frame_line_width_vq']/2}"),
        )
        legend_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(f"{var['custom_page_dist_top_vq'] + var['custom_frame_line_width_vq']/2}"),
        )

        legend_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(f"{var['custom_frame_width_vq']}"),
        )

        expr_map_width = (
            f"GetDynamicItemPositionX(@layout_name, 'legend_frame') - "
            f"{var['custom_item_dist_left_vq']} - "
            f"{var['custom_frame_line_width_vq']} - "
            f"GetDynamicItemPositionX(@layout_name, 'map')"
        )
        map_item.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(expr_map_width)
        )

        ########################################################################
        ### Legend Title
        legend_title = QgsLayoutItemLabel(layout)
        legend_title.setText("Legende")
        legend_title.setId("legend_title")
        legend_title.setFont(QFont(font, font_size_title, QFont.Bold))
        legend_title.setMargin(0)
        
        ### Static Set Up
        lt_positionX = lf_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
        lt_positionY = lf_positionY + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_top_vq"])
        lt_itemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        lt_itemHeight = self.calculateHeight(legend_title)
        legend_title.attemptMove(QgsLayoutPoint(lt_positionX, lt_positionY, QgsUnitTypes.LayoutMillimeters))
        legend_title.attemptResize(QgsLayoutSize(lt_itemWidth, lt_itemHeight, QgsUnitTypes.LayoutMillimeters))

        ##Dynamic Set Up
        legend_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                f"GetDynamicItemPositionX(  @layout_name ,'legend_frame') + (to_real({var['custom_frame_line_width_vq']})/2) + to_real({var['custom_item_dist_left_vq']})"
            ),
        )
        legend_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(  @layout_name ,'legend_frame') + "
                f"to_real({var['custom_frame_line_width_vq']})/2 + "
                f"to_real({var['custom_item_dist_top_vq']})"
            ),
        )
        legend_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_width_vq']}) - "
                f"2*to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_item_dist_right_vq']}) - "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )
        legend_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'legend_title')"),
        )
        
        ########################################################################
        ### Legend 
        legend_symbol_width = 6
        legend_symbol_height = 3
        legend_symbol_spacing_left = 0.4
        legend_symbol_spacing = 3
        legend_symbol_label_spacing = 2
        custom_legend_column_count = 1  #
        selected_layers = self.user_inputs.get('selected_layers', [])

        legend = QgsLayoutItemLegend(layout)
        legend.setId("legend")
        legend.setLinkedMap(map_item)
        legend.setLegendFilterByMapEnabled(True)
        legend.setAutoUpdateModel(False)
        legend.model().rootGroup().removeAllChildren()

        for layer_name in selected_layers:
            layer = self.project.mapLayersByName(layer_name)
            if layer:
                legend.model().rootGroup().addLayer(layer[0])

        legend.setResizeToContents(True)
        legend.setWrapString("//")

        legend.setStyleFont(QgsLegendStyle.Group, QFont(font, font_size))
        legend.setStyleFont(QgsLegendStyle.Subgroup, QFont(font, font_size))
        legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont(font, font_size))

        legend.setSymbolWidth(legend_symbol_width)
        legend.setSymbolHeight(legend_symbol_height)

        legend.setColumnCount(custom_legend_column_count)
        legend.setEqualColumnWidth(True)
        legend.setSplitLayer(True)

        styles = [
            QgsLegendStyle.Title,
            QgsLegendStyle.Group,
            QgsLegendStyle.Subgroup,
        ]

        for style in styles:
            legend.rstyle(style).setMargin(0)
        legend.rstyle(QgsLegendStyle.Title).setMargin(0)

        legend.setBoxSpace(0)
        legend.setColumnSpace(0)

        legend.rstyle(QgsLegendStyle.Symbol).setMargin(
            QgsLegendStyle.Left, legend_symbol_spacing_left
        )
        legend.rstyle(QgsLegendStyle.Symbol).setMargin(
            QgsLegendStyle.Top, legend_symbol_spacing
        )
        legend.rstyle(QgsLegendStyle.SymbolLabel).setMargin(legend_symbol_label_spacing)

        ## Static Set Up
        l_positionX = lf_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
        l_positionY = lf_positionY + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_top_vq"]) + lt_itemHeight + var["custom_dist_title_text_vq"]
        l_itemWidth = float(var["custom_frame_width_vq"]) - float(2*var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        legend.attemptMove(QgsLayoutPoint(l_positionX, l_positionY, QgsUnitTypes.LayoutMillimeters))

        legend.adjustBoxSize()
        current_legend_height = legend.sizeWithUnits().height()
        legend.attemptResize(QgsLayoutSize(l_itemWidth, current_legend_height, QgsUnitTypes.LayoutMillimeters))
        
        ##dynamic Set Up
        expr_legend_posX = (
            "GetDynamicItemPositionX(  @layout_name ,'legend_frame') + "
            f"(to_real({var['custom_frame_line_width_vq']})/2) + "
            f"to_real({var['custom_item_dist_left_vq']})"
        )
        legend.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX, QgsProperty.fromExpression(expr_legend_posX)
        )

        expr_legend_posY = (
            "GetDynamicItemPositionY(  @layout_name ,'legend_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_top_vq']}) + "
            "GetDynamicItemHeight(@layout_name,'legend_title') + "
            f"to_real({var['custom_dist_title_text_vq']})"
        )
        legend.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY, QgsProperty.fromExpression(expr_legend_posY)
        )

        expr_legend_width = (
            f"to_real({var['custom_frame_width_vq']}) - "
            f"2 *to_real({var['custom_frame_line_width_vq']}) - "
            f"to_real({var['custom_item_dist_right_vq']}) - "
            f"to_real({var['custom_item_dist_left_vq']})"
        )
        legend.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(expr_legend_width)
        )
        

        ########################################################################
        ### Auftragsbox
        municipality_frame = QgsLayoutItemShape(layout)
        municipality_frame.setShapeType(QgsLayoutItemShape.Rectangle)
        municipality_frame.setId("municipality_frame")
        municipality_frame.setFrameEnabled(True)
        municipality_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))


        ########################################################################
        ### Metadata Frame
        metadata_frame = QgsLayoutItemShape(layout)
        metadata_frame.setShapeType(QgsLayoutItemShape.Rectangle)
        metadata_frame.setId("metadata_frame")
        metadata_frame.setFrameEnabled(True)
        metadata_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))
        ### Static Set Up
        metaF_PositionX = lf_positionX
        metaF_ItemWidth = var["custom_frame_width_vq"]
       
        ### Metadata ###
        metadata = QgsLayoutItemLabel(layout)
        metadata.setText(
            "Datengrundlage: \n"
            + "© XXX \n"
            + "Hintergrundkarte: \n"
            + "© XXX\n"
            + "Sonstige Karteninhalte: \n"
            + "eigene Darstellung"
        )
        metadata.setFont(QFont(font, font_size_metadata))
        metadata.setMargin(0)
        metadata.setId("metadata")

        ##Static Set Up
        metadata_PositionX = metaF_PositionX + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_left_vq"]
        metadata_itemWidth = float(var["custom_frame_width_vq"]) - float(2*var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        metadata.attemptResize(QgsLayoutSize(metadata_itemWidth, 0, QgsUnitTypes.LayoutMillimeters))
        metadata_itemHeight = self.calculateHeight(metadata)
        metadata.attemptResize(QgsLayoutSize(metadata_itemWidth, metadata_itemHeight, QgsUnitTypes.LayoutMillimeters))

        metaF_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + metadata_itemHeight + var["custom_item_dist_bottom_vq"]
        metadata_frame.attemptResize(QgsLayoutSize(metaF_ItemWidth, metaF_ItemHeight, QgsUnitTypes.LayoutMillimeters))
        metaF_PositionY = var["custom_page_size_height_vq"] - var["custom_frame_line_width_vq"] - var["custom_page_dist_bottom_vq"] - metaF_ItemHeight
        metadata_frame.attemptMove(QgsLayoutPoint(metaF_PositionX, metaF_PositionY, QgsUnitTypes.LayoutMillimeters))

        metadata_PositionY = metaF_PositionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
        metadata.attemptMove(QgsLayoutPoint(metadata_PositionX, metadata_PositionY, QgsUnitTypes.LayoutMillimeters))

        ##Dynamic Set Up
        ### (Metadata Frame)
        metadata_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name ,'legend_frame')"
            ),
        )

        metadata_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(
                f"{var['custom_frame_width_vq']}"
            )
        )
        expr_metadata_frame_height = (
            f"to_real({var['custom_frame_line_width_vq']}) +"
            f"to_real({var['custom_item_dist_top_vq']}) + "
            f"GetDynamicItemHeight(@layout_name,'metadata') + "
            f"to_real({var['custom_item_dist_bottom_vq']})"
        )
        metadata_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(expr_metadata_frame_height)
        )

        metadata_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                f"to_real({var['custom_page_size_height_vq']}) -"
                f"to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_page_dist_bottom_vq']}) - "
                "GetDynamicItemHeight(@layout_name,'metadata_frame')"
            ),
        )

        ### (Metadata)
        metadata.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(  @layout_name ,'metadata_frame') + "
                f"{var['custom_frame_line_width_vq']}/2 + "
                f"{var['custom_item_dist_left_vq']}"
            ),
        )

        metadata.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(  @layout_name ,'metadata_frame') + "
                f"{var['custom_frame_line_width_vq']}/2 + "
                f"{var['custom_item_dist_top_vq']}"
            ),
        )

        metadata.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_width_vq']}) - "
                f"2*to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_item_dist_right_vq']}) - "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )

        metadata.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'metadata')"),
        )


        ########################################################################
        ### Bearbeitungsbox
        spie_frame = QgsLayoutItemShape(layout)
        spie_frame.setShapeType(QgsLayoutItemShape.Rectangle)
        spie_frame.setId("spie_frame")
        spie_frame.setFrameEnabled(True)
        spie_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))
        ## Static Set Up
        spieFrame_positionX = lf_positionX
        spieFrame_ItemWidth = var["custom_frame_width_vq"]

        ### SPIE title ###
        spie_title = QgsLayoutItemLabel(layout)
        spie_title.setText("Bearbeitung")
        spie_title.setId("spie_title")
        spie_title.setFont(QFont(font, font_size_title, QFont.Bold))
        spie_title.setMargin(0)

        ### Static Set Up
        spieTitle_positionX = spieFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
        spieTitle__ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        spie_title.attemptResize(QgsLayoutSize(spieTitle__ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
        spieTitle_ItemHeight = self.calculateHeight(spie_title)
        spie_title.attemptResize(QgsLayoutSize(spieTitle__ItemWidth, spieTitle_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        ## Dynamic Set Up
        spie_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_width_vq']}) - "
                f"2*to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_item_dist_right_vq']}) - "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )
        spie_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'spie_title')"),
        )

        ###SPIE LOGO###
        svg_logo_path = os.path.join(os.path.dirname(__file__), "assets", "SPIE.svg")
        spie_logo = QgsLayoutItemPicture(layout)
        spie_logo.setId("spie_logo")
        spie_logo.setFrameEnabled(False)
        spie_logo.setPicturePath(svg_logo_path)

        ## Static Set Up
        spieLogo_positionX = spieFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"]) + 0.2 
        spieLogo_ItemWidth = 10
        spieLogo_ItemHeight = 8
        spie_logo.attemptResize(QgsLayoutSize(spieLogo_ItemWidth, spieLogo_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        ## Dynamic Set Up
        spie_logo.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth, QgsProperty.fromExpression("10")
        )
        spie_logo.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("8")
        )

        ###SPIE Label###
        spie_content = QgsLayoutItemLabel(layout)
        spie_content.setId("spie_content")
        spie_content.setFrameEnabled(False)
        spie_content.setText("SPIE WirliebenKabel GmbH\nHohe Straße 125a\n07937 Zeulenroda-Triebes")
        spie_content.setFont(QFont(font, font_size))
        spie_content.setMargin(0)

        ## Static Set Up
        spieContent_positionX = spieLogo_positionX +  float(var["custom_item_dist_left_vq"])+ spieLogo_ItemWidth
        spieContent_ItemWidth = spieFrame_positionX + var["custom_frame_width_vq"] - var["custom_item_dist_right_vq"] - spieContent_positionX
        spie_content.attemptResize(QgsLayoutSize(spieContent_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
        spieContent_ItemHeight = self.calculateHeight(spie_content)
        spie_content.attemptResize(QgsLayoutSize(spieContent_ItemWidth, spieContent_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        spieFrame_ItemHeight = var["custom_frame_line_width_vq"]
        max_height = max((spieLogo_ItemHeight + 1.776), spieContent_ItemHeight)
        
        spieFrame_ItemHeight += (
            max_height + 
            var["custom_item_dist_top_vq"] + 
            var["custom_item_dist_bottom_vq"] + 
            spieTitle_ItemHeight + 
            var["custom_dist_title_text_vq"]
        )

        spie_frame.attemptResize(QgsLayoutSize(spieFrame_ItemWidth, spieFrame_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        spieFrame_positionY = metaF_PositionY - spieFrame_ItemHeight
        spie_frame.attemptMove(QgsLayoutPoint(spieFrame_positionX, spieFrame_positionY, QgsUnitTypes.LayoutMillimeters))

        spieTitle_positionY = spieFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
        spie_title.attemptMove(QgsLayoutPoint(spieTitle_positionX, spieTitle_positionY, QgsUnitTypes.LayoutMillimeters))

        spieLogo_positionY = spieFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"] + spieTitle_ItemHeight + var["custom_dist_title_text_vq"] + 1.776
        spie_logo.attemptMove(QgsLayoutPoint(spieLogo_positionX, spieLogo_positionY, QgsUnitTypes.LayoutMillimeters))

        spieContent_positionY = spieFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"] + spieTitle_ItemHeight + var["custom_dist_title_text_vq"] 
        spie_content.attemptMove(QgsLayoutPoint(spieContent_positionX, spieContent_positionY, QgsUnitTypes.LayoutMillimeters))

        ##dynamic Set Up
        spie_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                "(GetDynamicItemPositionX(@layout_name, 'spie_frame') + "
                f"{var['custom_frame_width_vq'] - var['custom_item_dist_right_vq']}"
                "- GetDynamicItemPositionX(@layout_name, 'spie_content')"
            ),
        )
        spie_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'spie_content')"),
        )

        spie_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(
                f"{var['custom_frame_width_vq']}"
            )
        )

        expr_spie_frame_height = (
            f"{var['custom_frame_line_width_vq']} + "
            "if((GetDynamicItemHeight(@layout_name, 'spie_logo') + 1.776) > GetDynamicItemHeight(@layout_name, 'spie_content'), (GetDynamicItemHeight(@layout_name, 'spie_logo') + 1.776), GetDynamicItemHeight(@layout_name, 'spie_content')) + "
            f"{var['custom_item_dist_top_vq']} + {var['custom_item_dist_bottom_vq']} + "
            "GetDynamicItemHeight(@layout_name, 'spie_title') + "
            f"{var['custom_dist_title_text_vq']}"
        )
        spie_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression(expr_spie_frame_height),
        )

        spie_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression("GetDynamicItemPositionX(@layout_name ,'legend_frame')"),
        )

        spie_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name,'metadata_frame') - "
                "GetDynamicItemHeight(@layout_name,'spie_frame')"
            ),
        )

        spie_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(  @layout_name ,'spie_frame') + "
                f"(to_real({var['custom_frame_line_width_vq']})/2) + "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )

        spie_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(  @layout_name ,'spie_frame') + "
                f"{var['custom_frame_line_width_vq']}/2 + "
                f"{var['custom_item_dist_top_vq']}"
            ),
        )

        spie_logo.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name, 'spie_frame') + "
                f"(to_real({var['custom_frame_line_width_vq']})/2) + "
                f"to_real({var['custom_item_dist_left_vq']}) + 0.2"
            ),
        )

        spie_logo.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name, 'spie_frame') + "
                f"{var['custom_frame_line_width_vq']}/2 + "
                f"{var['custom_item_dist_top_vq']} + "
                "GetDynamicItemHeight(@layout_name, 'spie_title') + "
                f"{var['custom_dist_title_text_vq']} + 1.776"
            ),
        )

        spie_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name, 'spie_logo') + "
                f"to_real({var['custom_item_dist_left_vq']}) + "
                "GetDynamicItemWidth(@layout_name, 'spie_logo')"
            ),
        )

        spie_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name, 'spie_frame') + "
                f"{var['custom_frame_line_width_vq']}/2 + "
                f"{var['custom_item_dist_top_vq']} + "
                f"GetDynamicItemHeight(@layout_name, 'spie_title') + "
                f"{var['custom_dist_title_text_vq']}"
            ),
        )
        
        ########################################################################
        ### Plan content
        ### Plan content frame ###
        plan_content_frame = QgsLayoutItemShape(layout)
        plan_content_frame.setShapeType(QgsLayoutItemShape.Rectangle)
        plan_content_frame.setId("plan_content_frame")
        plan_content_frame.setFrameEnabled(True)
        plan_content_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var['custom_frame_line_width_vq']))

        ## Static Set Up
        PlanContentFrame_positionX = lf_positionX
        PlanContentFrame_ItemWidth = var['custom_frame_width_vq']

        ### Plan content title ###
        plan_content_title = QgsLayoutItemLabel(layout)
        plan_content_title.setText("Planinhalt")
        plan_content_title.setId("plan_content_title")
        plan_content_title.setFont(QFont(font, font_size_title, QFont.Bold))
        plan_content_title.setMargin(0)

        ## Static Set Up
        planContentTitle_positionX = PlanContentFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
        planContentTitle__ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        plan_content_title.attemptResize(QgsLayoutSize(planContentTitle__ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
        planContentTitle_ItemHeight = self.calculateHeight(plan_content_title)
        plan_content_title.attemptResize(QgsLayoutSize(planContentTitle__ItemWidth, planContentTitle_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        ## Dynamic Set Up
        plan_content_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_width_vq']}) - "
                f"2*to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_item_dist_right_vq']}) - "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )

        plan_content_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression(
                "CalcLabelHeight(@layout_name, 'plan_content_title')"
            ),
        )

        ### Plan content ###
        plan_content = QgsLayoutItemLabel(layout)
        plan_content.setText("XXX")
        plan_content.setId("plan_content")
        plan_content.setFont(QFont(font, font_size))
        plan_content.setMargin(0)

        ## Static Set Up
        planContent_positionX = PlanContentFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
        planContent_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
        plan_content.attemptResize(QgsLayoutSize(planContent_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
        planContent_ItemHeight = self.calculateHeight(plan_content)
        plan_content.attemptResize(QgsLayoutSize(planContent_ItemWidth, planContent_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        PlanContentFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + planContentTitle_ItemHeight + var["custom_dist_title_text_vq"] + planContent_ItemHeight + var["custom_item_dist_bottom_vq"]
        plan_content_frame.attemptResize(QgsLayoutSize(PlanContentFrame_ItemWidth, PlanContentFrame_ItemHeight, QgsUnitTypes.LayoutMillimeters))

        PlanContentFrame_positionY = spieFrame_positionY - PlanContentFrame_ItemHeight
        plan_content_frame.attemptMove(QgsLayoutPoint(PlanContentFrame_positionX, PlanContentFrame_positionY, QgsUnitTypes.LayoutMillimeters))

        planContentTitle_positionY = PlanContentFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
        plan_content_title.attemptMove(QgsLayoutPoint(planContentTitle_positionX, planContentTitle_positionY, QgsUnitTypes.LayoutMillimeters))

        planContent_positionY = planContentTitle_positionY + planContentTitle_ItemHeight + float(var["custom_item_dist_top_vq"])
        plan_content.attemptMove(QgsLayoutPoint(planContent_positionX, planContent_positionY, QgsUnitTypes.LayoutMillimeters))

        ## Dynamic Set Up
        plan_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_width_vq']}) - "
                f"2*to_real({var['custom_frame_line_width_vq']}) - "
                f"to_real({var['custom_item_dist_right_vq']}) - "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )

        plan_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression(
                "CalcLabelHeight(@layout_name, 'plan_content')"
            ),
        )

        plan_content_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemWidth, 
            QgsProperty.fromExpression(f"{var['custom_frame_width_vq']}"),
        )

        plan_content_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.ItemHeight,
            QgsProperty.fromExpression(
                f"to_real({var['custom_frame_line_width_vq']}) + "
                f"to_real({var['custom_item_dist_top_vq']}) + "
                "GetDynamicItemHeight(@layout_name,'plan_content_title') + "
                f"to_real({var['custom_dist_title_text_vq']}) + "
                "GetDynamicItemHeight(@layout_name,'plan_content') + "
                f"to_real({var['custom_item_dist_bottom_vq']})"
            ),
        )

        plan_content_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name,'legend_frame')"
            ),
        )

        plan_content_frame.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name,'spie_frame') - "
                "GetDynamicItemHeight(@layout_name,'plan_content_frame')"
            ),
        )

        plan_content_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name,'plan_content_frame') + "
                f"to_real({var['custom_frame_line_width_vq']})/2 + "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )

        plan_content_title.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name,'plan_content_frame') + "
                f"to_real({var['custom_frame_line_width_vq']})/2 + "
                f"to_real({var['custom_item_dist_top_vq']})"
            ),
        )

        plan_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionX,  
            QgsProperty.fromExpression(
                "GetDynamicItemPositionX(@layout_name,'plan_content_frame') + "
                f"to_real({var['custom_frame_line_width_vq']})/2 + "
                f"to_real({var['custom_item_dist_left_vq']})"
            ),
        )
        plan_content.dataDefinedProperties().setProperty(
            QgsLayoutObject.PositionY,
            QgsProperty.fromExpression(
                "GetDynamicItemPositionY(@layout_name,'plan_content_title') + "
                "GetDynamicItemHeight(@layout_name,'plan_content_title') + "
                f"to_real({var['custom_item_dist_top_vq']})"
            ),
        )


                


        layout.addLayoutItem(map_item)
        layout.addLayoutItem(legend_frame)
        layout.addLayoutItem(legend_title)
        layout.addLayoutItem(legend)
        layout.addLayoutItem(metadata_frame)
        layout.addLayoutItem(metadata)
        layout.addLayoutItem(spie_frame)
        layout.addLayoutItem(spie_title)
        layout.addLayoutItem(spie_logo)
        layout.addLayoutItem(spie_content)
        layout.addLayoutItem(plan_content_frame)
        layout.addLayoutItem(plan_content_title)    
        layout.addLayoutItem(plan_content)

        # title_text = self.user_inputs.get('title', 'Default Title')
        # title = QgsLayoutItemLabel(layout)
        # title.setText(title_text)
        # title.setFont(QFont("Arial", 24, QFont.Bold))
        # title.adjustSizeToText()
        # layout.addLayoutItem(title)
        # title.attemptMove(QgsLayoutPoint(10, 5, QgsUnitTypes.LayoutMillimeters))

        # selected_layers = self.user_inputs.get('selected_layers', [])
        # legend = QgsLayoutItemLegend(layout)
        # legend.setId("legend_frame")
        # legend.setAutoUpdateModel(False)
        # legend_root= legend.model().rootGroup()
        # legend_root.clear()
        # for layer_name in selected_layers:
        #     layer = self.project.mapLayersByName(layer_name)
        #     if layer:
        #         legend_root.addLayer(layer[0])

        # # legend.model().setRootGroup(legend_root)
        # legend.setEqualColumnWidth(True)  # Giúp các cột có độ rộng đều nhau, nhìn cân đối hơn
        # legend.setSplitLayer(True)
        # legend.setLinkedMap(map_item)
        # layout.addLayoutItem(legend)
        # legend.attemptMove(QgsLayoutPoint(8,140,QgsUnitTypes.LayoutMillimeters))

        return layout


