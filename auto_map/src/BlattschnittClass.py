import math
from multiprocessing import process
from qgis.core import (
    QgsVectorLayer, QgsFeature, QgsGeometry, QgsPointXY, QgsRectangle,
    QgsField, QgsProject, QgsWkbTypes, QgsLayoutItemMap,
    QgsLayoutObject, QgsProperty, QgsFillSymbol, QgsSingleSymbolRenderer,
    QgsPalLayerSettings, QgsTextFormat, QgsTextBufferSettings, QgsVectorLayerSimpleLabeling, Qgis
)
from PyQt5.QtCore import QVariant, QCoreApplication
from PyQt5.QtWidgets import QInputDialog
from qgis.PyQt.QtGui import QColor, QFont
from qgis.utils import iface

def create_rotated_rect(center, width, height, angle_rad):
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    hw, hh = width / 2.0, height / 2.0
    p1 = QgsPointXY(center.x() + hw * cos_a - hh * sin_a, center.y() + hw * sin_a + hh * cos_a)
    p2 = QgsPointXY(center.x() - hw * cos_a - hh * sin_a, center.y() - hw * sin_a + hh * cos_a)
    p3 = QgsPointXY(center.x() - hw * cos_a + hh * sin_a, center.y() - hw * sin_a - hh * cos_a)
    p4 = QgsPointXY(center.x() + hw * cos_a + hh * sin_a, center.y() + hw * sin_a - hh * cos_a)
    return QgsGeometry.fromPolygonXY([[p1, p2, p3, p4, p1]])

