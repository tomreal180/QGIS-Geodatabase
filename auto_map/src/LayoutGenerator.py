from qgis.core import *
from PyQt5.QtGui import QFontMetricsF
import os

from .dynamicTools import register_functions
from .StandardLayout import create_standard_A4_layout
from .Layout_Bericht_Unten import create_layout_bericht_unten

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
            "custom_north_arrow_width_vq": 15,
            "custom_north_arrow_height_vq": 20,
            "custom_scale_width_vq": 35,
            "custom_scale_height_vq": 9,
            "custom_scale_label_space_vq": 2,
            "custom_scale_bar_height_vq": 2,
            "custom_page_size_width_vq": 297,
            "custom_page_size_height_vq": 210,
        }
        return create_standard_A4_layout(self)

    def create_bericht_legende_unten_layout(self):
        self.variables = {
            "custom_page_size_width_blu": 169.03,
            "custom_map_height_blu": 120.535,
            "custom_page_dist_left_blu": 3,
            "custom_page_dist_right_blu": 3,
            "custom_page_dist_top_blu": 3,
            "custom_page_dist_bottom_blu": 3,
            "custom_item_dist_left_blu": 3,
            "custom_item_dist_right_blu": 3,
            "custom_item_dist_top_blu": 3,
            "custom_item_dist_bottom_blu": 3,
            "custom_frame_line_width_blu": 0.3,
            "custom_dist_title_text_blu": 2,
            "custom_frame_width_blu": 40,
            "custom_north_arrow_width_blu": 5,
            "custom_north_arrow_height_blu": 8,
            "custom_scale_width_blu": 35,
            "custom_scale_height_blu": 9,
            "custom_scale_label_space_blu": 2,
            "custom_scale_bar_height_blu": 2,
        }
        return create_layout_bericht_unten(self)
    