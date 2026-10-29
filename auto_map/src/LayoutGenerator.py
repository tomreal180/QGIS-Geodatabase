from qgis.core import *
from PyQt5.QtGui import QFontMetricsF
import os

from .dynamicTools import register_functions
# from .Layout.StandardLayout import create_standard_A4_layout
# from .Layout.Layout_Bericht_Unten import create_layout_bericht_unten
from .Layout.LayoutBuilder import build_layout
# from .Layout.A3_layout import create_layout_a3

class LayoutGenerator:

    def __init__(self,project,user_inputs):
        self.project = project
        self.user_inputs = user_inputs
        self.manager = self.project.layoutManager()
        register_functions()  # Register the functions when the module is imported

    def _remove_existing_layouts(self,layout_name):
        existing_layout = self.manager.layoutByName(layout_name)
        if existing_layout:
            self.manager.removeLayout(existing_layout)

    def export_layout(self,layout,output_path):
        exporter = QgsLayoutExporter(layout)
        settings = QgsLayoutExporter.PdfExportSettings()
        exporter.exportToPdf(output_path, settings)
    
    def calculateHeight(self, item, target_width_mm=None, line_spacing=1.0):
        """
        Returns the height of a layout item in millimeters.
        Usage: calculateHeight('Item')
        """
        # Text, Font und Breite des Labels
        text = item.text()
        font = item.font()
        width_mm = target_width_mm if target_width_mm is not None else item.sizeWithUnits().width()
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
        
    def calculateWidth(self, item):
        if not item or not isinstance(item, QgsLayoutItemLabel):
            return 0

        text = item.text()
        font = item.font()
        if not text.strip():
            return 0

        font_metrics = QFontMetricsF(font)
        # get max line width in pixels
        widths_px = [font_metrics.horizontalAdvance(line) for line in text.split("\n")]
        max_width_px = max(widths_px) if widths_px else 0

        # add 5% padding
        max_width_px *= 1.04

        # convert px back to mm (96 dpi assumption)
        width_mm = max_width_px * 25.4 / 96

        return width_mm
    
    
    def create_a4_landscape_layout(self):
        self.variables = {
            "custom_format": "A4",
            "custom_page_dist_left": 3,
            "custom_page_dist_right": 3,
            "custom_page_dist_top": 3,
            "custom_page_dist_bottom": 3,
            "custom_item_dist_left": 1,
            "custom_item_dist_right": 1,
            "custom_item_dist_top": 1,
            "custom_item_dist_bottom": 1,
            "custom_frame_line_width": 0.1,
            "custom_dist_title_text_small": 2,
            "custom_dist_title_text": 0.5,
            "custom_frame_height": 27,          
            "custom_north_arrow_width": 7.5,   
            "custom_north_arrow_height": 12.5,  
            "custom_scale_width": 30,           
            "custom_scale_height": 7.5,        
            
            "custom_scale_label_space": 2,
            "custom_scale_bar_height": 2,
            
            "custom_page_size_width": 297,
            "custom_page_size_height": 210,
            "item_dist_1": 20,
            "item_dist_2": 10,
            "item_dist": 5
        }
        # return create_standard_A4_layout(self)
        return build_layout(self)
    
    def create_a4_portrait_layout(self):
        self.variables = {
            "custom_format": "A4",
            "custom_page_dist_left": 3,
            "custom_page_dist_right": 3,
            "custom_page_dist_top": 3,
            "custom_page_dist_bottom": 3,
            "custom_item_dist_left": 1,
            "custom_item_dist_right": 1,
            "custom_item_dist_top": 1,
            "custom_item_dist_bottom": 1,
            "custom_frame_line_width": 0.1,
            "custom_dist_title_text_small": 2,
            "custom_dist_title_text": 0.5,
            "custom_frame_height": 30,
            "custom_north_arrow_width": 7.5,
            "custom_north_arrow_height": 12.5,
            "custom_scale_width": 30,
            "custom_scale_height": 7.5,
            "custom_scale_label_space": 2,
            "custom_scale_bar_height": 2,
            "custom_page_size_width": 210,
            "custom_page_size_height": 297,
            "item_dist_1": 10,
            "item_dist_2": 1,
            "item_dist": 0.25
        }
        return build_layout(self)

    def create_a3_landscape_layout(self):
        self.variables ={
            "custom_format": "A3",
            "custom_page_dist_left": 3,
            "custom_page_dist_right": 3,
            "custom_page_dist_top": 3,
            "custom_page_dist_bottom": 3,
            "custom_item_dist_left": 1,
            "custom_item_dist_right": 1,
            "custom_item_dist_top": 1,
            "custom_item_dist_bottom": 1,
            "custom_frame_line_width": 0.1,
            "custom_dist_title_text_small": 2,
            "custom_dist_title_text": 0.5,
            "custom_frame_height": 35,
            "custom_north_arrow_width": 9,
            "custom_north_arrow_height": 15,
            "custom_scale_width": 35,
            "custom_scale_height": 9,
            "custom_scale_label_space": 2,
            "custom_scale_bar_height": 2,
            "custom_page_size_width": 420,
            "custom_page_size_height": 297,
            "item_dist_1": 50,
            "item_dist_2": 40,
            "item_dist": 30
        }
        return build_layout(self)
    
    def create_a3_portrait_layout(self):
        self.variables ={
            "custom_format": "A3",
            "custom_page_dist_left": 3,
            "custom_page_dist_right": 3,
            "custom_page_dist_top": 3,
            "custom_page_dist_bottom": 3,
            "custom_item_dist_left": 1,
            "custom_item_dist_right": 1,
            "custom_item_dist_top": 1,
            "custom_item_dist_bottom": 1,
            "custom_frame_line_width": 0.1,
            "custom_dist_title_text_small": 2,
            "custom_dist_title_text": 0.5,
            "custom_frame_height": 35,
            "custom_north_arrow_width": 9,
            "custom_north_arrow_height": 15,
            "custom_scale_width": 35,
            "custom_scale_height": 9,
            "custom_scale_label_space": 2,
            "custom_scale_bar_height": 2,
            "custom_page_size_width": 297,
            "custom_page_size_height": 420,
            "item_dist_1": 50,
            "item_dist_2": 25,
            "item_dist": 10
        }
        return build_layout(self)