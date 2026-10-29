def test_layout_designer(generator):
    var = generator.variables
    layout_name = "Test Layout"
    generator._remove_existing_layouts(layout_name)
    designer = LayoutDesigner(generator.project, layout_name, var, generator.user_inputs)
    generator.manager.addLayout(designer.layout)
    
    page = designer.layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(var["custom_page_size_width_vq"], var["custom_page_size_height_vq"], QgsUnitTypes.LayoutMillimeters))
    page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width_vq']}"))
    page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_page_size_height_vq']}"))
    
    ## Map
    map_id = 'map'
    map_item = designer.add_item(MapItem(map_id, target_layer= generator.user_inputs.get("target_layer"), stroke_width=0.3))
    
    map_positionX = var["custom_frame_line_width_vq"]/2 + var["custom_page_dist_left_vq"]
    map_positionY = var["custom_frame_line_width_vq"]/2 + var["custom_page_dist_top_vq"]
    map_item.setPosition(x=map_positionX, y=map_positionY)
    
    map_itemHeight = var["custom_page_size_height_vq"] - var["custom_page_dist_top_vq"] - var["custom_frame_line_width_vq"] - var["custom_page_dist_bottom_vq"]  
    map_item.setSize(height=map_itemHeight)
    map_item.set_dynamic({
        QgsLayoutObject.PositionX: f"{map_positionX}",
        QgsLayoutObject.PositionY: f"{map_positionY}",
        QgsLayoutObject.ItemHeight: f"{map_itemHeight}"
    })
    
    
    ## Legend
    legend_id = 'legend'
    Legend = designer.add_item(LegendBox(legend_id, map_item.qgs_item, generator.user_inputs.get("selected_layers"), generator.project, var))
    
    
    lf_positionX = var["custom_page_size_width_vq"] - var["custom_page_dist_left_vq"] - var["custom_frame_width_vq"] - var["custom_frame_line_width_vq"]
    lf_positionY = var["custom_page_dist_top_vq"] + var["custom_frame_line_width_vq"]/2
    lf_itemWidth = var["custom_frame_width_vq"]
    
    
    ##Metatdata
    metadata_id = 'metadata'
    Metadata = designer.add_item(MetadataBox(metadata_id, var, generator.user_inputs))
    
    metaF_PositionX = lf_positionX
    metaF_ItemWidth = var["custom_frame_width_vq"]
    metadata_itemHeight = generator.calculateHeight(Metadata.children.get("metadata").qgs_item)
    
    metaF_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + metadata_itemHeight + var["custom_item_dist_bottom_vq"]
    metaF_PositionY = var["custom_page_size_height_vq"] - var["custom_frame_line_width_vq"] - var["custom_page_dist_bottom_vq"] - metaF_ItemHeight
    Metadata.set_static(metaF_PositionX,metaF_PositionY,metaF_ItemWidth, metaF_ItemHeight, metadata_itemHeight)
    
    
    
    
    map_itemWidth = lf_positionX - var["custom_item_dist_left_vq"] - var["custom_frame_line_width_vq"] - map_positionX
    map_item.setSize(width=map_itemWidth)
    expr_map_width = (
        f"GetDynamicItemPositionX(@layout_name, 'legend_frame') - "
        f"{var['custom_item_dist_left_vq']} - "
        f"{var['custom_frame_line_width_vq']} - "
        f"GetDynamicItemPositionX(@layout_name, 'map')"
    )
    map_item.set_dynamic({
        QgsLayoutObject.ItemWidth: expr_map_width
    })
    
    
    ##Spie Box
    # 1. Add to the designer
    spie_box = designer.add_item(SpieBox("spie", var))

    # 2. Calculate the height of the Title and Content (using your calculation function)
    spie_title_h = generator.calculateHeight(spie_box.children["title"].qgs_item)
    spie_content_h = generator.calculateHeight(spie_box.children["content"].qgs_item)

    logo_h = 8.0

    # Calculate the total height of the Frame based on the inner content
    max_content_h = max((logo_h + 1.776), spie_content_h)
    frame_h = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + spie_title_h + var["custom_dist_title_text_vq"] + max_content_h + var["custom_item_dist_bottom_vq"]

    # 3. Assign static coordinates (Spie is located above Metadata, so Spie_Y = Metadata_Y - Spie_Height)
    # Since the set_static function above returns the frame height, you calculate Y as follows:
    spieFrame_positionY = metaF_PositionY - frame_h
    spie_box.set_static(lf_positionX, spieFrame_positionY, var["custom_frame_width_vq"], spie_title_h, spie_content_h)

    # 4. Gán Dynamic
    spie_box.set_dynamic(spie_box.get_dynamic_dict())
    
    ##Plan Content
    plan_text = generator.user_inputs.get('planinhalt')
    planinhalt_content = plan_text if plan_text else "XXX"
    plan_box = designer.add_item(GenericBox("plan_content", "Planinhalt", planinhalt_content, var))
    planContentFrame_positionX = lf_positionX
    planContentFrame_ItemWidth = var['custom_frame_width_vq']
    
    planContentTitle_ItemHeight = generator.calculateHeight(plan_box.children["title"].qgs_item)
    planContent_ItemHeight = generator.calculateHeight(plan_box.children["content"].qgs_item)

    planContentFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + planContentTitle_ItemHeight + var["custom_dist_title_text_vq"] + planContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    planContentFrame_positionY = spieFrame_positionY - planContentFrame_ItemHeight
    
    plan_box.set_static(planContentFrame_positionX, planContentFrame_positionY, planContentFrame_ItemWidth, planContentFrame_ItemHeight, planContentTitle_ItemHeight, planContent_ItemHeight)
    
    ##Project
    project_text = generator.user_inputs.get('title')
    projekt_content = project_text if project_text else "XXX"
    project_box = designer.add_item(GenericBox("project", "Projekt", projekt_content, var))
    projectFrame_positionX = lf_positionX
    projectFrame_ItemWidth = var['custom_frame_width_vq']
    
    projectTitle_ItemHeight = generator.calculateHeight(project_box.children["title"].qgs_item)
    projectContent_ItemHeight = generator.calculateHeight(project_box.children["content"].qgs_item)

    projectFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + projectTitle_ItemHeight + var["custom_dist_title_text_vq"] + projectContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    projectFrame_positionY = planContentFrame_positionY - projectFrame_ItemHeight
    
    project_box.set_static(projectFrame_positionX, projectFrame_positionY, projectFrame_ItemWidth, projectFrame_ItemHeight, projectTitle_ItemHeight, projectContent_ItemHeight)
    ##Auftragbox
    municipality_text = generator.user_inputs.get('auftraggeber')
    municipality_content = municipality_text if municipality_text else "XXX"
    municipality_box = designer.add_item(GenericBox("municipality", "Auftraggeber", municipality_content, var))
    municipalityFrame_positionX = lf_positionX
    municipalityFrame_ItemWidth = var['custom_frame_width_vq']
    
    municipalityTitle_ItemHeight = generator.calculateHeight(municipality_box.children["title"].qgs_item)
    municipalityContent_ItemHeight = generator.calculateHeight(municipality_box.children["content"].qgs_item)

    municipalityFrame_ItemHeight = var["custom_frame_line_width_vq"] + var["custom_item_dist_top_vq"] + municipalityTitle_ItemHeight + var["custom_dist_title_text_vq"] + municipalityContent_ItemHeight + var["custom_item_dist_bottom_vq"]
    municipalityFrame_positionY = projectFrame_positionY - municipalityFrame_ItemHeight
    
    municipality_box.set_static(municipalityFrame_positionX, municipalityFrame_positionY, municipalityFrame_ItemWidth, municipalityFrame_ItemHeight, municipalityTitle_ItemHeight, municipalityContent_ItemHeight)
    
    
    lf_itemHeight =  municipalityFrame_positionY -lf_positionY 
    Legend.set_static(lf_positionX, lf_positionY, lf_itemWidth, lf_itemHeight, title_h=generator.calculateHeight(Legend.children.get("title").qgs_item))
    
    
    return designer.build()