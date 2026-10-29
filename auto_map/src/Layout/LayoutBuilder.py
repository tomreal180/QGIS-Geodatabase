from matplotlib import legend

from ..LayoutDesigner import LayoutDesigner
from ..Layout_Builder.basic_items import *
from ..Layout_Builder.composer import *

from qgis.core import *

class WidthObserver:
    def __init__(self, generator, var):
        self.generator = generator
        self.var = var
        self.best_title_width = 0
        self.best_content_width = 0

    def check_width(self, item):
        title_itemWidth = self.generator.calculateWidth(item.children.get("title").qgs_item)
        content_itemWidth = self.generator.calculateWidth(item.children.get("content").qgs_item)
        if title_itemWidth > self.best_title_width:
            self.best_title_width = title_itemWidth
        if content_itemWidth > self.best_content_width:
            self.best_content_width = content_itemWidth
        
        best_full_width = self.var["custom_frame_line_width"]*2  + self.var["custom_item_dist_left"] + self.best_title_width + self.var["custom_dist_title_text_small"] + self.best_content_width +self.var["custom_item_dist_right"] 
            
        return self.best_title_width, self.best_content_width, best_full_width
    def check_title_width(self, item):
        title_itemWidth = self.generator.calculateWidth(item.children.get("title").qgs_item)
        if title_itemWidth > self.best_title_width:
            self.best_title_width = title_itemWidth
        return self.best_title_width
    def check_content_width(self, item):
        content_itemWidth = self.generator.calculateWidth(item.children.get("content").qgs_item)
        if content_itemWidth > self.best_content_width:
            self.best_content_width = content_itemWidth
        return self.best_content_width
    
    def get_best_widths(self):
        best_full_width = self.var["custom_frame_line_width"]*2  + self.var["custom_item_dist_left"] + self.best_title_width + self.var["custom_dist_title_text_small"] + self.best_content_width +self.var["custom_item_dist_right"] 
        return best_full_width
    
