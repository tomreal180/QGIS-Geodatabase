from numpy import var

from .base_item import BaseLayoutItem
from .basic_items import *
from qgis.core import QgsPrintLayout, QgsLayoutObject, QgsProperty


import os

class CompositeGroup(BaseLayoutItem):
    def __init__(self, item_id):
        super().__init__(item_id)
        self.children = {}

    def add_child(self, key: str, child_item: BaseLayoutItem):
        self.children[key] = child_item
    
    def get_child(self, key: str):
        return self.children.get(key)

    def create_item(self, layout: QgsPrintLayout):
        # Create all child items
        for child in self.children.values():
            child.create_item(layout)
        return None

    def add_to_layout(self, layout: QgsPrintLayout):
        for child in self.children.values():
            child.add_to_layout(layout)
    
    def set_dynamic_by_id(self, child_id, props):
        child = self.children.get(child_id)
        if child:
            child.set_dynamic(props)
        
class SmallBox(CompositeGroup):
    def __init__(self, item_id, title_text, content_text, var):
        super().__init__(item_id)
        self.var = var
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        self.add_child("title", LabelItem(f"{item_id}_title", title_text, font_size=5, is_Bold=True))
        self.add_child("content", LabelItem(f"{item_id}_content", content_text, font_size=5, is_Bold=False))

    def set_static(self, x, y, width, height, title_ItemWidth, content_ItemWidth):
        self.children["frame"].set_static(x, y, width, height)
        
        title_PositionX = x + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_left"])
        title_PositionY = y + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_top"])
        content_PositionX = title_PositionX+title_ItemWidth+ self.var["custom_dist_title_text_small"]
        content_PositionY = title_PositionY
        title_ItemHeight = height - float(self.var["custom_frame_line_width"])*2 - float(self.var["custom_item_dist_top"]) - float(self.var["custom_item_dist_bottom"])
        content_ItemHeight = title_ItemHeight
        
        
        self.children["title"].set_static(title_PositionX, title_PositionY, title_ItemWidth, title_ItemHeight)
        self.children["content"].set_static(content_PositionX, content_PositionY, content_ItemWidth, content_ItemHeight)
    def get_dynamic_dict(self, expr_max_title_w=None, expr_max_content_w=None):
        line_w_half = float(self.var["custom_frame_line_width"]) / 2
        line_w_double = float(self.var["custom_frame_line_width"]) * 2
        dist_left = float(self.var["custom_item_dist_left"])
        dist_top = float(self.var["custom_item_dist_top"])
        dist_bottom = float(self.var["custom_item_dist_bottom"])
        dist_title_text = float(self.var["custom_dist_title_text_small"])

        # If no maximum title width expression is provided, use the width of the title of this item itself.
        if not expr_max_title_w:
            expr_max_title_w = f"CalcLabelWidth(@layout_name, '{self.id}_title')"
        if not expr_max_content_w:
            expr_max_content_w = f"CalcLabelWidth(@layout_name, '{self.id}_content')"

        return {
            "title": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame') + {line_w_half + dist_left}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + {line_w_half + dist_top}",
                QgsLayoutObject.ItemWidth: f"({expr_max_title_w})",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{self.id}_frame') - {line_w_double + dist_top + dist_bottom}"
            },
            "content": {
                # Content X will be offset by the width of the longest title (expr_max_title_w)
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame') + {line_w_half + dist_left} + ({expr_max_title_w}) + {dist_title_text}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_title')",
                QgsLayoutObject.ItemWidth: f"({expr_max_content_w})",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{self.id}_title')"
            }
        }
    # def get_dynamic_dict(self, expr_max_title_w = None, expr_max_content_w=None):
    #     return {
    #         "title":{
    #             QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame') + {float(self.var['custom_frame_line_width']/2) + float(self.var['custom_item_dist_left'])}",
    #             QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + {float(self.var['custom_frame_line_width']/2) + float(self.var['custom_item_dist_top'])}",
    #             QgsLayoutObject.ItemWidth: f"({expr_max_title_w})",
    #             QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{self.id}_frame') - {float(self.var['custom_frame_line_width'])*2 + float(self.var['custom_item_dist_top']) + float(self.var['custom_item_dist_bottom'])}"
    #         },
    #         "content":{
    #             QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_title') + CalcLabelWidth(@layout_name, '{self.id}_title') + {self.var['custom_dist_title_text_small']}",
    #             QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_title')",
    #             QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name, '{self.id}_content')",
    #             QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name, '{self.id}_title')"
    #         }
    #     }
            
    def set_dynamic(self, expr_max_title_w=None, expr_max_content_w=None):
        dynamic_dict = self.get_dynamic_dict(expr_max_title_w=expr_max_title_w, expr_max_content_w=expr_max_content_w)
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)
            
        
class LegendBox(CompositeGroup):
    def __init__(self, item_id, linked_map, layer_name, project, var):
        super().__init__(item_id)
        
        self.var = var
        
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        self.add_child("title", LabelItem(f"{item_id}_title", layer_name, font_size=7, is_Bold=True))
        list_layer_names = [layer_name]
        self.add_child("content", LegendContentItem(f"{item_id}_content", linked_map, list_layer_names, project, font_size=5))
        
    def set_static(self, x, y, width, height, title_h):
        self.children["frame"].set_static(x, y, width, height)
        
        lt_positionX = x + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_left"])
        lt_positionY = y + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_top"])
        lt_itemWidth =  width - 2*float(self.var["custom_frame_line_width"]) - float(self.var["custom_item_dist_left"]) - float(self.var["custom_item_dist_right"])
        self.children["title"].set_static(lt_positionX, lt_positionY, lt_itemWidth, title_h)
        
        l_positionX = x + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_left"])
        l_positionY = y + float(self.var["custom_frame_line_width"]/2) + float(self.var["custom_item_dist_top"]) + title_h + self.var["custom_dist_title_text"]
        l_itemHeight = float(self.var["custom_frame_height"]) - float(2*self.var["custom_frame_line_width"]) - float(self.var["custom_item_dist_top"]) - float(self.var["custom_item_dist_bottom"]) - title_h - self.var["custom_dist_title_text"]
        self.children["content"].set_static(l_positionX, l_positionY, 0, l_itemHeight)
        
        legend_qgs = self.children["content"].qgs_item
        if legend_qgs:
            legend_qgs.adjustBoxSize()
            l_itemWidth = legend_qgs.boundingRect().width()
            self.children["content"].set_static(l_positionX, l_positionY, l_itemWidth, l_itemHeight)
            
    def get_dynamic_dict(self):
        return {
            "title": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name ,'{self.id}_frame') + ({self.var['custom_frame_line_width']})/2 + {self.var['custom_item_dist_left']}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name ,'{self.id}_frame') + ({self.var['custom_frame_line_width']})/2 + {self.var['custom_item_dist_top']}",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name ,'{self.id}_frame') - 2*{self.var['custom_frame_line_width']} - {self.var['custom_item_dist_right']} - {self.var['custom_item_dist_left']}",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name, '{self.id}_title')"
            },
            "content": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name ,'{self.id}_frame') + ({self.var['custom_frame_line_width']})/2 + {self.var['custom_item_dist_left']}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name ,'{self.id}_frame') + {self.var['custom_frame_line_width']}/2 + {self.var['custom_item_dist_top']} + GetDynamicItemHeight(@layout_name,'{self.id}_title') + {self.var['custom_dist_title_text']}",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name ,'{self.id}_frame') - 2*{self.var['custom_frame_line_width']} - {self.var['custom_item_dist_right']} - {self.var['custom_item_dist_left']}"
            }
        }
        
    def set_dynamic(self):
        dynamic_dict = self.get_dynamic_dict()
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)