class BlattschnittTool:
    def __init__(self):
        self.layout_name = ""
        self.layer_name = "Blattschnitt"
        self.scale = 0
        self.map_uuid = ""
    
    def get_boxes_size(self, layout_name, map_uuid, scale):
            project = QgsProject.instance()
            manager = project.layoutManager()
            
            layout = manager.layoutByName(layout_name)
            self.layout_name = layout_name
            
            map_item = layout.itemByUuid(map_uuid)
            self.map_uuid = map_uuid
                    
            if not map_item or not isinstance(map_item, QgsLayoutItemMap):
                print(f"ERROR: Map frame with UUID '{map_uuid}' not found in Layout '{layout_name}'!")
                return
                
            map_w_mm = map_item.sizeWithUnits().width()
            map_h_mm = map_item.sizeWithUnits().height()
            
            ground_w = (map_w_mm / 1000.0) * scale
            ground_h = (map_h_mm / 1000.0) * scale
            # overlap_ground = (overlap_mm / 1000.0) * scale
            
            return ground_w, ground_h #, overlap_ground

    def merge_boxes(self, raw_boxes, full_line_geom, ground_w, ground_h, progress=None):
        ## Merge Boxes
        merging = True
        max_pct = 0
        
        while merging:
            merging = False
            n_boxes = len(raw_boxes)
            for i in range(n_boxes):
                if progress:
                    if progress.wasCanceled():
                        print("Process was canceled by the user.")
                        return raw_boxes
                    current_pct = 50 + int((i / n_boxes) * 45)
                    
                    if current_pct > max_pct:
                        max_pct = current_pct
                        progress.setValue(max_pct)
                    QCoreApplication.processEvents()
                
                for j in range(i + 1, len(raw_boxes)):
                    if raw_boxes[i]['geom'].intersects(raw_boxes[j]['geom']):
                        union_box = raw_boxes[i]['geom'].combine(raw_boxes[j]['geom'])
                        covered_line = full_line_geom.intersection(union_box)
                        if covered_line.length() > 0:
                            new_angle_rad = raw_boxes[i]['angle_rad'] 
                            center_pt = covered_line.boundingBox().center()
                            new_box = create_rotated_rect(center_pt, ground_w, ground_h, new_angle_rad)
                            leftover_line = covered_line.difference(new_box)
                            is_safe = False
                            if leftover_line.length() < 0.1: is_safe = True
                            else:
                                other_geom = QgsGeometry()
                                for k, bd in enumerate(raw_boxes):
                                    if k != i and k != j:
                                        other_geom = QgsGeometry(bd['geom']) if other_geom.isNull() else other_geom.combine(bd['geom'])
                                if leftover_line.difference(other_geom).length() < 0.1: is_safe = True
                            if is_safe:
                                raw_boxes.pop(j); raw_boxes.pop(i)
                                raw_boxes.append({'geom': new_box, 'angle_rad': new_angle_rad, 'angle_deg': math.degrees(new_angle_rad)})
                                merging = True; break 
                if merging: break
        
        return raw_boxes
    
    def decorate_layer(self, vl):
        # =====================================================================
        # Decorate LAYER (Outline Red + Label ID in the center)
        # =====================================================================
        
        # 1. Set Red Outline and Transparent Fill for the layer
        symbol = QgsFillSymbol.createSimple({
            'color': 'transparent',
            'outline_color': 'red',
            'outline_width': '0.8'
        })
        vl.setRenderer(QgsSingleSymbolRenderer(symbol))

        # 2. Display the fid text in the center of the box
        label_settings = QgsPalLayerSettings()
        label_settings.fieldName = 'fid'
        label_settings.isExpression = False
        label_settings.placement = Qgis.LabelPlacement.Horizontal # Force text to be at the center of the Polygon

        text_format = QgsTextFormat()
        text_format.setFont(QFont("Arial", 14, QFont.Bold))
        text_format.setColor(QColor("red"))

        # Add white border effect (Halo) around the red text to improve visibility on satellite imagery
        buffer_settings = QgsTextBufferSettings()
        buffer_settings.setEnabled(True)
        buffer_settings.setSize(1)
        buffer_settings.setColor(QColor("white"))
        text_format.setBuffer(buffer_settings)

        label_settings.setFormat(text_format)
        return label_settings
    
    
    def generate_boxes(self, i, layer_name, layout_name, map_uuid, scale, isNorth, progress= None):
        layer = QgsProject.instance().mapLayersByName(layer_name)
        layer = layer[0] if layer else None
        if layer.geometryType() == QgsWkbTypes.LineGeometry:
            self.generate_boxes_for_lines(i, layer, layout_name, map_uuid, scale, isNorth, progress)
        elif layer.geometryType() == QgsWkbTypes.PointGeometry:
            self.generate_boxes_for_points(i, layer, layout_name, map_uuid, scale, progress)
            
        
    #=====================================================================
    # STEP 1: READ EXISTING LAYOUT & GENERATE BOXES
    # =====================================================================
    def generate_boxes_for_lines(self,i,  line_layer, layout_name, map_uuid, scale, isNorth, progress= None): 
        

        # overlap_mm, ok = QInputDialog.getInt(iface.mainWindow(), "Parameters", "Enter overlap in mm:", 30, 0, 100, 5)
        # if not ok: return
        
        self.scale = scale
        self.layer_name = "Blattschnitt"+ str(i)
        ground_w, ground_h = self.get_boxes_size(layout_name, map_uuid, scale)
        
        features = list(line_layer.selectedFeatures()) or list(line_layer.getFeatures())
        full_line_geom = None
        
        total_length = 0
        for feature in features:
            if not feature.geometry().isNull():
                total_length += feature.geometry().length()
                if full_line_geom is None: full_line_geom = QgsGeometry(feature.geometry())
                else: full_line_geom = full_line_geom.combine(feature.geometry())

        if total_length == 0: total_length = 1
        raw_boxes = []
        processed_length = 0
        
        for feature in features:
            geom = feature.geometry()
            if geom.isNull(): continue
            for part_geom in geom.asGeometryCollection():
                line_length = part_geom.length()
                if line_length == 0: continue
                distance = 0
                i = 0
                while distance<= line_length:
                    if progress:
                        if progress.wasCanceled():
                            print("Processing was canceled by the user.")
                            return
                        
                        pct = int(((processed_length + distance) / total_length) *50)
                        progress.setValue(pct)
                        QCoreApplication.processEvents()
                    
                    # 1. make sure the distance does not exceed the line length
                    current_dist = min(distance, line_length)
                    pt = part_geom.interpolate(current_dist).asPoint()
                    
                    # 2. Calculate the rotation angle of the vector at that point
                    if current_dist == line_length:
                        pt_prev = part_geom.interpolate(max(0, current_dist - 1.0)).asPoint()
                        angle_rad = math.atan2(pt.y() - pt_prev.y(), pt.x() - pt_prev.x())
                    else:
                        pt_next = part_geom.interpolate(min(current_dist + 1.0, line_length)).asPoint()
                        angle_rad = math.atan2(pt_next.y() - pt.y(), pt_next.x() - pt.x())
                    if angle_rad > math.pi / 2.0:
                        angle_rad -= math.pi
                    elif angle_rad <= -math.pi / 2.0:
                        angle_rad += math.pi
                    if isNorth:
                        angle_rot = 0
                    else:
                        angle_rot = angle_rad
                        
                    
                    # 3. Draw the actual frame and save it to the list
                    box_geom = create_rotated_rect(pt, ground_w, ground_h, angle_rot)
                    raw_boxes.append({'geom': box_geom, 'angle_rad': angle_rot, 'angle_deg': math.degrees(angle_rot)})
                    
                    # 4. Find the exit point of the cable from the frame (Exit Point)
                    probe_dist = current_dist
                    while probe_dist <= line_length:
                        if not box_geom.contains(QgsGeometry.fromPointXY(part_geom.interpolate(probe_dist).asPoint())):
                            break
                        probe_dist += 1.0
                    exit_dist = probe_dist
                    
                    # If the frame has covered the entire cable -> end this line
                    if exit_dist >= line_length:
                        break
                        
                    # 5. Calculate the dynamic overlap (10% of the cable length in the frame)
                    # covered_line = part_geom.intersection(box_geom)
                    # l_in_box = covered_line.length()
                    # add_line = math.sin(angle_rot)*(ground_w/2.0)
                    l_in_box = (exit_dist - current_dist)
                    
                    if l_in_box <= 0:
                        distance += 1.0 # Đề phòng lỗi hình học của QGIS
                        continue
                        
                    overlap_len = 0.2 * l_in_box # Tính đúng 10%
                    
                    # 6. Calculate the center of the next frame
                    # The entry point into the cable = Exit point of the previous frame - 10% overlap
                    enter_next = exit_dist - overlap_len
                    
                    # print(f"i={i}, Line in box: {l_in_box}, Exit dist: {exit_dist}, Overlap len: {overlap_len}")
                    
                    # The center of the new frame will be located at a distance of half the frame width from the entry point
                    distance = enter_next + l_in_box*0.6
                    
                    processed_length += l_in_box
                    
        if progress:
            progress.setLabelText("Optimizing and merging boxes...")
            progress.setValue(50)
            QCoreApplication.processEvents()
            
        raw_boxes = self.merge_boxes(raw_boxes, full_line_geom, ground_w, ground_h, progress)

        

        vl = QgsVectorLayer(f"Polygon?crs={line_layer.crs().authid()}", self.layer_name, "memory")
        pr = vl.dataProvider()
        pr.addAttributes([QgsField("fid", QVariant.Int), QgsField("angle", QVariant.Double)])
        vl.updateFields()
        for idx, box_data in enumerate(raw_boxes):
            feat = QgsFeature()
            feat.setGeometry(box_data['geom'])
            feat.setAttributes([idx + 1, box_data['angle_deg']])
            pr.addFeatures([feat])
        
        QgsProject.instance().addMapLayer(vl)

        label_settings = self.decorate_layer(vl)

        # Enable Label
        vl.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        vl.setLabelsEnabled(True)
        
        # =====================================================================

        vl.triggerRepaint()
        print(f"\n✅ Completed to generate {len(raw_boxes)} boxes!")

    def generate_boxes_for_points(self,i, point_layer, layout_name, map_uuid, scale, progress=None):
        
        self.scale = scale
        self.layer_name = "Blattschnitt"+ str(i)
        ground_w, ground_h= self.get_boxes_size(layout_name, map_uuid, scale)

        features = list(point_layer.selectedFeatures()) or list(point_layer.getFeatures())
        total_points = len(features)
        
        if total_points == 0: total_points = 1
        processed_points = 0
        
        raw_boxes = []
        for feature in features:
            geom = feature.geometry()
            
            if progress:
                if progress.wasCanceled(): return
                pct = int((processed_points / total_points) * 90)
                progress.setValue(pct)
                QCoreApplication.processEvents()
            processed_points+=1
            
            if geom.isNull():
                continue
            
            if geom.isMultipart():
                points = geom.asMultiPoint()
            else:
                points = [geom.asPoint()]
            
            for pt in points:
                
                qgs_pt = QgsPointXY(pt)
                
                print(f"Processing point: {qgs_pt}")
                print(f"x: {qgs_pt.x()}, y: {qgs_pt.y()}")
                
                box_geom = create_rotated_rect(qgs_pt, ground_w, ground_h, 0.0)
                
                raw_boxes.append({
                    'geom': box_geom,
                    'angle_rad': 0.0, 
                    'angle_deg': 0.0
                })
            
        merging = True
        while merging:
            merging = False
            for i in range(len(raw_boxes)):
                for j in range(i + 1, len(raw_boxes)):
                    center_j = raw_boxes[j]['geom'].centroid()
                    if raw_boxes[i]['geom'].contains(center_j):
                        raw_boxes.pop(j)
                        merging = True
                        break
                if merging: break
        
        vl = QgsVectorLayer(f"Polygon?crs={point_layer.crs().authid()}", self.layer_name, "memory")
        pr = vl.dataProvider()
        pr.addAttributes([QgsField("blatt_id", QVariant.Int), QgsField("angle", QVariant.Double)])
        vl.updateFields()
        
        for idx, box_data in enumerate(raw_boxes):
            feat = QgsFeature()
            feat.setGeometry(box_data['geom'])
            feat.setAttributes([idx + 1, box_data['angle_deg']])
            pr.addFeatures([feat])
        
        QgsProject.instance().addMapLayer(vl)
        
        label_settings = self.decorate_layer(vl)
        
        # Enable Label
        vl.setLabeling(QgsVectorLayerSimpleLabeling(label_settings))
        vl.setLabelsEnabled(True)
        
        # # =====================================================================

        # vl.triggerRepaint()
        print(f"\n✅ Completed to generate {len(raw_boxes)} boxes!")
        
        
    # =====================================================================
    # Step 2: Apply Atlas with Auto-Renumbering
    # =====================================================================
    def apply_atlas(self, layer_name, layout_name, mapuuid, scale,idx_column, autorenumbering):
        if layer_name == "":
            layer_name = self.layer_name
        if layout_name == "":
            layout_name = self.layout_name
        if mapuuid == "":
            mapuuid = self.mapuuid
        if scale == "":
            scale = self.scale
        if idx_column == "":
            idx_column = "fid"
            
        project = QgsProject.instance()
        poly_layer = project.mapLayersByName(layer_name)
        if not poly_layer:
            print(f"Error: Layer {layer_name} not found!")
            return
        poly_layer = poly_layer[0]
        
        # if not self.check_parameters():
        #     print("ERROR: Parameters check failed.")
        #     return
            
        layout = project.layoutManager().layoutByName(layout_name)
        if not layout:
            print("Error: Layout not found! Please run generate_boxes() first.")
            return
        if autorenumbering:
            # Auto-Renumbering
            line_layer = None
            for layer in project.mapLayers().values():
                if isinstance(layer, QgsVectorLayer) and layer.geometryType() == QgsWkbTypes.LineGeometry:
                    line_layer = layer
                    break
                    
            if line_layer:
                full_line_geom = None
                for feature in line_layer.getFeatures():
                    geom = feature.geometry()
                    if not geom.isNull():
                        if full_line_geom is None: full_line_geom = QgsGeometry(geom)
                        else: full_line_geom = full_line_geom.combine(geom)

                poly_sorting_list = []
                for poly_feat in poly_layer.getFeatures():
                    poly_geom = poly_feat.geometry()
                    if not poly_geom.isNull():
                        centroid = poly_geom.centroid()
                        dist_along_line = full_line_geom.lineLocatePoint(centroid)
                        poly_sorting_list.append((poly_feat.id(), dist_along_line))

                poly_sorting_list.sort(key=lambda x: x[1])
                idx = poly_layer.fields().lookupField(idx_column)
                
                poly_layer.startEditing()
                new_id = 1
                for feat_id, dist in poly_sorting_list:
                    poly_layer.changeAttributeValue(feat_id, idx, new_id)
                    new_id += 1
                poly_layer.commitChanges()
                
                # Refresh the interface so that the labels display the latest ID
                poly_layer.triggerRepaint()

        # Apply Atlas
        atlas = layout.atlas()
        atlas.setEnabled(True)
        atlas.setCoverageLayer(poly_layer)
        atlas.setPageNameExpression(f'"{idx_column}"') 
        
        atlas.setSortFeatures(True)
        atlas.setSortExpression(f'"{idx_column}"')
        atlas.setSortAscending(True)
        
        atlas.setHideCoverage(True)

        map_item = layout.itemByUuid(mapuuid)
        if map_item and isinstance(map_item, QgsLayoutItemMap):
            map_item.setAtlasDriven(True)
            map_item.setAtlasScalingMode(QgsLayoutItemMap.Fixed)
            map_item.setScale(scale)
            
            prop = QgsProperty.fromExpression('"angle"')
            map_item.dataDefinedProperties().setProperty(QgsLayoutObject.MapRotation, prop)
            
            print(f"✅ Successfully applied Atlas to Layout '{layout_name}'!")
        else:
            print(f"Error: Map Item with ID '{mapuuid}' not found.")
            
            
    