def build_layout(generator):
    ## Initialization
    var = generator.variables
    layout_name = f"{generator.user_inputs.get('layout_name')} ({generator.variables['custom_format']})" if generator.user_inputs.get('layout_name') else f"{generator.variables['custom_format']} Layout"
    generator._remove_existing_layouts(layout_name)
    designer = LayoutDesigner(generator.project,layout_name, var, generator.user_inputs)
    generator.manager.addLayout(designer.layout)
    
    ########################################################################################################################################################################    
    ##Page Setup
    page = designer.layout.pageCollection().page(0)
    page.setPageSize(QgsLayoutSize(var["custom_page_size_width"], var["custom_page_size_height"], QgsUnitTypes.LayoutMillimeters))
    page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemWidth, QgsProperty.fromExpression(f"{var['custom_page_size_width']}"))
    page.dataDefinedProperties().setProperty(QgsLayoutObject.ItemHeight, QgsProperty.fromExpression(f"{var['custom_page_size_height']}"))
    
    ########################################################################################################################################################################    
    ## Map Setup
    map_id = 'map'
    map_item = designer.add_item(MapItem(map_id, target_layer= generator.user_inputs.get("target_layer"), stroke_width=0.3))
    selected_layers = generator.user_inputs.get("selected_layers")
    qgs_map = map_item.qgs_item
    actual_layers = []
    for layer_name in selected_layers:
        layers_found = QgsProject.instance().mapLayersByName(layer_name)
        if layers_found:
            actual_layers.append(layers_found[0])
    hintergrund_layers = generator.user_inputs.get("hintergrund_layers")
    for layer_name in hintergrund_layers:
        layers_found = QgsProject.instance().mapLayersByName(layer_name)
        if layers_found:
            actual_layers.append(layers_found[0])
    
    vegetation_layers = generator.user_inputs.get("vegetation_layers") 
    for layer_name in vegetation_layers:
        layers_found = QgsProject.instance().mapLayersByName(layer_name)
        if layers_found:
            actual_layers.append(layers_found[0])
            
    qgs_map.setLayers(actual_layers)
    qgs_map.setKeepLayerSet(True)
    
    map_positionX = var["custom_frame_line_width"]/2 + var["custom_page_dist_left"]
    map_positionY = var["custom_frame_line_width"]/2 + var["custom_page_dist_top"]
    map_item.setPosition(x=map_positionX, y=map_positionY)
    
    map_itemWidth = var["custom_page_size_width"] - var["custom_page_dist_left"] - var["custom_frame_line_width"] - var["custom_page_dist_right"]

    # map_itemHeight = 257
    map_item.set_dynamic({
        QgsLayoutObject.PositionX: f"{map_positionX}",
        QgsLayoutObject.PositionY: f"{map_positionY}",
        QgsLayoutObject.ItemWidth: f"{map_itemWidth}"
        # QgsLayoutObject.ItemHeight: f"{map_itemHeight}"
    })
    
    ########################################################################################################################################################################    
    # ---------------- INITIALIZE THE BOXES ----------------
    width_observer_11 = WidthObserver(generator, var)
    
    sheet_id = 'sheet'
    sheet_content = "[% coalesce(@atlas_featurenumber, 1) %] von [% coalesce(@atlas_totalfeatures, 1) %]"
    sheet_box = designer.add_item(SmallBox(sheet_id, title_text="Blatt", content_text=sheet_content, var=var))
    
    date_id = 'date'
    date = generator.user_inputs.get("date") if generator.user_inputs.get("date") else "01.01.2024"
    date_box = designer.add_item(SmallBox(date_id, title_text="Erstellt", content_text=date, var=var))
    
    stand_id = 'stand'
    stand = generator.user_inputs.get("stand") if generator.user_inputs.get("stand") else "Monat-Jahr"
    stand_box = designer.add_item(SmallBox(stand_id, title_text="Stand", content_text=stand, var=var))
    
    zoom_id = 'zoom'
    dynamic_scale_text = f"1: [% round(map_get(item_variables('{map_id}'), 'map_scale')) %]"
    zoom_box = designer.add_item(SmallBox(zoom_id, title_text="Maßstab", content_text=dynamic_scale_text, var=var))
    
    format_id = 'format'
    format_box = designer.add_item(SmallBox(format_id, title_text="Format", content_text=var["custom_format"], var=var))

    # --- STATIC CALCULATION (STATIC) ---
    sf_itemHeight = var["custom_frame_height"] / 5  # Or some fixed height
    
    for box in [date_box, stand_box, format_box]:
        content11_itemWidth = width_observer_11.check_content_width(box)
    # Measure statically to draw the first time
    for box in [sheet_box, date_box, stand_box, format_box, zoom_box]:
        title11_itemWidth = width_observer_11.check_title_width(box)
        sf_itemWidth = width_observer_11.get_best_widths()
    
    sf_positionX = map_positionX + map_itemWidth - sf_itemWidth
    sf_positionY = var["custom_page_size_height"] - var["custom_page_dist_bottom"] - var["custom_frame_line_width"] - sf_itemHeight
    df_positionY = sf_positionY - sf_itemHeight
    stf_positionY = df_positionY - sf_itemHeight
    zf_positionY = stf_positionY - sf_itemHeight
    ff_positionY = zf_positionY - sf_itemHeight
    map_itemHeight = ff_positionY- map_positionY
    map_item.setSize(width=map_itemWidth, height=map_itemHeight)

    sheet_box.set_static(sf_positionX, sf_positionY, sf_itemWidth, sf_itemHeight, title11_itemWidth, content11_itemWidth)
    date_box.set_static(sf_positionX, df_positionY, sf_itemWidth, sf_itemHeight, title11_itemWidth, content11_itemWidth)
    stand_box.set_static(sf_positionX, stf_positionY, sf_itemWidth, sf_itemHeight, title11_itemWidth, content11_itemWidth)    
    zoom_box.set_static(sf_positionX, zf_positionY, sf_itemWidth, sf_itemHeight, title11_itemWidth, content11_itemWidth)
    format_box.set_static(sf_positionX, ff_positionY, sf_itemWidth, sf_itemHeight, title11_itemWidth, content11_itemWidth)

    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------

    # 1. Find the maximum width of Title and Content using the max() function of QGIS
    expr_max_title_w = (
        "max(CalcLabelWidth(@layout_name, 'sheet_title'), CalcLabelWidth(@layout_name, 'date_title'), CalcLabelWidth(@layout_name, 'stand_title'), CalcLabelWidth(@layout_name, 'zoom_title'), CalcLabelWidth(@layout_name, 'format_title'))"
    )
    
    expr_max_content_w = (
        "max(CalcLabelWidth(@layout_name, 'date_content'), "
        "CalcLabelWidth(@layout_name, 'stand_content'), CalcLabelWidth(@layout_name, 'format_content'))"
    )

    # 2. The width of the ENTIRE FRAME follows the two max() values above
    expr_frame_w = (
        f"{var['custom_frame_line_width']}*2 + {var['custom_item_dist_left']} + "
        f"({expr_max_title_w}) + {var['custom_dist_title_text_small']} + ({expr_max_content_w}) + {var['custom_item_dist_right']}"
    )

    # 3. X position of the frame (always aligned to the right edge of the Map)
    expr_frame_x = f"GetDynamicItemPositionX(@layout_name, 'map') + GetDynamicItemWidth(@layout_name, 'map') - ({expr_frame_w})"

    # 4. Set dynamic expressions for the text inside the boxes
    for box in [sheet_box, date_box, stand_box, zoom_box, format_box]:
        box.set_dynamic(expr_max_title_w=expr_max_title_w, expr_max_content_w=expr_max_content_w)

    # 5. Define dynamic positions for the frames (Bottom-Up)
    
    # Box in bottom(sheet_box)
    sheet_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.ItemWidth: expr_frame_w,
        QgsLayoutObject.ItemHeight: f"{sf_itemHeight}",
        QgsLayoutObject.PositionX: expr_frame_x,
        QgsLayoutObject.PositionY: f"{var['custom_page_size_height']} - {var['custom_page_dist_bottom']} - {var['custom_frame_line_width']} - {sf_itemHeight}"
    })
    
    date_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.ItemWidth: expr_frame_w,
        QgsLayoutObject.ItemHeight: f"{sf_itemHeight}",
        QgsLayoutObject.PositionX: expr_frame_x,
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, 'sheet_frame') - {sf_itemHeight}"
    })
    stand_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.ItemWidth: expr_frame_w,
        QgsLayoutObject.ItemHeight: f"{sf_itemHeight}",
        QgsLayoutObject.PositionX: expr_frame_x,
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, 'date_frame') - {sf_itemHeight}"
    })
    zoom_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.ItemWidth: expr_frame_w,
        QgsLayoutObject.ItemHeight: f"{sf_itemHeight}",
        QgsLayoutObject.PositionX: expr_frame_x,
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, 'stand_frame') - {sf_itemHeight}"
    })
    format_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.ItemWidth: expr_frame_w,
        QgsLayoutObject.ItemHeight: f"{sf_itemHeight}",
        QgsLayoutObject.PositionX: expr_frame_x,
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, 'zoom_frame') - {sf_itemHeight}"
    })

    map_item.set_dynamic({
        QgsLayoutObject.ItemHeight: ("GetDynamicItemPositionY(@layout_name, 'format_frame') - "
                                    "GetDynamicItemPositionY(@layout_name, 'map')"
                                    )
    })
    ########################################################################################################################################################################    
    # Column 10
    # ---------------- INITIALIZE THE BOXES ----------------
    width_observer_10 = WidthObserver(generator, var)
    ## Überprüfer
    checker_id = 'checker'
    checker = generator.user_inputs.get("prüfer") if generator.user_inputs.get("prüfer") else "Max Mustermann"
    checker_box = designer.add_item(SmallBox(checker_id, title_text="geprüft:", content_text=checker, var=var))
    
    
    ##Planverfasser
    planer_id = 'planer'
    planer = generator.user_inputs.get("planverfasser") if generator.user_inputs.get("planverfasser") else "Max Mustermann"
    planer_box = designer.add_item(SmallBox(planer_id, title_text="Planverfasser:", content_text=planer, var=var))
    
    ##Auftraggerber
    muni_id = 'auftraggeber'
    auftraggeber_logo_path = generator.user_inputs.get("auftraggeber_logo")
    ag_logo_path = auftraggeber_logo_path if auftraggeber_logo_path else os.path.join(os.path.dirname(__file__), "assets", "SPIE.jpg")
    # ag_logo_path = "SPIE.svg"
    auftraggeber = generator.user_inputs.get("auftraggeber")
    ag_name = auftraggeber if auftraggeber else "SPIE WirliebenKabel GmbH"
    auftraggeber_adresse = generator.user_inputs.get("auftraggeber_adresse")
    ag_adresse = auftraggeber_adresse if auftraggeber_adresse else "Hohe Straße 125a\n07937 Zeulenroda-Triebes"
    muni_box = designer.add_item(CompanyBox(muni_id, var, title="Auftraggeber", logo=ag_logo_path, name=ag_name, adresse=ag_adresse))
        
    # --- STATIC CALCULATION (STATIC) ---
    cf_itemHeight = var["custom_frame_height"]/5
    
    cf_positionY = sf_positionY
    pf_positionY = cf_positionY - cf_itemHeight
    
    for box in [checker_box, planer_box]:
        title10_itemWidth, content10_itemWidth, cf_itemWidth = width_observer_10.check_width(box)
    cf_positionX = sf_positionX- cf_itemWidth
    
    
    mf_itemHeight = pf_positionY - ff_positionY
    mf_positionY = pf_positionY - mf_itemHeight
    mf_itemWidth = cf_itemWidth
    mf_contentitemWidth = mf_itemWidth - var["custom_item_dist_left"] - var["custom_item_dist_right"]- 2*var["custom_frame_line_width"]
    
    ct_height = generator.calculateHeight(muni_box.children.get("title").qgs_item,target_width_mm=mf_contentitemWidth)
    cn_height = generator.calculateHeight(muni_box.children.get("name").qgs_item,target_width_mm=mf_contentitemWidth)
    ca_height = generator.calculateHeight(muni_box.children.get("adresse").qgs_item,target_width_mm=mf_contentitemWidth)

    checker_box.set_static(cf_positionX, cf_positionY, cf_itemWidth, cf_itemHeight,title_ItemWidth=title10_itemWidth, content_ItemWidth=content10_itemWidth)
    planer_box.set_static(cf_positionX, pf_positionY, cf_itemWidth, cf_itemHeight,title_ItemWidth=title10_itemWidth, content_ItemWidth=content10_itemWidth)
    muni_box.set_static(cf_positionX, mf_positionY, cf_itemWidth, mf_itemHeight, title_h = ct_height, name_h = cn_height, adresse_h = ca_height, logo_h=4)
    
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    expr_max_title_w_2 = (
        "max(CalcLabelWidth(@layout_name, 'checker_title'), CalcLabelWidth(@layout_name, 'planer_title'))"
    )
    
    expr_max_content_w_2 = (
        "max(CalcLabelWidth(@layout_name, 'checker_content'), CalcLabelWidth(@layout_name, 'planer_content'))"
    )
    
    expr_frame_w_2 = (
        f"{var['custom_frame_line_width']}*2 + {var['custom_item_dist_left']} + "
        f"({expr_max_title_w_2}) + {var['custom_dist_title_text_small']} + ({expr_max_content_w_2}) + {var['custom_item_dist_right']}"
    )
    
    for box in [checker_box, planer_box]:
        box.set_dynamic(expr_max_title_w=expr_max_title_w_2, expr_max_content_w=expr_max_content_w_2)
    muni_box.set_dynamic()
    
    # Define dynamic positions for the frames (Bottom-Up)
    checker_box.set_dynamic_by_id("frame",{
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, 'sheet_frame') - getDynamicItemWidth(@layout_name, 'checker_frame')",
        QgsLayoutObject.PositionY: "GetDynamicItemPositionY(@layout_name, 'sheet_frame')",
        QgsLayoutObject.ItemWidth: f"{expr_frame_w_2}",
        QgsLayoutObject.ItemHeight: f"{var['custom_frame_height']/5}"
    })
    
    planer_box.set_dynamic_by_id("frame",{
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, 'sheet_frame') - getDynamicItemWidth(@layout_name, 'planer_frame')",
        QgsLayoutObject.PositionY: "GetDynamicItemPositionY(@layout_name, 'checker_frame') - GetDynamicItemHeight(@layout_name, 'checker_frame')",
        QgsLayoutObject.ItemWidth: f"{expr_frame_w_2}",
        QgsLayoutObject.ItemHeight: f"{var['custom_frame_height']/5}"
    })
    
    muni_box.set_dynamic_by_id("frame",{
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, 'checker_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, 'planer_frame') - GetDynamicItemHeight(@layout_name, '{muni_id}_frame')",
        QgsLayoutObject.ItemWidth: f"{expr_frame_w_2}",
        QgsLayoutObject.ItemHeight: f"GetDynamicItemPositionY(@layout_name, '{planer_id}_frame') - GetDynamicItemPositionY(@layout_name, '{format_id}_frame')"
    })
    
    ########################################################################################################################################################################    
    #Column 9
    # ---------------- INITIALIZE THE BOXES ----------------
    width_observer_9 = WidthObserver(generator, var)
    ##Vertragsnummer
    vertragsnummer_id = 'vertragsnummer'
    vertragsnummer = generator.user_inputs.get("vertragsnummer")
    vertragsnummer = vertragsnummer if vertragsnummer else "XXX"
    vertragsnummer_box = designer.add_item(SmallBox(vertragsnummer_id, title_text="Vertragsnummer:", content_text=vertragsnummer, var=var))
    
    ##Spie 
    spie_id = 'spie'
    spie_logo_path = os.path.join(os.path.dirname(__file__), "assets", "SPIE.jpg")
    spie_name = "SPIE WirliebenKabel GmbH"
    spie_adresse = "Hohe Straße 125a\n07937 Zeulenroda-Triebes"
    spie_box = designer.add_item(CompanyBox(spie_id, var, title="Planungsbüro", logo=spie_logo_path, name=spie_name, adresse=spie_adresse))
    
    # --- STATIC CALCULATION (STATIC) ---
    vnf_positionY = sf_positionY
    vnf_itemHeight = var["custom_frame_height"]/5
    title9_itemWidth, content9_itemWidth, vnf_itemWidth = width_observer_9.check_width(vertragsnummer_box)

    spie_itemHeight = vnf_positionY - ff_positionY
    spie_positionY = vnf_positionY - spie_itemHeight
    spie_itemWidth = vnf_itemWidth
    spie_contentitemWidth = spie_itemWidth - var["custom_item_dist_left"] - var["custom_item_dist_right"]- 2*var["custom_frame_line_width"]
    spie_ct_height = generator.calculateHeight(spie_box.children.get("title").qgs_item,target_width_mm=spie_contentitemWidth)
    spie_cn_height = generator.calculateHeight(spie_box.children.get("name").qgs_item,target_width_mm=spie_contentitemWidth)
    spie_ca_height = generator.calculateHeight(spie_box.children.get("adresse").qgs_item,target_width_mm=spie_contentitemWidth)
    
    vnf_positionX = cf_positionX- vnf_itemWidth
    vertragsnummer_box.set_static(vnf_positionX, vnf_positionY, vnf_itemWidth, vnf_itemHeight,title_ItemWidth=title9_itemWidth, content_ItemWidth=content9_itemWidth)
    spie_box.set_static(vnf_positionX, spie_positionY, spie_itemWidth, spie_itemHeight, title_h = spie_ct_height, name_h = spie_cn_height, adresse_h = spie_ca_height)
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    for box in [vertragsnummer_box, spie_box]:
        box.set_dynamic()
    
    # Define dynamic positions for the frames (Bottom-Up)
    expr_frame_w_vertragnummer = (
        f"{var['custom_frame_line_width']}*2 + {var['custom_item_dist_left']} + "
        f"CalcLabelWidth(@layout_name,'{vertragsnummer_id}_title') + {var['custom_dist_title_text_small']} + (CalcLabelWidth(@layout_name,'{vertragsnummer_id}_content')) + {var['custom_item_dist_right']}"
    )
    vertragsnummer_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, 'checker_frame') - getDynamicItemWidth(@layout_name, '{vertragsnummer_id}_frame')",
        QgsLayoutObject.PositionY: "GetDynamicItemPositionY(@layout_name, 'sheet_frame')",
        QgsLayoutObject.ItemWidth: f"{expr_frame_w_vertragnummer}",
        QgsLayoutObject.ItemHeight: f"{var['custom_frame_height']/5}"
    })
    
    spie_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{vertragsnummer_id}_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{vertragsnummer_id}_frame') - getDynamicItemHeight(@layout_name, '{spie_id}_frame')",
        QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{vertragsnummer_id}_frame')",
        QgsLayoutObject.ItemHeight: f"GetDynamicItemPositionY(@layout_name, '{vertragsnummer_id}_frame') - GetDynamicItemPositionY(@layout_name, '{format_id}_frame')"
    })
    ########################################################################################################################################################################    
    ##Column 8
    # ---------------- INITIALIZE THE BOXES ----------------
    #North Arrow
    north_arrow_id = 'north_arrow'
    north_arrow_box = designer.add_item(NorthArrowBox(north_arrow_id, var))
    north_arrow_box.children["north_arrow"].qgs_item.setLinkedMap(qgs_map)
    # --- STATIC CALCULATION (STATIC) ---
    north_arrow_box.set_static(neighbor_x = vnf_positionX, y = spie_positionY, height = var["custom_frame_height"])
    na_positionX, na_positionY, na_itemWidth, na_itemHeight = north_arrow_box.get_FrameParameter()
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    north_arrow_box.set_dynamic(neighbor=vertragsnummer_id)
    # Define dynamic positions for the frames (Bottom-Up)
    north_arrow_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{vertragsnummer_id}_frame') - GetDynamicItemWidth(@layout_name, '{north_arrow_id}_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{spie_id}_frame')",
        QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{north_arrow_id}_north_arrow')+ {2*var["custom_frame_line_width"] + var["custom_item_dist_left"] + var["custom_item_dist_right"]}",
        QgsLayoutObject.ItemHeight: f"{var["custom_frame_height"]}"
    })
    ########################################################################################################################################################################  
    ##Column 7
    ##Project 
    project_id = 'project'
    project_text = generator.user_inputs.get("title")
    project_text = project_text if project_text else "xxx"#"FTTB/H Ausbau FIBER\nGenehmigungsplanung\nPolygon 80.2b\nTrassierungsplan"
    project_box = designer.add_item(GenericBox(project_id, content_text=project_text, var=var, font_size=7))
    project_itemHeight = na_itemHeight
    project_positionY = na_positionY
    project_ct_width = generator.calculateWidth(project_box.children.get("content").qgs_item)
    project_ct_height = generator.calculateHeight(project_box.children.get("content").qgs_item,target_width_mm=project_ct_width)
    
    project_box.set_static(na_positionX, project_positionY, project_itemHeight, content_w=project_ct_width, content_h=project_ct_height)
    project_positionX, project_positionY, project_itemWidth, project_itemHeight = project_box.get_FrameParameter()
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    project_box.set_dynamic()
    # Define dynamic positions for the frames (Bottom-Up)
    project_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{north_arrow_id}_frame')- GetDynamicItemWidth(@layout_name,'{project_id}_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{north_arrow_id}_frame')",
        QgsLayoutObject.ItemWidth: f"getDynamicItemWidth(@layout_name,'{project_id}_content')+{ var["custom_frame_line_width"]*2+var["custom_item_dist_left"]+var["custom_item_dist_right"]}",
        QgsLayoutObject.ItemHeight: f"{var['custom_frame_height']}"
    })
    ########################################################################################################################################################################  
    ##Column 6
    ##Abschnitt
    part_id = 'part'
    abschnitt_user_input = generator.user_inputs.get("abschnitt")
    part_text = f"Abschnitt:\n{abschnitt_user_input if abschnitt_user_input else '##################'}"
    part_box = designer.add_item(GenericBox(part_id, content_text=part_text, var=var, font_size=10, middle=True))
    part_itemHeight = project_itemHeight
    part_positionY = project_positionY
    part_ct_width = generator.calculateWidth(part_box.children.get("content").qgs_item)
    part_ct_height = generator.calculateHeight(part_box.children.get("content").qgs_item,target_width_mm=part_ct_width)
    if len(generator.user_inputs.get("selected_layers")) == 1:
        item_dist = var["item_dist_1"]
    elif len(generator.user_inputs.get("selected_layers")) == 2:
        item_dist = var["item_dist_2"]
    else:
        item_dist = var["item_dist"]
    part_box.set_static(project_positionX, part_positionY, part_itemHeight, content_w=part_ct_width, content_h=part_ct_height, item_dist=item_dist)
    part_positionX, part_positionY, part_itemWidth, part_itemHeight = part_box.get_FrameParameter()
    
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    part_box.set_dynamic(item_dist=item_dist)
    # Define dynamic positions for the frames (Bottom-Up)
    part_box.set_dynamic_by_id("frame", {
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{project_id}_frame')- GetDynamicItemWidth(@layout_name,'{part_id}_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{project_id}_frame')",
        QgsLayoutObject.ItemWidth: f"getDynamicItemWidth(@layout_name,'{part_id}_content')+{ var["custom_frame_line_width"]*2+2*item_dist}",
        QgsLayoutObject.ItemHeight: f"{var['custom_frame_height']}"
    })
    ########################################################################################################################################################################  
    ##Column 5
    ##Beschreibung
    vegetation_names = None
    if  len(vegetation_layers) != 0:
        vegetation_names = vegetation_layers
    street_desc = generator.user_inputs.get("beschriftungen")
    # street_desc = "60 x 30 cm (Überdeckung x Grabenbreite)\n15 m (Abschnittslänge)\noffen (Bauweise)"
    # vegetation_names = ['Grünanlagen']
    meta_neighbor_id = part_id
    meta_neighbor_positionX = part_positionX
    if street_desc or vegetation_names:
        description_id = 'description'
        meta_neighbor_id = description_id
        description_box = designer.add_item(DescriptionBox(description_id, street_desc=street_desc, linked_map= map_item.qgs_item, vegetation_names=vegetation_names, project=generator.project, var=var))
        desc_positionY = part_positionY
        desc_itemHeight = part_itemHeight
        if description_box.has_street:    
            desc_title_w = generator.calculateWidth(description_box.children.get("street_title").qgs_item)
            desc_title_h = generator.calculateHeight(description_box.children.get("street_title").qgs_item,target_width_mm=desc_title_w)
            desc_content_w = generator.calculateWidth(description_box.children.get("street_content").qgs_item)
            desc_content_h = generator.calculateHeight(description_box.children.get("street_content").qgs_item,target_width_mm=desc_content_w)
            description_box.set_static(part_positionX, desc_positionY, desc_itemHeight, title_w=desc_title_w, title_h=desc_title_h, content_street_w=desc_content_w, content_street_h=desc_content_h)
            
            description_box.set_dynamic_by_id("frame",{
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{part_id}_frame') - GetDynamicItemWidth(@layout_name, '{description_id}_frame')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{part_id}_frame')",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{description_id}_street_title') + {var['custom_frame_line_width']*2 + var['custom_item_dist_left'] + var['custom_item_dist_right']}",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{part_id}_frame')"
            })
        elif description_box.has_veg:
            desc_title_w = generator.calculateWidth(description_box.children.get("vegetation_title").qgs_item)
            desc_title_h = generator.calculateHeight(description_box.children.get("vegetation_title").qgs_item,target_width_mm=desc_title_w)
            description_box.set_static(part_positionX, desc_positionY, desc_itemHeight, title_w=desc_title_w, title_h=desc_title_h)
            description_box.set_dynamic_by_id("frame",{
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{part_id}_frame') - GetDynamicItemWidth(@layout_name, '{description_id}_frame')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{part_id}_frame')",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{description_id}_vegetation_title') + {var['custom_frame_line_width']*2 + var['custom_item_dist_left'] + var['custom_item_dist_right']}",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{part_id}_frame')"
            })
        desc_positionX, desc_positionY, desc_itemWidth, desc_itemHeight = description_box.get_FrameParameter()
        # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
        description_box.set_dynamic()
        # Define dynamic positions for the frames (Bottom-Up)
        meta_neighbor_positionX = desc_positionX
        
    ########################################################################################################################################################################  
    ##Column 4
    ##Meatadata
    metadata_id = 'metadata'
    metadata_box = designer.add_item(MetadataBox(metadata_id, var=var, user_inputs=generator.user_inputs))
    # self,neighbor_x, y, height, title_w, title_h
    meta_positionY = part_positionY
    meta_itemHeight = part_itemHeight
    meta_title_w = generator.calculateWidth(metadata_box.children.get("title").qgs_item)
    meta_title_h = generator.calculateHeight(metadata_box.children.get("title").qgs_item,target_width_mm=meta_title_w)
    # meta_content_w = generator.calculateWidth(metadata_box.children.get("content").qgs_item)
    
    metadata_box.set_static(meta_neighbor_positionX, meta_positionY, meta_itemHeight, title_h=meta_title_h)
    meta_positionX, meta_positionY, meta_itemWidth, meta_itemHeight = metadata_box.get_FrameParameter()
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    metadata_box.set_dynamic()
    # Define dynamic positions for the frames (Bottom-Up)
    metadata_box.set_dynamic_by_id("frame",{
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{meta_neighbor_id}_frame') - GetDynamicItemWidth(@layout_name,'{metadata_id}_frame')",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{meta_neighbor_id}_frame')",
        QgsLayoutObject.ItemWidth: f"max(CalcLabelWidth(@layout_name,'{metadata_id}_content'), CalcLabelWidth(@layout_name,'{metadata_id}_title')) + {var["custom_item_dist_left"] + var["custom_item_dist_right"] + 2*var["custom_frame_line_width"]}",
        QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name,'{meta_neighbor_id}_frame')"
    })
    #########################################################################################################################################################################
    ##First Columns
    ##Legend
    legend_id = 'legend'
    lf_positionX = map_positionX
    lf_positionY = var["custom_page_size_height"] - var["custom_page_dist_bottom"] - var["custom_frame_line_width"] - var["custom_frame_height"]
    lf_itemHeight = var["custom_frame_height"]
    lf_itemWidth = meta_positionX-lf_positionX
    
    legendBox_id = "legend"
    multilegend_box = designer.add_item(MultiLegendBox(legendBox_id, map_item.qgs_item, generator.user_inputs.get("selected_layers"), generator.project, var,generator))
    multilegend_box.set_static(lf_positionX, lf_positionY, lf_itemWidth, lf_itemHeight)
    
    # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
    # Define dynamic positions for the frames (Bottom-Up)
    multilegend_box.set_dynamic_by_id("frame",{
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{map_id}')",
        QgsLayoutObject.PositionY: f"{lf_positionY}",
        QgsLayoutObject.ItemWidth: f"GetDynamicItemPositionX(@layout_name,'{metadata_id}_frame') - GetDynamicItemPositionX(@layout_name,'{map_id}')",
        QgsLayoutObject.ItemHeight: f"{lf_itemHeight}"
    })
    
    #########################################################################################################################################################################
    ##Scale bar
    scale_bar_id = 'scale_bar'
    scale_bar_item = designer.add_item(ScaleBarItem(scale_bar_id, map_item.qgs_item, var, font_size=5))
    
    sb_positionX = map_positionX + var["custom_item_dist_right"] + var["custom_frame_line_width"]
    sb_positionY = ff_positionY - var["custom_item_dist_bottom"] - var["custom_frame_line_width"] 
    sb_itemWidth = var["custom_scale_width"]
    sb_itemHeight = var["custom_scale_height"]
    scale_bar_item.set_static(sb_positionX, sb_positionY, sb_itemWidth, sb_itemHeight)
    
    scale_bar_item.set_dynamic({
        QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{map_id}') + {var['custom_item_dist_right'] + var['custom_frame_line_width']}",
        QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{format_id}_frame') - {var['custom_item_dist_bottom'] + var['custom_frame_line_width']}"
    })
    
    
    return designer.build()