class MultiLegendBox(CompositeGroup):
    def __init__(self, item_id, linked_map, selected_layers, project, var, generator):
        super().__init__(item_id)
        self.var = var
        self.generator = generator
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=var["custom_frame_line_width"]))
        for i, layer in enumerate(selected_layers):
            legend_id = f"{item_id}_legendBox_{i}"
            self.add_child(legend_id, LegendBox(legend_id, linked_map, layer, project, var))
        
    def set_static(self, x, y, width, height):
        self.children["frame"].set_static(x, y, width, height)
        legend_ids = [child_id for child_id in self.children if child_id != "frame"]
        num_legends = len(legend_ids)
        
        if num_legends == 0:
            return
            
        box_positionX = x
        box_itemWidth = width / num_legends
        
        for i, child_id in enumerate(legend_ids):   
            child = self.children.get(child_id)
            title_h = self.generator.calculateHeight(child.children.get("title").qgs_item)
            child.set_static(box_positionX, y, box_itemWidth, height, title_h)
            # ---------------- CREATE DYNAMIC EXPRESSIONS ----------------
            child.set_dynamic()
            # Update the position for the next child in the composite group
            child.set_dynamic_by_id("frame",{
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{self.id}_frame')+{i}*GetDynamicItemWidth(@layout_name,'{child_id}_frame')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{self.id}_frame')",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name,'{self.id}_frame')/{num_legends}",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemHeight(@layout_name,'{self.id}_frame')"
            })
            box_positionX += box_itemWidth
            
    
