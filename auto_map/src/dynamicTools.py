# from qgis.utils import qgsfunction

# from qgis.core import *
# from qgis.gui import *


# @qgsfunction(args='auto', group='Custom')
# def getDynamicItemPositionX(LayoutName, ItemName, feature, parent):
#     """
#     Returns the X position of a layout item in millimeters.
#     Usage: getDynamicItemPositionX('LayoutName', 'ItemName')
#     """
#     layout_name = LayoutName
#     item_name = ItemName

#     manager = QgsProject.instance().layoutManager()
#     layout = manager.layoutByName(layout_name)

#     get_item = layout.itemById(item_name)
#     get_item_position = get_item.positionWithUnits()
#     get_item_position_x = get_item_position.x()

#     return get_item_position_x

# @qgsfunction(args='auto', group='Custom')
# def getDynamicItemPositionY(LayoutName, ItemName, feature, parent):
#     """
#     Returns the Y position of a layout item in millimeters.
#     Usage: getDynamicItemPositionY('LayoutName', 'ItemName')
#     """
#     layout_name = LayoutName
#     item_name = ItemName

#     manager = QgsProject.instance().layoutManager()
#     layout = manager.layoutByName(layout_name)

#     get_item = layout.itemById(item_name)
#     get_item_position = get_item.positionWithUnits()
#     get_item_position_y = get_item_position.y()

#     return get_item_position_y


# functions_to_load = [getDynamicItemPositionX, getDynamicItemPositionY]

# def register_functions():
#     for func in functions_to_load:
#         QgsExpression.registerFunction(func)

# # def unregister_functions():


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


# --- ĐĂNG KÝ HÀM VÀO QGIS ---
# Danh sách các hàm cần đưa vào QGIS Expression Engine
FUNCTIONS_TO_LOAD = (
    GetDynamicItemPositionX, 
    GetDynamicItemPositionY, 
    GetDynamicItemHeight, 
    GetDynamicItemWidth, 
    CalcLabelHeight
)

def register_functions(is_register=True):
    """
    Hàm này sẽ được gọi ở hàm __init__ của plugin 
    để nạp tất cả các hàm toán học vào QGIS.
    """
    for f in FUNCTIONS_TO_LOAD:
        if is_register:
            QgsExpression.registerFunction(f)
        else:
            QgsExpression.unregisterFunction(f.name())