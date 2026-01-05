import os
import re
from qgis.core import (QgsProject, QgsLayout, QgsLayoutItemMap, 
                       QgsLayoutExporter, QgsUnitTypes, QgsLayoutPoint, 
                       QgsLayoutSize, QgsLayoutItemLabel, QgsLayoutItemPage)
from PyQt5.QtGui import QFont

# --- CONFIGURATION ---
output_path = "D:/QGIS_GEE_Kanha_Moniter_2025/image/RasterLayersMask2.pdf"
date_pattern = r"(\d{4})_(\d{2})_(\d{2})"
# ---------------------

project = QgsProject.instance()

# 1. Get and SORT layers
all_layers = [l for l in project.mapLayers().values() if l.type() == QgsMapLayerType.RasterLayer]

def get_date_key(layer):
    match = re.search(date_pattern, layer.name())
    if match:
        return match.group(1) + match.group(2) + match.group(3)
    return "99999999"

sorted_layers = sorted(all_layers, key=get_date_key)
print(f"Processing {len(sorted_layers)} layers...")

# 2. Setup Layout
layout = QgsLayout(project)
layout.initializeDefaults() 

page_height = 210  
page_width = 297   

# 3. Loop through layers
for i, layer in enumerate(sorted_layers):
    
    # Add new page (skip for first one)
    if i > 0:
        new_page = QgsLayoutItemPage(layout)
        new_page.setPageSize('A4', QgsLayoutItemPage.Landscape)
        layout.pageCollection().addPage(new_page)

    y_offset = i * page_height

    # Create Map Item
    map_item = QgsLayoutItemMap(layout)
    map_item.attemptMove(QgsLayoutPoint(5, 5 + y_offset, QgsUnitTypes.LayoutMillimeters))
    map_item.attemptResize(QgsLayoutSize(page_width - 10, page_height - 20, QgsUnitTypes.LayoutMillimeters))
    
    # --- THE FIX: LOCK LAYERS ---
    # This forces this map item to ONLY render this specific layer
    # regardless of what is visible in the QGIS Layer Tree.
    map_item.setKeepLayerSet(True)
    map_item.setLayers([layer]) 
    
    # Set Extent
    map_item.setExtent(layer.extent())
    layout.addLayoutItem(map_item)

    # Add Label
    label = QgsLayoutItemLabel(layout)
    label.setText(f"{i+1}. {layer.name()}")
    label.setFont(QFont("Arial", 16, QFont.Bold))
    label.attemptMove(QgsLayoutPoint(10, 5 + y_offset, QgsUnitTypes.LayoutMillimeters))
    label.attemptResize(QgsLayoutSize(200, 15, QgsUnitTypes.LayoutMillimeters))
    layout.addLayoutItem(label)

# 4. Export
exporter = QgsLayoutExporter(layout)
settings = QgsLayoutExporter.PdfExportSettings()
settings.dpi = 150 

print("Exporting PDF... this might take a moment.")
result = exporter.exportToPdf(output_path, settings)

if result == QgsLayoutExporter.Success:
    print(f"Success! PDF saved to: {output_path}")
else:
    print(f"Export failed. Error: {result}")