class CompanyBox(CompositeGroup):
    def __init__(self,item_id, var,title,logo, name, adresse, font_family="Calibri", font_size=5):
        super().__init__(item_id)
        self.var = var
        
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=var["custom_frame_line_width"]))
        
        self.add_child("title", LabelItem(f"{item_id}_title", title, font_family, font_size = 5))
        
        # svg_logo_path = os.path.join(os.path.dirname(__file__), "assets", logo)
        self.add_child("logo", PictureItem(f"{item_id}_logo", logo))
        
        self.add_child("name", LabelItem(f"{item_id}_name", name, font_family, font_size))

        self.add_child("adresse", LabelItem(f"{item_id}_adresse", adresse, font_family, font_size))
        
    def set_static(self, x, y, width, height, title_h, name_h, adresse_h, logo_h = None):
        self.children["frame"].set_static(x, y, width, height)
        
        ct_positionX = x + self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_left"]
        ct_positionY = y + self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_top"]
        ct_width = width - self.var["custom_frame_line_width"] - self.var["custom_item_dist_left"] - self.var["custom_item_dist_right"]
        self.children["title"].set_static(ct_positionX, ct_positionY, ct_width, title_h)
        
        cl_positionX = ct_positionX
        cl_positionY = ct_positionY + title_h #+ self.var["custom_item_dist_top"]
        cl_width = ct_width
            
        # cl_height = (cl_width*6.)/25.
        if logo_h is not None:
            cl_height = logo_h
        else:
            cl_height = 7.5
        self.children["logo"].set_static(cl_positionX, cl_positionY, cl_width, cl_height)
        
        cn_positionX = cl_positionX
        cn_positionY = cl_positionY + cl_height #+ self.var["custom_item_dist_top"]
        cn_width = ct_width
        self.children["name"].set_static(cn_positionX, cn_positionY, cn_width, name_h)
        
        ca_positionX = cl_positionX
        ca_positionY = cn_positionY + name_h + self.var["custom_dist_title_text"]
        ca_width = ct_width
        self.children["adresse"].set_static(ca_positionX, ca_positionY, ca_width, adresse_h)

    def get_dynamic_dict(self):
        return {
            "title": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame') + {self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_left"]}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + {self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_top"]}",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{self.id}_frame') - ({self.var["custom_frame_line_width"] + self.var["custom_item_dist_left"] + self.var["custom_item_dist_right"]})",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name, '{self.id}_title')"
            },
            "logo":{
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_title')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_title') + CalcLabelHeight(@layout_name, '{self.id}_title')",
                # QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{self.id}_title')",
                # QgsLayoutObject.ItemHeight: f"(GetDynamicItemWidth(@layout_name, '{self.id}_logo') * 6)/25"
            },
            "name": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_logo')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_logo') + GetDynamicItemHeight(@layout_name, '{self.id}_logo')",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{self.id}_title')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name, '{self.id}_name')"
            },
            "adresse":{
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_logo')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_name') + GetDynamicItemHeight(@layout_name, '{self.id}_name')+{self.var["custom_dist_title_text"]}",
                QgsLayoutObject.ItemWidth: f"GetDynamicItemWidth(@layout_name, '{self.id}_title')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name, '{self.id}_adresse')"
            }
        }
            
    def set_dynamic(self):
        dynamic_dict = self.get_dynamic_dict()
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)
            

