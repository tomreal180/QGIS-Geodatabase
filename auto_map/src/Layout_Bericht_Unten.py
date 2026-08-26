from qgis.core import *
from PyQt5.QtGui import QFont, QFontMetricsF
import os

def create_layout_bericht_unten(generator):
    # Font
    font = "Calibri"
    font_size = 10
    font_size_title = 10
    font_size_metadata = 7
    #################################################################
    layout_name = "Bericht_Legende_unten"
    generator._remove_existing_layouts(layout_name)
    
    var = generator.variables    
    layout = QgsPrintLayout(generator.project)
    layout.initializeDefaults()
    layout.setName(layout_name)
    generator.manager.addLayout(layout)

    ########################################################################
    ### Step 1: Initialize Layout Items and Set Static Properties
    ########################################################################
    
    # Map
    map_item = QgsLayoutItemMap(layout)
    map_item.setId("map")
    map_item.setFrameEnabled(True)
    map_item.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_blu"]))
    target_layer = generator.user_inputs.get('target_layer')
    if target_layer:
        map_item.zoomToExtent(target_layer.extent())

    # Legend Frame
    legend_frame = QgsLayoutItemShape(layout)
    legend_frame.setShapeType(QgsLayoutItemShape.Rectangle)
    legend_frame.setId("legend_frame")
    legend_frame.setFrameEnabled(True)
    legend_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_blu"]))

    # Legend Title
    legend_title = QgsLayoutItemLabel(layout)
    legend_title.setId("legend_title")
    legend_title.setText("Legende")
    legend_title.setFont(QFont(font, font_size_title, QFont.Bold))
    legend_title.setMargin(0)

    # Legend Content
    legend = QgsLayoutItemLegend(layout)
    legend.setId("legend")
    legend.setLinkedMap(map_item)
    legend.setLegendFilterByMapEnabled(True)
    legend.setAutoUpdateModel(False)
    legend.model().rootGroup().removeAllChildren()
    for layer_name in generator.user_inputs.get('selected_layers', []):
        layer = generator.project.mapLayersByName(layer_name)
        if layer:
            legend.model().rootGroup().addLayer(layer[0])
    legend.setResizeToContents(True)
    legend.setWrapString('//')
    legend.setStyleFont(QgsLegendStyle.Group, QFont(font, font_size))
    legend.setStyleFont(QgsLegendStyle.Subgroup, QFont(font, font_size))
    legend.setStyleFont(QgsLegendStyle.SymbolLabel, QFont(font, font_size))
    legend.setSymbolWidth(6)
    legend.setSymbolHeight(3)
    legend.setColumnCount(1)
    legend.setEqualColumnWidth(True)
    legend.setSplitLayer(True)
    for style in [QgsLegendStyle.Title, QgsLegendStyle.Group, QgsLegendStyle.Subgroup]:
        legend.rstyle(style).setMargin(0)
    legend.setBoxSpace(0)
    legend.setColumnSpace(var["custom_item_dist_left_blu"])
    legend.rstyle(QgsLegendStyle.Symbol).setMargin(QgsLegendStyle.Left, 0.4)
    legend.rstyle(QgsLegendStyle.Symbol).setMargin(QgsLegendStyle.Top, 3)
    legend.rstyle(QgsLegendStyle.SymbolLabel).setMargin(2)

    # Plan Content Frame
    plan_content_frame = QgsLayoutItemShape(layout)
    plan_content_frame.setShapeType(QgsLayoutItemShape.Rectangle)
    plan_content_frame.setId("plan_content_frame")
    plan_content_frame.setFrameEnabled(True)
    plan_content_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_blu"]))

    # Plan Content Title
    plan_content_title = QgsLayoutItemLabel(layout)
    plan_content_title.setId("plan_content_title")
    plan_content_title.setText("Planinhalt")
    plan_content_title.setFont(QFont(font, font_size_title, QFont.Bold))
    plan_content_title.setMargin(0)

    # Plan Content
    plan_content = QgsLayoutItemLabel(layout)
    plan_content.setId("plan_content")
    planinhalt_content = generator.user_inputs.get('planinhalt', 'XXX')
    plan_content.setText(planinhalt_content if planinhalt_content else "XXX")
    plan_content.setFont(QFont(font, font_size))
    plan_content.setMargin(0)

    # Metadata Frame
    metadata_frame = QgsLayoutItemShape(layout)
    metadata_frame.setShapeType(QgsLayoutItemShape.Rectangle)
    metadata_frame.setId("metadata_frame")
    metadata_frame.setFrameEnabled(True)
    metadata_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_blu"]))

    # Metadata Label
    metadata = QgsLayoutItemLabel(layout)
    metadata.setId("metadata")
    datagrundlage = generator.user_inputs.get('datengrundlage', 'XXX')
    hintergrundlage = generator.user_inputs.get('hintergrundlage', 'XXX')
    Sonstige = generator.user_inputs.get('sonstige', '')
    metadata_text = f"Datengrundlage: \n© {datagrundlage if datagrundlage else 'XXX'}\nHintergrundkarte: \n© {hintergrundlage if hintergrundlage else 'XXX'}\n"
    if Sonstige: metadata_text += f"Sonstige Karteninhalte: \n{Sonstige}\n"
    metadata.setText(metadata_text)
    metadata.setFont(QFont(font, font_size_metadata))
    metadata.setMargin(0)

    # Municipality Box (Auftragsbox)
    municipality_box = QgsLayoutItemShape(layout)
    municipality_box.setShapeType(QgsLayoutItemShape.Rectangle)
    municipality_box.setId("municipality_box")
    municipality_box.setBackgroundEnabled(False)
    municipality_box.setSymbol(QgsFillSymbol.createSimple({"color": "255, 255, 255, 155", "outline_color": "0, 0, 0, 0", "outline_width": str(var["custom_frame_line_width_blu"])}))
    municipality_box.setFrameEnabled(False)

    municipality_label = QgsLayoutItemLabel(layout)
    municipality_label.setId("municipality_label")
    municipality_label.setFrameEnabled(False)
    muni_text = generator.user_inputs.get('auftraggeber')
    municipality_label.setText(muni_text if muni_text else "Gemeinde/Stadt\nXX")
    municipality_label.setFont(QFont(font, font_size))
    municipality_label.setMargin(0)


    ########################################################################
    ### Step 2: Static Calculations and Set Positions
    ########################################################################
    
    # --- Calculate Width Item ---
    right_col_W = float(var["custom_frame_width_blu"])
    left_col_W = float(var["custom_page_size_width_blu"]) - right_col_W - float(var["custom_frame_line_width_blu"])
    
    content_right_W = right_col_W - 2*var["custom_frame_line_width_blu"] - var["custom_item_dist_left_blu"] - var["custom_item_dist_right_blu"]
    content_left_W = left_col_W - 2*var["custom_frame_line_width_blu"] - var["custom_item_dist_left_blu"] - var["custom_item_dist_right_blu"]

    # --- Set Width and Measure Height for Right Column ---
    metadata.attemptResize(QgsLayoutSize(content_right_W, 0, QgsUnitTypes.LayoutMillimeters))
    meta_H = generator.calculateHeight(metadata)
    metadata.attemptResize(QgsLayoutSize(content_right_W, meta_H, QgsUnitTypes.LayoutMillimeters))
    meta_frame_H = var["custom_frame_line_width_blu"] + var["custom_item_dist_top_blu"] + meta_H + var["custom_item_dist_bottom_blu"]

    plan_content_title.attemptResize(QgsLayoutSize(content_right_W, 0, QgsUnitTypes.LayoutMillimeters))
    pct_H = generator.calculateHeight(plan_content_title)
    plan_content_title.attemptResize(QgsLayoutSize(content_right_W, pct_H, QgsUnitTypes.LayoutMillimeters))

    plan_content.attemptResize(QgsLayoutSize(content_right_W, 0, QgsUnitTypes.LayoutMillimeters))
    pc_H = generator.calculateHeight(plan_content)
    plan_content.attemptResize(QgsLayoutSize(content_right_W, pc_H, QgsUnitTypes.LayoutMillimeters))
    
    plan_frame_H = var["custom_frame_line_width_blu"] + var["custom_item_dist_top_blu"] + pct_H + var["custom_dist_title_text_blu"] + pc_H + var["custom_item_dist_bottom_blu"]

    right_col_total_H = meta_frame_H + plan_frame_H

    # --- Set Width and Measure Height for Left Column ---
    legend_title.attemptResize(QgsLayoutSize(content_left_W, 0, QgsUnitTypes.LayoutMillimeters))
    lt_H = generator.calculateHeight(legend_title)
    legend_title.attemptResize(QgsLayoutSize(content_left_W, lt_H, QgsUnitTypes.LayoutMillimeters))

    layout.addLayoutItem(legend) # Cần add vào layout trước để đo Legend chính xác
    legend.attemptResize(QgsLayoutSize(content_left_W, 0, QgsUnitTypes.LayoutMillimeters))
    layout.refresh()
    legend.adjustBoxSize()
    leg_H = legend.sizeWithUnits().height()
    legend.attemptResize(QgsLayoutSize(content_left_W, leg_H, QgsUnitTypes.LayoutMillimeters))

    left_col_content_H = var["custom_frame_line_width_blu"] + var["custom_item_dist_top_blu"] + lt_H + var["custom_dist_title_text_blu"] + leg_H + var["custom_item_dist_bottom_blu"]

    # --- Calculate Page Height and Legend Frame Height ---
    legend_frame_H = max(right_col_total_H, left_col_content_H)
    static_page_H = var["custom_map_height_blu"] + legend_frame_H + var["custom_frame_line_width_blu"]

    # Set static Page
    page = layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(var["custom_page_size_width_blu"], static_page_H, QgsUnitTypes.LayoutMillimeters))

    # --- Set coordinates (Move) for the blocks ---
    map_X = var["custom_frame_line_width_blu"]/2
    map_Y = var["custom_frame_line_width_blu"]/2
    map_W = var["custom_page_size_width_blu"] - var["custom_frame_line_width_blu"]
    map_item.attemptResize(QgsLayoutSize(map_W, var["custom_map_height_blu"], QgsUnitTypes.LayoutMillimeters))
    map_item.attemptMove(QgsLayoutPoint(map_X, map_Y, QgsUnitTypes.LayoutMillimeters))

    lf_X = var["custom_frame_line_width_blu"]/2
    lf_Y = static_page_H - right_col_total_H - var["custom_frame_line_width_blu"]/2
    legend_frame.attemptResize(QgsLayoutSize(left_col_W, legend_frame_H, QgsUnitTypes.LayoutMillimeters))
    legend_frame.attemptMove(QgsLayoutPoint(lf_X, lf_Y, QgsUnitTypes.LayoutMillimeters))

    legend_title.attemptMove(QgsLayoutPoint(lf_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], lf_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"], QgsUnitTypes.LayoutMillimeters))
    legend.attemptMove(QgsLayoutPoint(lf_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], lf_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"] + lt_H + var["custom_dist_title_text_blu"], QgsUnitTypes.LayoutMillimeters))

    metaF_X = var["custom_page_size_width_blu"] - right_col_W - var["custom_frame_line_width_blu"]/2
    metaF_Y = static_page_H - meta_frame_H - var["custom_frame_line_width_blu"]/2
    metadata_frame.attemptResize(QgsLayoutSize(right_col_W, meta_frame_H, QgsUnitTypes.LayoutMillimeters))
    metadata_frame.attemptMove(QgsLayoutPoint(metaF_X, metaF_Y, QgsUnitTypes.LayoutMillimeters))
    metadata.attemptMove(QgsLayoutPoint(metaF_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], metaF_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"], QgsUnitTypes.LayoutMillimeters))

    planF_X = metaF_X
    planF_Y = metaF_Y - plan_frame_H
    plan_content_frame.attemptResize(QgsLayoutSize(right_col_W, plan_frame_H, QgsUnitTypes.LayoutMillimeters))
    plan_content_frame.attemptMove(QgsLayoutPoint(planF_X, planF_Y, QgsUnitTypes.LayoutMillimeters))
    
    plan_content_title.attemptMove(QgsLayoutPoint(planF_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], planF_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"], QgsUnitTypes.LayoutMillimeters))
    plan_content.attemptMove(QgsLayoutPoint(planF_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], planF_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"] + pct_H + var["custom_dist_title_text_blu"], QgsUnitTypes.LayoutMillimeters))

    # Calculate static Municipality Box (Auftragsbox) WITHOUT LOGO
    metrics = QFontMetricsF(municipality_label.font())
    muni_lines = municipality_label.text().split('\n')
    muni_label_W_px = max([metrics.horizontalAdvance(l) for l in muni_lines]) * 1.04
    muni_label_W = muni_label_W_px * 25.4 / 96
    muni_label_H = generator.calculateHeight(municipality_label)
    
    muni_box_W = muni_label_W + var["custom_frame_line_width_blu"] + var["custom_item_dist_left_blu"] + var["custom_item_dist_right_blu"]
    muni_box_H = var["custom_frame_line_width_blu"]/2 + muni_label_H + var["custom_item_dist_top_blu"] + var["custom_item_dist_bottom_blu"]
    
    muni_box_X = var["custom_page_size_width_blu"] - muni_box_W - var["custom_frame_line_width_blu"]
    muni_box_Y = var["custom_frame_line_width_blu"]/2
    
    municipality_box.attemptResize(QgsLayoutSize(muni_box_W, muni_box_H, QgsUnitTypes.LayoutMillimeters))
    municipality_box.attemptMove(QgsLayoutPoint(muni_box_X, muni_box_Y, QgsUnitTypes.LayoutMillimeters))
    
    municipality_label.attemptResize(QgsLayoutSize(muni_label_W, muni_label_H, QgsUnitTypes.LayoutMillimeters))
    municipality_label.attemptMove(QgsLayoutPoint(muni_box_X + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_left_blu"], muni_box_Y + var["custom_frame_line_width_blu"]/2 + var["custom_item_dist_top_blu"], QgsUnitTypes.LayoutMillimeters))

    ########################################################################
    ### Step 3: Dynamic Injection (for F5)
    ########################################################################
    
    # PAGE
    page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']}"))
    page.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight, 
        QgsProperty.fromExpression(f"{var['custom_map_height_blu']} + GetDynamicItemHeight(@layout_name, 'legend_frame') + {var['custom_frame_line_width_blu']}")
    )

    # MAP
    map_item.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']}/2"))
    map_item.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']}/2"))
    map_item.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - {var['custom_frame_line_width_blu']}"))
    map_item.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_map_height_blu']}"))

    # PLAN CONTENT FRAME
    plan_content_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression("GetDynamicItemPositionX(@layout_name ,'metadata_frame')"))
    plan_content_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression("GetDynamicItemPositionY(@layout_name,'metadata_frame') - GetDynamicItemHeight(@layout_name,'plan_content_frame')"))
    plan_content_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_frame_width_blu']}"))
    
    expr_plan_h_text = f"to_real({var['custom_frame_line_width_blu']}) + to_real({var['custom_item_dist_top_blu']}) + GetDynamicItemHeight(@layout_name,'plan_content_title') + to_real({var['custom_dist_title_text_blu']}) + GetDynamicItemHeight(@layout_name,'plan_content') + to_real({var['custom_item_dist_bottom_blu']})"
    expr_plan_h_text_meta = f"GetDynamicItemHeight(@layout_name,'metadata_frame') + {expr_plan_h_text}"
    expr_legend_h_text = f"to_real({var['custom_frame_line_width_blu']}) + to_real({var['custom_item_dist_top_blu']}) + GetDynamicItemHeight(@layout_name,'legend_title') + to_real({var['custom_dist_title_text_blu']}) + GetDynamicItemHeight(@layout_name,'legend') + to_real({var['custom_item_dist_bottom_blu']})"
    expr_plan_h_legend = "GetDynamicItemHeight(@layout_name,'legend_frame') - GetDynamicItemHeight(@layout_name,'metadata_frame')"
    expr_plan_content_frame_height = f"if({expr_plan_h_text_meta} > {expr_legend_h_text}, {expr_plan_h_text}, {expr_plan_h_legend})"
    plan_content_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(expr_plan_content_frame_height))

    plan_content_title.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name ,'plan_content_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    plan_content_title.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name ,'plan_content_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_top_blu']}"))
    plan_content_title.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_frame_width_blu']} - 2*{var['custom_frame_line_width_blu']} - {var['custom_item_dist_right_blu']} - {var['custom_item_dist_left_blu']}"))
    plan_content_title.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'plan_content_title')"))

    plan_content.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name ,'plan_content_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    plan_content.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name, 'plan_content_title') + GetDynamicItemHeight(@layout_name,'plan_content_title') + {var['custom_dist_title_text_blu']}"))
    plan_content.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_frame_width_blu']} - 2*{var['custom_frame_line_width_blu']} - {var['custom_item_dist_right_blu']} - {var['custom_item_dist_left_blu']}"))
    plan_content.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'plan_content')"))

    # METADATA FRAME
    metadata_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - {var['custom_frame_width_blu']} - {var['custom_frame_line_width_blu']}/2"))
    metadata_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetPageSizeHeight(@layout_name) - GetDynamicItemHeight(@layout_name, 'metadata_frame') - {var['custom_frame_line_width_blu']}/2"))
    metadata_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_frame_width_blu']}"))
    expr_meta_frame_h = f"{var['custom_frame_line_width_blu']} + {var['custom_item_dist_top_blu']} + GetDynamicItemHeight(@layout_name,'metadata') + {var['custom_item_dist_bottom_blu']}"
    metadata_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(expr_meta_frame_h))

    metadata.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name ,'metadata_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    metadata.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name ,'metadata_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_top_blu']}"))
    metadata.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_frame_width_blu']} - 2*{var['custom_frame_line_width_blu']} - {var['custom_item_dist_right_blu']} - {var['custom_item_dist_left_blu']}"))
    metadata.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'metadata')"))

    # LEGEND FRAME
    legend_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']}/2"))
    legend_frame.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetPageSizeHeight(@layout_name) - GetDynamicItemHeight(@layout_name, 'plan_content_frame') - GetDynamicItemHeight(@layout_name, 'metadata_frame') - {var['custom_frame_line_width_blu']}/2"))
    legend_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - {var['custom_frame_width_blu']} - {var['custom_frame_line_width_blu']}"))
    expr_legend_frame_h = f"if({expr_plan_h_text_meta} > {expr_legend_h_text}, {expr_plan_h_text_meta}, {expr_legend_h_text})"
    legend_frame.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(expr_legend_frame_h))

    legend_title.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name ,'legend_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    legend_title.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name ,'legend_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_top_blu']}"))
    legend_title.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - {var['custom_frame_width_blu']} - 2*{var['custom_frame_line_width_blu']} - {var['custom_item_dist_right_blu']} - {var['custom_item_dist_left_blu']}"))
    legend_title.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'legend_title')"))

    legend.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name ,'legend_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    legend.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name ,'legend_frame') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_top_blu']} + GetDynamicItemHeight(@layout_name,'legend_title') + {var['custom_dist_title_text_blu']}"))
    legend.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - {var['custom_frame_width_blu']} - 2*{var['custom_frame_line_width_blu']} - {var['custom_item_dist_right_blu']} - {var['custom_item_dist_left_blu']}"))

    # MUNICIPALITY BOX WITHOUT LOGO
    municipality_box.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_page_size_width_blu']} - GetDynamicItemWidth(@layout_name, 'municipality_box') - {var['custom_frame_line_width_blu']}"))
    municipality_box.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']}/2"))
    
    expr_muni_box_w = f"GetDynamicItemWidth(@layout_name, 'municipality_label') + {var['custom_frame_line_width_blu']} + {var['custom_item_dist_left_blu']} + {var['custom_item_dist_right_blu']}"
    municipality_box.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(expr_muni_box_w))
    
    expr_muni_box_h = f"{var['custom_frame_line_width_blu']} / 2 + GetDynamicItemHeight(@layout_name, 'municipality_label') + {var['custom_item_dist_top_blu']} + {var['custom_item_dist_bottom_blu']}"
    municipality_box.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(expr_muni_box_h))

    municipality_label.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"GetDynamicItemPositionX(@layout_name, 'municipality_box') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_left_blu']}"))
    municipality_label.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemPositionY(@layout_name, 'municipality_box') + {var['custom_frame_line_width_blu']}/2 + {var['custom_item_dist_top_blu']}"))
    municipality_label.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression("CalcLabelWidth(@layout_name, 'municipality_label')"))
    municipality_label.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression("CalcLabelHeight(@layout_name, 'municipality_label')"))

    ########################################################################
    ### Step 4: Add to Layout (North Arrow & Scale Bar added last)
    ########################################################################
    
    layout.addLayoutItem(map_item)
    layout.addLayoutItem(legend_frame)
    layout.addLayoutItem(legend_title)
    
    layout.addLayoutItem(metadata_frame)
    layout.addLayoutItem(metadata)
    
    layout.addLayoutItem(plan_content_frame)
    layout.addLayoutItem(plan_content_title)
    layout.addLayoutItem(plan_content)
    
    layout.addLayoutItem(municipality_box)
    layout.addLayoutItem(municipality_label) 

    # North Arrow
    north_arrow = QgsLayoutItemPicture(layout)
    north_arrow.setId("north_arrow")
    north_arrow.setFrameEnabled(False)
    north_arrow.setPicturePath(os.path.join(os.path.dirname(__file__), "assets", "NorthArrow.svg"))
    north_arrow.setLinkedMap(map_item)
    north_arrow.setNorthMode(0)
    north_arrow.attemptResize(QgsLayoutSize(var["custom_north_arrow_width_blu"], var["custom_north_arrow_height_blu"], QgsUnitTypes.LayoutMillimeters))
    north_arrow.attemptMove(QgsLayoutPoint(var["custom_frame_line_width_blu"] + var["custom_item_dist_left_blu"], var["custom_frame_line_width_blu"] + var["custom_item_dist_top_blu"], QgsUnitTypes.LayoutMillimeters))
    north_arrow.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']} + {var['custom_item_dist_left_blu']}"))
    north_arrow.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']} + {var['custom_item_dist_top_blu']}"))
    north_arrow.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_north_arrow_width_blu']}"))
    north_arrow.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_north_arrow_height_blu']}"))
    layout.addLayoutItem(north_arrow)

    # Scale Bar
    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setId("scale_bar")
    scale_bar.setFrameEnabled(False)
    scale_bar.setStyle("Single Box")
    scale_bar.setBoxContentSpace(0)
    scale_bar.setFont(QFont(font, font_size_metadata))
    scale_bar.setLabelBarSpace(var["custom_scale_label_space_blu"])
    scale_bar.setLinkedMap(map_item)
    scale_bar.setHeight(var["custom_scale_bar_height_blu"])
    scale_bar.setSegmentSizeMode(Qgis.ScaleBarSegmentSizeMode.Fixed)
    scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
    scale_bar.setMapUnitsPerScaleBarUnit(1)
    scale_bar.setUnitsPerSegment(100)
    scale_bar.setNumberOfSegments(2)
    scale_bar.setNumberOfSegmentsLeft(0)
    scale_bar.setUnitLabel("m")
    scale_bar.setReferencePoint(QgsLayoutItem.LowerLeft)
    
    sb_X = var["custom_frame_line_width_blu"] + var["custom_item_dist_left_blu"] - 0.4
    sb_Y = var["custom_map_height_blu"] + var["custom_frame_line_width_blu"]/2 - var["custom_item_dist_bottom_blu"] + 0.525
    sb_W = scale_bar.sizeWithUnits().width()
    sb_H = var["custom_scale_bar_height_blu"] + var["custom_scale_label_space_blu"] + int(font_size_metadata)*0.352778
    scale_bar.attemptResize(QgsLayoutSize(sb_W, sb_H, QgsUnitTypes.LayoutMillimeters))
    scale_bar.attemptMove(QgsLayoutPoint(sb_X, sb_Y, QgsUnitTypes.LayoutMillimeters))
    
    scale_bar.dataDefinedProperties().setProperty(QgsLayoutObject.PositionX, QgsProperty.fromExpression(f"{var['custom_frame_line_width_blu']} + {var['custom_item_dist_left_blu']} - 0.4"))
    scale_bar.dataDefinedProperties().setProperty(QgsLayoutObject.PositionY, QgsProperty.fromExpression(f"GetDynamicItemHeight(@layout_name, 'map') + {var['custom_frame_line_width_blu']}/2 - {var['custom_item_dist_bottom_blu']} + 0.525"))
    scale_bar.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_scale_bar_height_blu']} + {var['custom_scale_label_space_blu']} + {int(font_size_metadata)}*0.352778"))
    layout.addLayoutItem(scale_bar)

    return layout