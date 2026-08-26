from qgis.core import *
from PyQt5.QtGui import QFont, QFontMetricsF

import os

def create_standard_A4_layout(generator):
    # Font
    font = "Calibri"
    font_size = 10
    font_size_title = 10
    font_size_metadata = 7
    #################################################################
    layout_name = "Standard Layout"
    generator._remove_existing_layouts(layout_name)
    var = generator.variables  
    layout = QgsPrintLayout(generator.project)
    layout.initializeDefaults()
    layout.setName(layout_name)
    generator.manager.addLayout(layout)
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
    target_layer = generator.user_inputs.get('target_layer')
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
    lt_itemHeight = generator.calculateHeight(legend_title)
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
    selected_layers = generator.user_inputs.get('selected_layers', [])

    legend = QgsLayoutItemLegend(layout)
    legend.setId("legend")
    legend.setLinkedMap(map_item)
    legend.setLegendFilterByMapEnabled(True)
    legend.setAutoUpdateModel(False)
    legend.model().rootGroup().removeAllChildren()

    for layer_name in selected_layers:
        layer = generator.project.mapLayersByName(layer_name)
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
    datagrundlage = generator.user_inputs.get('datengrundlage')
    datagrundlage = datagrundlage if datagrundlage else "XXX"
    hintergrundlage = generator.user_inputs.get('hintergrundlage')
    hintergrundlage = hintergrundlage if hintergrundlage else "XXX"
    Sonstige = generator.user_inputs.get('sonstige')
    metadata_text = f"Datengrundlage: \n© {datagrundlage}\nHintergrundkarte: \n© {hintergrundlage}\n"
    if Sonstige:
        metadata_text += f"Sonstige Karteninhalte: \n{Sonstige}\n"
    
    metadata = QgsLayoutItemLabel(layout)
    metadata.setText(
        metadata_text
    )
    metadata.setFont(QFont(font, font_size_metadata))
    metadata.setMargin(0)
    metadata.setId("metadata")

    ##Static Set Up
    metadata_PositionX = metaF_PositionX + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_left_vq"]
    metadata_itemWidth = float(var["custom_frame_width_vq"]) - float(2*var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    metadata.attemptResize(QgsLayoutSize(metadata_itemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    metadata_itemHeight = generator.calculateHeight(metadata)
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
    spieTitle_ItemHeight = generator.calculateHeight(spie_title)
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
    spieContent_ItemHeight = generator.calculateHeight(spie_content)
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
            "(GetDynamicItemPositionX(@layout_name,'spie_frame') + "
            f"{var['custom_frame_width_vq'] - var['custom_item_dist_right_vq']}"
            " - GetDynamicItemPositionX(@layout_name, 'spie_content')"
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
    planContentFrame_positionX = lf_positionX
    planContentFrame_ItemWidth = var['custom_frame_width_vq']

    ### Plan content title ###
    plan_content_title = QgsLayoutItemLabel(layout)
    plan_content_title.setText("Planinhalt")
    plan_content_title.setId("plan_content_title")
    plan_content_title.setFont(QFont(font, font_size_title, QFont.Bold))
    plan_content_title.setMargin(0)

    ## Static Set Up
    planContentTitle_positionX = planContentFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    planContentTitle_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    plan_content_title.attemptResize(QgsLayoutSize(planContentTitle_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    planContentTitle_ItemHeight = generator.calculateHeight(plan_content_title)
    plan_content_title.attemptResize(QgsLayoutSize(planContentTitle_ItemWidth, planContentTitle_ItemHeight, QgsUnitTypes.LayoutMillimeters))

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
    planinhalt_content = generator.user_inputs.get('planinhalt')
    planinhalt_content = planinhalt_content if planinhalt_content else "XXX"
    plan_content = QgsLayoutItemLabel(layout)
    plan_content.setText(planinhalt_content)
    plan_content.setId("plan_content")
    plan_content.setFont(QFont(font, font_size))
    plan_content.setMargin(0)

    ## Static Set Up
    planContent_positionX = planContentFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    planContent_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    plan_content.attemptResize(QgsLayoutSize(planContent_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    planContent_ItemHeight = generator.calculateHeight(plan_content)
    plan_content.attemptResize(QgsLayoutSize(planContent_ItemWidth, planContent_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    planContentFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + planContentTitle_ItemHeight + var["custom_dist_title_text_vq"] + planContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    plan_content_frame.attemptResize(QgsLayoutSize(planContentFrame_ItemWidth, planContentFrame_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    planContentFrame_positionY = spieFrame_positionY - planContentFrame_ItemHeight
    plan_content_frame.attemptMove(QgsLayoutPoint(planContentFrame_positionX, planContentFrame_positionY, QgsUnitTypes.LayoutMillimeters))

    planContentTitle_positionY = planContentFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
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


    ########################################################################
    ### Project
    ### Project frame ### 
    project_frame = QgsLayoutItemShape(layout)
    project_frame.setShapeType(QgsLayoutItemShape.Rectangle)
    project_frame.setId("project_frame")
    project_frame.setFrameEnabled(True)
    project_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var['custom_frame_line_width_vq']))
    
    ## Static Set Up
    projectFrame_positionX = lf_positionX
    projectFrame_ItemWidth = var['custom_frame_width_vq']

    ### Project title ###
    project_title = QgsLayoutItemLabel(layout)
    project_title.setText("Projekt")
    project_title.setId("project_title")
    project_title.setFont(QFont(font, font_size_title, QFont.Bold))
    project_title.setMargin(0)
    
    ### Static Set Up
    projectTitle_positionX = projectFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    projectTitle_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    project_title.attemptResize(QgsLayoutSize(projectTitle_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    projectTitle_ItemHeight = generator.calculateHeight(project_title)
    project_title.attemptResize(QgsLayoutSize(projectTitle_ItemWidth, projectTitle_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    ## Dynamic Set Up
    project_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_width_vq']}) - "
            f"2*to_real({var['custom_frame_line_width_vq']}) - "
            f"to_real({var['custom_item_dist_right_vq']}) - "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    project_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            "CalcLabelHeight(@layout_name, 'project_title')"
        ),
    )
    
    ### project content ###
    project_name = generator.user_inputs.get('title')
    project_name = project_name if project_name else "XXX"
    project_content = QgsLayoutItemLabel(layout)
    project_content.setText(project_name)
    project_content.setId("project_content")
    project_content.setFont(QFont(font, font_size))
    project_content.setMargin(0)

    ## Static Set Up
    projectContent_positionX = projectFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    projectContent_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    project_content.attemptResize(QgsLayoutSize(projectContent_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    projectContent_ItemHeight = generator.calculateHeight(project_content)
    project_content.attemptResize(QgsLayoutSize(projectContent_ItemWidth, projectContent_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    projectFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + projectTitle_ItemHeight + var["custom_dist_title_text_vq"] + projectContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    project_frame.attemptResize(QgsLayoutSize(projectFrame_ItemWidth, projectFrame_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    projectFrame_positionY = planContentFrame_positionY - projectFrame_ItemHeight
    project_frame.attemptMove(QgsLayoutPoint(projectFrame_positionX, projectFrame_positionY, QgsUnitTypes.LayoutMillimeters))

    projectTitle_positionY = projectFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
    project_title.attemptMove(QgsLayoutPoint(projectTitle_positionX, projectTitle_positionY, QgsUnitTypes.LayoutMillimeters))

    projectContent_positionY = projectTitle_positionY + projectTitle_ItemHeight + float(var["custom_item_dist_top_vq"])
    project_content.attemptMove(QgsLayoutPoint(projectContent_positionX, projectContent_positionY, QgsUnitTypes.LayoutMillimeters))

    ## Dynamic Set Up
    project_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_width_vq']}) - "
            f"2*to_real({var['custom_frame_line_width_vq']}) - "
            f"to_real({var['custom_item_dist_right_vq']}) - "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    project_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            "CalcLabelHeight(@layout_name, 'project_content')"
        ),
    )

    project_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth, 
        QgsProperty.fromExpression(f"{var['custom_frame_width_vq']}"),
    )

    project_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_line_width_vq']}) + "
            f"to_real({var['custom_item_dist_top_vq']}) + "
            "GetDynamicItemHeight(@layout_name,'project_title') + "
            f"to_real({var['custom_dist_title_text_vq']}) + "
            "GetDynamicItemHeight(@layout_name,'project_content') + "
            f"to_real({var['custom_item_dist_bottom_vq']})"
        ),
    )

    project_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'legend_frame')"
        ),
    )

    project_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'plan_content_frame') - "
            "GetDynamicItemHeight(@layout_name,'project_frame')"
        ),
    )

    project_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'project_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    project_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'project_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_top_vq']})"
        ),
    )

    project_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,  
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'project_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )
    project_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'project_title') + "
            "GetDynamicItemHeight(@layout_name,'project_title') + "
            f"to_real({var['custom_item_dist_top_vq']})"
        ),
    )
    
    
    ########################################################################
    ### Auftragsbox
    ### Auftragsbox frame ####
    municipality_frame = QgsLayoutItemShape(layout)
    municipality_frame.setShapeType(QgsLayoutItemShape.Rectangle)
    municipality_frame.setId("municipality_frame")
    municipality_frame.setFrameEnabled(True)
    municipality_frame.setFrameStrokeWidth(QgsLayoutMeasurement(var["custom_frame_line_width_vq"]))
    
    ## Static Set Up
    municipalityFrame_positionX = lf_positionX
    municipalityFrame_ItemWidth = var['custom_frame_width_vq']

    ### Auftragsbox title ###
    municipality_title = QgsLayoutItemLabel(layout)
    municipality_title.setText("Auftraggeber")
    municipality_title.setId("municipality_title")
    municipality_title.setFont(QFont(font, font_size_title, QFont.Bold))
    municipality_title.setMargin(0)
    
    ### Static Set Up
    municipalityTitle_positionX = municipalityFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    municipalityTitle_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    municipality_title.attemptResize(QgsLayoutSize(municipalityTitle_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    municipalityTitle_ItemHeight = generator.calculateHeight(municipality_title)
    municipality_title.attemptResize(QgsLayoutSize(municipalityTitle_ItemWidth, municipalityTitle_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    ## Dynamic Set Up
    municipality_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_width_vq']}) - "
            f"2*to_real({var['custom_frame_line_width_vq']}) - "
            f"to_real({var['custom_item_dist_right_vq']}) - "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    municipality_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            "CalcLabelHeight(@layout_name, 'municipality_title')"
        ),
    )
    
    ### Auftragsbox content ###
    municipality_name = generator.user_inputs.get('auftraggeber')
    municipality_name = municipality_name if municipality_name else "Gemeinde/Stadt\nXXX\nXXX(Adresse)"
    municipality_content = QgsLayoutItemLabel(layout)
    municipality_content.setText(municipality_name)
    municipality_content.setId("municipality_content")
    municipality_content.setFont(QFont(font, font_size))
    municipality_content.setMargin(0)

    ## Static Set Up
    municipalityContent_positionX = municipalityFrame_positionX + float(var["custom_frame_line_width_vq"]/2) + float(var["custom_item_dist_left_vq"])
    municipalityContent_ItemWidth = float(var["custom_frame_width_vq"]) - 2*float(var["custom_frame_line_width_vq"]) - float(var["custom_item_dist_left_vq"]) - float(var["custom_item_dist_right_vq"])
    municipality_content.attemptResize(QgsLayoutSize(municipalityContent_ItemWidth, 0, QgsUnitTypes.LayoutMillimeters))
    municipalityContent_ItemHeight = generator.calculateHeight(municipality_content)
    municipality_content.attemptResize(QgsLayoutSize(municipalityContent_ItemWidth, municipalityContent_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    municipalityFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + municipalityTitle_ItemHeight + var["custom_dist_title_text_vq"] + municipalityContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    municipality_frame.attemptResize(QgsLayoutSize(municipalityFrame_ItemWidth, municipalityFrame_ItemHeight, QgsUnitTypes.LayoutMillimeters))

    municipalityFrame_positionY = projectFrame_positionY - municipalityFrame_ItemHeight
    municipality_frame.attemptMove(QgsLayoutPoint(municipalityFrame_positionX, municipalityFrame_positionY, QgsUnitTypes.LayoutMillimeters))

    municipalityTitle_positionY = municipalityFrame_positionY + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_top_vq"]
    municipality_title.attemptMove(QgsLayoutPoint(municipalityTitle_positionX, municipalityTitle_positionY, QgsUnitTypes.LayoutMillimeters))

    municipalityContent_positionY = municipalityTitle_positionY + municipalityTitle_ItemHeight + float(var["custom_item_dist_top_vq"])
    municipality_content.attemptMove(QgsLayoutPoint(municipalityContent_positionX, municipalityContent_positionY, QgsUnitTypes.LayoutMillimeters))
    
    lf_itemWidth = var["custom_frame_width_vq"]
    lf_itemHeight = municipalityFrame_positionY -lf_positionY  
    legend_frame.attemptResize(QgsLayoutSize(lf_itemWidth, lf_itemHeight, QgsUnitTypes.LayoutMillimeters))

    ## Dynamic Set Up
    municipality_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_width_vq']}) - "
            f"2*to_real({var['custom_frame_line_width_vq']}) - "
            f"to_real({var['custom_item_dist_right_vq']}) - "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    municipality_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            "CalcLabelHeight(@layout_name, 'municipality_content')"
        ),
    )

    municipality_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth, 
        QgsProperty.fromExpression(f"{var['custom_frame_width_vq']}"),
    )

    municipality_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            f"to_real({var['custom_frame_line_width_vq']}) + "
            f"to_real({var['custom_item_dist_top_vq']}) + "
            "GetDynamicItemHeight(@layout_name,'municipality_title') + "
            f"to_real({var['custom_dist_title_text_vq']}) + "
            "GetDynamicItemHeight(@layout_name,'municipality_content') + "
            f"to_real({var['custom_item_dist_bottom_vq']})"
        ),
    )

    municipality_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'municipality_frame')"
        ),
    )

    municipality_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'project_frame') - "
            "GetDynamicItemHeight(@layout_name,'municipality_frame')"
        ),
    )

    municipality_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'municipality_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )

    municipality_title.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'municipality_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_top_vq']})"
        ),
    )

    municipality_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,  
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name,'municipality_frame') + "
            f"to_real({var['custom_frame_line_width_vq']})/2 + "
            f"to_real({var['custom_item_dist_left_vq']})"
        ),
    )
    municipality_content.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'municipality_title') + "
            "GetDynamicItemHeight(@layout_name,'municipality_title') + "
            f"to_real({var['custom_item_dist_top_vq']})"
        ),
    )
    
    legend_frame.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name,'municipality_frame') - "
            "GetDynamicItemPositionY(@layout_name,'legend_frame')"
        ),
    )
    
    
    ########################################################################
    ### North Arrow
    svg_north_arrow_path = os.path.join(os.path.dirname(__file__), "assets", "NorthArrow.svg")
    north_arrow = QgsLayoutItemPicture(layout)
    north_arrow.setId("north_arrow")
    north_arrow.setFrameEnabled(False)
    north_arrow.setPicturePath(svg_north_arrow_path)
    north_arrow.setLinkedMap(map_item)
    north_arrow.setNorthMode(0)
    ## Static Set Up
    northArrow_positionX = (map_itemWidth + var["custom_page_dist_left_vq"]) - var["custom_item_dist_right_vq"] - var["custom_north_arrow_width_vq"]
    northArrow_positionY = map_positionY + var["custom_item_dist_top_vq"] + var["custom_frame_line_width_vq"]/2
    north_arrow.attemptMove(QgsLayoutPoint(northArrow_positionX, northArrow_positionY, QgsUnitTypes.LayoutMillimeters))
    
    northArrow_ItemWidth = var["custom_north_arrow_width_vq"]
    northArrow_ItemHeight = var["custom_north_arrow_height_vq"]
    north_arrow.attemptResize(QgsLayoutSize(northArrow_ItemWidth, northArrow_ItemHeight, QgsUnitTypes.LayoutMillimeters))
    
    ## Dynamic Set Up
    north_arrow.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "(GetDynamicItemWidth(@layout_name, 'map') +"
            f" {var['custom_page_dist_left_vq']}) - "
            f" {var['custom_item_dist_right_vq']} - {var['custom_north_arrow_width_vq']}"
        ),
    )
    north_arrow.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionY(@layout_name, 'map') + "
            f"{var['custom_item_dist_top_vq']} + {var['custom_frame_line_width_vq']/2}"
        ),
    )
    north_arrow.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_north_arrow_width_vq']}")
    )
    north_arrow.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_north_arrow_height_vq']}")
    )
    
    ########################################################################
    ### Scale Bar ###
    custom_scale_segment_length = 100
    scale_bar = QgsLayoutItemScaleBar(layout)
    scale_bar.setId("scale_bar")
    scale_bar.setFrameEnabled(False)
    scale_bar.setStyle("Single Box")
    scale_bar.setBoxContentSpace(0)
    scale_bar.setFont(QFont(font, font_size_metadata))
    scale_bar.setLabelBarSpace(var["custom_scale_label_space_vq"])
    scale_bar.setLinkedMap(map_item)
    scale_bar.setHeight(var["custom_scale_bar_height_vq"])
    scale_bar.setSegmentSizeMode(Qgis.ScaleBarSegmentSizeMode.Fixed)
    scale_bar.setUnits(QgsUnitTypes.DistanceMeters)
    scale_bar.setMapUnitsPerScaleBarUnit(1)
    scale_bar.setUnitsPerSegment(custom_scale_segment_length)  # Wie Lange die Bar sein soll
    scale_bar.setNumberOfSegments(3)
    scale_bar.setNumberOfSegmentsLeft(0)
    scale_bar.setUnitLabel("m")
    scale_bar.setReferencePoint(QgsLayoutItem.LowerLeft)
    
    ## Static Set Up
    scaleBar_positionX = map_positionX + var["custom_frame_line_width_vq"]/2 + var["custom_item_dist_left_vq"] - 0.4
    scaleBar_positionY = map_positionY + map_itemHeight - float(var["custom_item_dist_bottom_vq"]) + 0.55
    scale_bar.attemptMove(QgsLayoutPoint(scaleBar_positionX, scaleBar_positionY, QgsUnitTypes.LayoutMillimeters))
    
    scaleBar_ItemWidth = scale_bar.sizeWithUnits().width()
    scaleBar_ItemHeight = var["custom_scale_bar_height_vq"] + var["custom_scale_label_space_vq"] + int(font_size_metadata)*0.352778
    scale_bar.attemptResize(QgsLayoutSize(scaleBar_ItemWidth, scaleBar_ItemHeight, QgsUnitTypes.LayoutMillimeters))
    
    ## Dynamic Set Up
    scale_bar.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionX,
        QgsProperty.fromExpression(
            "GetDynamicItemPositionX(@layout_name, 'map') + "
            f"{var['custom_frame_line_width_vq']/2 + var['custom_item_dist_left_vq'] - 0.4}"
        ),
    )
    scale_bar.dataDefinedProperties().setProperty(
        QgsLayoutObject.PositionY,
        QgsProperty.fromExpression(
            "(GetDynamicItemPositionY(@layout_name, 'map') "
            "+ GetDynamicItemHeight(@layout_name, 'map')) - "
            f"to_real({var['custom_item_dist_bottom_vq']}) + 0.55"
        ),
    )
    scale_bar.dataDefinedProperties().setProperty(
        QgsLayoutObject.ItemHeight,
        QgsProperty.fromExpression(
            f"to_real({var['custom_scale_bar_height_vq']}) + to_real({var['custom_scale_label_space_vq']}) + {int(font_size_metadata)}*0.352778"
        ),
    )
    
    #########################################################################
    ### Add all items to the layout
    
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
    
    layout.addLayoutItem(project_frame)
    layout.addLayoutItem(project_title) 
    layout.addLayoutItem(project_content)

    layout.addLayoutItem(municipality_frame)
    layout.addLayoutItem(municipality_title)
    layout.addLayoutItem(municipality_content)
    
    layout.addLayoutItem(north_arrow)
    
    layout.addLayoutItem(scale_bar)

    return layout