class NorthArrowBox(CompositeGroup):
    def __init__(self, item_id, var,):
        super().__init__(item_id)
        self.var = var
        
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        self.add_child("north_arrow", PictureItem(f"{item_id}_north_arrow", os.path.join(os.path.dirname(__file__), "assets", "NorthArrow.svg")))
     
    def get_FrameParameter(self):
        return self.naf_positionX, self.naf_positionY, self.naf_Itemwidth, self.naf_ItemHeight
    def set_static(self,neighbor_x, y, height):
        # self.children["frame"].set_static(x, y, width, height)
        na_itemWidth = self.var["custom_north_arrow_width"]
        na_itemHeight = self.var["custom_north_arrow_height"]
        na_positionY = y+self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_top"]+height/2-na_itemHeight/2
        na_positionX = neighbor_x - self.var["custom_frame_line_width"]/2 - self.var["custom_item_dist_right"] - na_itemWidth
        self.naf_Itemwidth = na_itemWidth+ 2*self.var["custom_frame_line_width"] + self.var["custom_item_dist_left"] + self.var["custom_item_dist_right"]
        self.naf_positionX = neighbor_x - self.naf_Itemwidth
        self.naf_positionY = y
        self.naf_ItemHeight = height
       
        self.children["frame"].set_static(self.naf_positionX, self.naf_positionY, self.naf_Itemwidth, self.naf_ItemHeight)
        self.children["north_arrow"].set_static(na_positionX, na_positionY, na_itemWidth, na_itemHeight)
    
    def get_dynamic_dict(self, neighbor):
        return {
            "north_arrow": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{neighbor}_frame')- {self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_right"]}- GetDynamicItemWidth(@layout_name, '{self.id}_north_arrow')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + {self.var["custom_frame_line_width"]/2 + self.var["custom_item_dist_top"]} +(GetDynamicItemHeight(@layout_name, '{self.id}_frame')/2 - GetDynamicItemHeight(@layout_name, '{self.id}_north_arrow')/2)",
                QgsLayoutObject.ItemWidth: f"{self.var['custom_north_arrow_width']}",
                QgsLayoutObject.ItemHeight: f"{self.var['custom_north_arrow_height']}"
            }
        }
                
    def set_dynamic(self, neighbor):
        dynamic_dict = self.get_dynamic_dict(neighbor)
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)

class GenericBox(CompositeGroup):
    def __init__(self, item_id, content_text, var , font_size=7, middle = False):
        super().__init__(item_id)
        self.var = var
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        self.add_child("content", LabelItem(f"{item_id}_content", content_text, font_size= font_size, is_Bold=False, middle=middle))
    
    def get_FrameParameter(self):
        return self.gf_postionX, self.gf_positionY, self.gf_itemWidth, self.gf_itemHeight
    def set_static(self,neighbor_x, y, height, content_w, content_h, item_dist = None):
        if item_dist is None:
            item_dist = self.var["custom_item_dist_left"]
            
        self.gf_itemWidth= content_w + self.var["custom_frame_line_width"]*2 + 2*item_dist
        self.gf_postionX = neighbor_x - self.gf_itemWidth
        self.gf_positionY = y
        self.gf_itemHeight = height
        self.children["frame"].set_static(self.gf_postionX, self.gf_positionY, self.gf_itemWidth, self.gf_itemHeight)
        
        gc_positionX = self.gf_postionX + self.var["custom_frame_line_width"] + item_dist
        gc_positionY = self.gf_positionY + self.gf_itemHeight/2- content_h/2
        self.children["content"].set_static(gc_positionX, gc_positionY, content_w, content_h)
        
    def get_dynamic_dict(self, item_dist=None):
        if item_dist is None:
            item_dist = self.var["custom_item_dist_left"]
        
        dynamic_dict = {
            "content": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{self.id}_frame')+{ self.var['custom_frame_line_width'] + item_dist}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{self.id}_frame')+GetDynamicItemHeight(@layout_name,'{self.id}_frame')/2-CalcLabelHeight(@layout_name,'{self.id}_content')/2",
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_content')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name,'{self.id}_content')"
            }
        }
        return dynamic_dict
    
    def set_dynamic(self, item_dist=None):
        dynamic_dict = self.get_dynamic_dict(item_dist=item_dist)
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)

