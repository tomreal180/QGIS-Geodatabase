from qgis.utils import qgsfunction
from qgis.core import QgsProject, QgsExpression, QgsLayoutItemLabel
from PyQt5.QtGui import QFontMetricsF

@qgsfunction(args='auto', group='Custom Layout')
def GetDynamicItemPositionX(layout_name, item_name, feature, parent):
    """Lấy tọa độ X hiện tại của một Item"""
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)
    if not layout: return 0
    
    item = layout.itemById(item_name)
    if not item: return 0
    
    return item.positionWithUnits().x()


@qgsfunction(args='auto', group='Custom Layout')
def GetDynamicItemPositionY(layout_name, item_name, feature, parent):
    """Lấy tọa độ Y hiện tại của một Item"""
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)
    if not layout: return 0
    
    item = layout.itemById(item_name)
    if not item: return 0
    
    return item.positionWithUnits().y()


@qgsfunction(args='auto', group='Custom Layout')
def GetDynamicItemHeight(layout_name, item_name, feature, parent):
    """Lấy chiều cao hiện tại của một Item"""
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)
    if not layout: return 0
    
    item = layout.itemById(item_name)
    if not item: return 0
    
    return item.sizeWithUnits().height()


@qgsfunction(args='auto', group='Custom Layout')
def GetDynamicItemWidth(layout_name, item_name, feature, parent):
    """Lấy chiều rộng hiện tại của một Item"""
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)
    if not layout: return 0
    
    item = layout.itemById(item_name)
    if not item: return 0
    
    return item.sizeWithUnits().width()


@qgsfunction(args='auto', group='Custom Layout')
def CalcLabelHeight(layout_name, item_name, feature, parent):
    """
    Tính toán chính xác chiều cao cần thiết cho một Text Label (dựa trên nội dung chữ).
    Đã được thiết kế cứng line_spacing = 1.0 để dùng gọn gàng trong Expression.
    """
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)
    if not layout: return 0

    item = layout.itemById(item_name)
    # Phải đảm bảo item tồn tại và đúng là Label
    if not item or not isinstance(item, QgsLayoutItemLabel): 
        return 0

    text = item.text()
    font = item.font()
    width_mm = item.sizeWithUnits().width()
    
    if not text.strip():
        return 0

    # Chuyển đổi mm sang Pixel (Giả định 96 dpi)
    width_px = width_mm * 96 / 25.4
    metrics = QFontMetricsF(font)

    lines = []
    paragraphs = text.split('\n')

    for para in paragraphs:
        if para.strip() == "":
            lines.append(" ")
            continue

        words = para.split(" ")
        current_line = ""

        for word in words:
            test_line = word if current_line == "" else current_line + " " + word
            
            # Kiểm tra xem dòng chữ có bị tràn ra khỏi chiều rộng (width_px) không
            if metrics.boundingRect(test_line).width() > width_px:
                if current_line != "":
                    lines.append(current_line)
                current_line = word
            else:
                current_line = test_line

        if current_line != "":
            lines.append(current_line)

    # Tính tổng chiều cao của tất cả các dòng
    total_height_px = sum([metrics.boundingRect(line).height() for line in lines])

    # Hệ số an toàn (Padding)
    total_height_px *= 1.025

    # Chuyển đổi ngược lại từ Pixel sang milimet
    height_mm = total_height_px * 25.4 / 96
    return height_mm

@qgsfunction(args="auto", group="Custom")
def CalcLabelWidth(layout_name, item_id, feature, parent):
    layout = QgsProject.instance().layoutManager().layoutByName(layout_name)
    if not layout:
        return 0

    item = layout.itemById(item_id)
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


@qgsfunction(args='auto', group='Custom')
def GetPageSizeWidth(LayoutName):
    layout_name = LayoutName

    # Layout abfragen
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)

    # Printseite --> Größe der Printseite --> Breite
    page = layout.pageCollection().page(0)
    size = page.pageSize()
    width_mm = size.width()

    return width_mm


@qgsfunction(args='auto', group='Custom')
def GetPageSizeHeight(LayoutName):
    layout_name = LayoutName

    # Layout abfragen
    manager = QgsProject.instance().layoutManager()
    layout = manager.layoutByName(layout_name)

    # Printseite --> Größe der Printseite --> Höhe
    page = layout.pageCollection().page(0)
    size = page.pageSize()
    height_mm = size.height()

    return height_mm
# --- Register functions in QGIS ---
# List of functions needed in QGIS Expression Engine
FUNCTIONS_TO_LOAD = (
    GetDynamicItemPositionX, 
    GetDynamicItemPositionY, 
    GetDynamicItemHeight, 
    GetDynamicItemWidth, 
    CalcLabelHeight,
    GetPageSizeWidth,
    GetPageSizeHeight
)

def register_functions(is_register=True):
    """
    Register or unregister the custom functions in QGIS Expression Engine.
    """
    for f in FUNCTIONS_TO_LOAD:
        if is_register:
            QgsExpression.registerFunction(f)
        else:
            QgsExpression.unregisterFunction(f.name())