class DescriptionBox(CompositeGroup):
    def __init__(self, item_id, street_desc, linked_map, vegetation_names, project, var):
        super().__init__(item_id)
        self.var = var
        self.has_street = bool(street_desc and str(street_desc).strip())
        self.has_veg = bool(vegetation_names and any(str(name).strip() for name in vegetation_names))
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        if self.has_street:
            self.add_child("street_title", LabelItem(f"{item_id}_street_title", text="Beschriftungen der Längstrasse:", font_size=7,is_Bold=True))
            self.add_child("street_content", LabelItem(f"{item_id}_street_content", text=street_desc, font_size=4, middle=True, background=True))
        if self.has_veg:
            self.add_child("vegetation_title", LabelItem(f"{item_id}_vegetation_title", text="Vegetationsbestand:", font_size=7, is_Bold=True))
            self.add_child("vegetation_content", LegendContentItem(f"{item_id}_vegetation_content", linked_map=linked_map, layer_names=vegetation_names, project=project))
        
        # self.add_child("vegetation_title", LabelItem(f"{item_id}_vegetation_title", text="Vegetationsbestand:", font_size=7, is_Bold=True))
        # self.add_child("vegetation_content", LegendContentItem(f"{item_id}_vegetation_content", linked_map=linked_map, layer_name=vegetation_name, project=project))

    def get_FrameParameter(self):
        return self.df_positionX, self.df_positionY, self.df_itemWidth, self.df_itemHeight
    
    def set_static(self, neighbor_x,y, height, title_w, title_h, content_street_w = None,content_street_h = None):
        self.df_itemWidth = title_w + self.var["custom_frame_line_width"]*2 + self.var["custom_item_dist_left"] + self.var["custom_item_dist_right"]
        self.df_positionX = neighbor_x - self.df_itemWidth
        self.df_positionY = y
        self.df_itemHeight = height
        self.children["frame"].set_static(self.df_positionX, self.df_positionY, self.df_itemWidth, self.df_itemHeight)
        
        base_X = self.df_positionX + self.var["custom_frame_line_width"] + self.var["custom_item_dist_left"]
        current_Y = self.df_positionY + self.var["custom_frame_line_width"] + self.var["custom_item_dist_top"]
        if self.has_street:
            self.children["street_title"].set_static(base_X, current_Y, title_w, title_h)
            current_Y += title_h + self.var["custom_dist_title_text"]
            dsc_positionX = base_X + title_w/2-(content_street_w-2)/2
            self.children["street_content"].set_static(dsc_positionX, current_Y, content_street_w, content_street_h+4)
            current_Y += content_street_h + 4 + self.var["custom_dist_title_text"]
        if self.has_veg:
            self.children["vegetation_title"].set_static(base_X, current_Y, title_w, title_h)
            current_Y += title_h + self.var["custom_dist_title_text"]
            
            dvc_itemHeight = self.df_positionY + self.df_itemHeight - self.var["custom_frame_line_width"] - self.var["custom_item_dist_bottom"] - current_Y
            self.children["vegetation_content"].set_static(base_X, current_Y, title_w, dvc_itemHeight)
    
    def get_dynamic_dict(self):
        dynamic_dict = {}
        
        previous_bottom_expr = f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + {self.var['custom_frame_line_width']} + {self.var['custom_item_dist_top']}"
        
        if self.has_street:
            dynamic_dict["street_title"] = {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame')+ {self.var['custom_frame_line_width']} + {self.var['custom_item_dist_left']}",
                QgsLayoutObject.PositionY: previous_bottom_expr,
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_street_title')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name,'{self.id}_street_title')"
            }
            
            dynamic_dict["street_content"] = {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_street_title') + GetDynamicItemWidth(@layout_name, '{self.id}_street_title')/2 - (CalcLabelWidth(@layout_name, '{self.id}_street_content'))/2",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_street_title') + GetDynamicItemHeight(@layout_name, '{self.id}_street_title') + {self.var['custom_dist_title_text']}",
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_street_content')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name,'{self.id}_street_content') + 4"
            }
            
            previous_bottom_expr = f"GetDynamicItemPositionY(@layout_name, '{self.id}_street_content') + GetDynamicItemHeight(@layout_name, '{self.id}_street_content') + {self.var['custom_dist_title_text']}"
        
        if self.has_veg:
            dynamic_dict["vegetation_title"] = {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_frame') + {self.var['custom_frame_line_width']} + {self.var['custom_item_dist_left']}",
                QgsLayoutObject.PositionY: previous_bottom_expr,
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_vegetation_title')",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name,'{self.id}_vegetation_title')"
            }
            
            dynamic_dict["vegetation_content"] = {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_vegetation_title')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_vegetation_title') + GetDynamicItemHeight(@layout_name, '{self.id}_vegetation_title') + {self.var['custom_dist_title_text']}",
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_vegetation_title')",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + GetDynamicItemHeight(@layout_name, '{self.id}_frame') - {self.var['custom_frame_line_width']} - {self.var['custom_item_dist_bottom']} - GetDynamicItemPositionY(@layout_name, '{self.id}_vegetation_title') - GetDynamicItemHeight(@layout_name, '{self.id}_vegetation_title')"
            }
        return dynamic_dict
        
    def set_dynamic(self):
        dynamic_dict = self.get_dynamic_dict()
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)

class MetadataBox(CompositeGroup): 
    def __init__(self, item_id,var,user_inputs):
        super().__init__(item_id)
        self.var = var
        self.user_inputs = user_inputs
        
        self.add_child("frame", ShapeItem(f"{item_id}_frame", stroke_width=self.var["custom_frame_line_width"]))
        self.add_child("title", LabelItem(f"{item_id}_title", text="Hinweise/ Sonstiges", font_size = 7))
        
        hinweise = self.user_inputs.get('hinweise')
        # datagrundlage = "Die zu genehmigende Trasse wird in Rot dargestellt.Hausanschlüsse sind generalisiert dargestellt, erfolgen unterirdisch und werden in der Regel über bereits vorhandene Mauerdurchführungen realisiert.Neue Durchführungen sind nur bei Bedarf und in Abstimmung vorgesehen."
        hinweise = hinweise if hinweise else "XXX"
        hintergrundlage = self.user_inputs.get('hintergrundlage')
        hintergrundlage = hintergrundlage if hintergrundlage else "XXX"
        Sonstige = self.user_inputs.get('sonstige')
        metadata_text = f"{hinweise}\n\nHintergrundkarte: \n© {hintergrundlage}\n"
        if Sonstige:
            metadata_text += f"Sonstige Karteninhalte: \n{Sonstige}\n"
        self.add_child("content", LabelItem(f"{item_id}_content", text=metadata_text, font_size = 5))
    
    def get_FrameParameter(self):
        return self.mf_positionX, self.mf_positionY, self.mf_itemWidth, self.mf_itemHeight
    
    def set_static(self,neighbor_x, y, height, title_h):
        title_w = 35
        self.mf_itemWidth = title_w + self.var["custom_item_dist_left"] + self.var["custom_item_dist_right"] + 2*self.var["custom_frame_line_width"]
        self.mf_positionX = neighbor_x - self.mf_itemWidth
        self.mf_positionY = y
        self.mf_itemHeight = height
        self.children.get("frame").set_static(self.mf_positionX, self.mf_positionY, self.mf_itemWidth, self.mf_itemHeight)
        
        mt_positionX = self.mf_positionX + self.var["custom_frame_line_width"] + self.var["custom_item_dist_left"]
        mt_positionY = self.mf_positionY + self.var["custom_frame_line_width"] + self.var["custom_item_dist_top"]
        self.children.get("title").set_static(mt_positionX, mt_positionY, title_w, title_h)
        
        mc_positionX = mt_positionX
        mc_positionY = mt_positionY + title_h + self.var["custom_dist_title_text"]
        mc_itemWidth = title_w
        mc_itemHeight = self.mf_positionY + self.mf_itemHeight - mt_positionY - title_h - self.var["custom_dist_title_text"] - self.var["custom_item_dist_bottom"] - self.var["custom_frame_line_width"]
        self.children.get("content").set_static(mc_positionX, mc_positionY, mc_itemWidth, mc_itemHeight)       
        
    def get_dynamic_dict(self):
        return {
            "title": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name,'{self.id}_frame')+ {self.var['custom_frame_line_width'] + self.var['custom_item_dist_left']}",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name,'{self.id}_frame')+ {self.var['custom_frame_line_width'] + self.var['custom_item_dist_top']}",
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_frame') - {self.var['custom_frame_line_width']*2 + self.var['custom_item_dist_left'] + self.var['custom_item_dist_right']}",
                QgsLayoutObject.ItemHeight: f"CalcLabelHeight(@layout_name,'{self.id}_title')"
            },
            "content": {
                QgsLayoutObject.PositionX: f"GetDynamicItemPositionX(@layout_name, '{self.id}_title')",
                QgsLayoutObject.PositionY: f"GetDynamicItemPositionY(@layout_name, '{self.id}_title') + GetDynamicItemHeight(@layout_name, '{self.id}_title') + {self.var['custom_dist_title_text']}",
                QgsLayoutObject.ItemWidth: f"CalcLabelWidth(@layout_name,'{self.id}_content')",
                QgsLayoutObject.ItemHeight: f"GetDynamicItemPositionY(@layout_name, '{self.id}_frame') + GetDynamicItemHeight(@layout_name, '{self.id}_frame') - GetDynamicItemPositionY(@layout_name, '{self.id}_title') - GetDynamicItemHeight(@layout_name, '{self.id}_title') - {self.var["custom_dist_title_text"] + self.var["custom_item_dist_bottom"] + self.var["custom_frame_line_width"]}"
            }
        }
        
    def set_dynamic(self):
        dynamic_dict = self.get_dynamic_dict()
        for child_id, props in dynamic_dict.items():
            self.set_dynamic_by_id(child_id, props)
