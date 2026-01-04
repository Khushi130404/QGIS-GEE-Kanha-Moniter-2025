import re
from datetime import datetime
from PyQt5.QtGui import QFont

from qgis.core import (
    QgsProject,
    QgsLayout,
    QgsLayoutItemMap,
    QgsLayoutItemLabel,
    QgsLayoutExporter,
    QgsLayoutPoint,
    QgsLayoutSize,
    QgsLayoutItemPage,
    QgsUnitTypes
)

# -------------------------------
# OUTPUT PDF
# -------------------------------
output_pdf = r"D:/QGIS_GEE_Kanha_Moniter_2025/NDVI_SalForest_2025_TimeSeries.pdf"

project = QgsProject.instance()

# -------------------------------
# REGEX for date
# -------------------------------
pattern = re.compile(r"NDVI_SalForest_(\d{4})_(\d{2})_(\d{2})")

# -------------------------------
# Collect rasters
# -------------------------------
rasters = []

for layer in project.mapLayers().values():
    if layer.type() == layer.RasterLayer:
        m = pattern.match(layer.name())
        if m:
            y, mth, d = m.groups()
            rasters.append((datetime(int(y), int(mth), int(d)), layer))

rasters.sort(key=lambda x: x[0])

if not rasters:
    raise Exception("No NDVI rasters found")

# -------------------------------
# Create layout
# -------------------------------
layout = QgsLayout(project)
layout.initializeDefaults()
layout.pageCollection().clear()

# Page size (A4)
PAGE_WIDTH = 210
PAGE_HEIGHT = 297

# -------------------------------
# Create pages + content
# -------------------------------
for page_index, (date_obj, layer) in enumerate(rasters):

    # Add page
    page = QgsLayoutItemPage(layout)
    page.setPageSize(QgsLayoutSize(PAGE_WIDTH, PAGE_HEIGHT, QgsUnitTypes.LayoutMillimeters))
    layout.pageCollection().addPage(page)

    # Vertical offset for this page
    y_offset = page_index * PAGE_HEIGHT

    # ---------------- MAP ----------------
    map_item = QgsLayoutItemMap(layout)
    map_item.setRect(0, 0, 200, 180)
    map_item.setExtent(layer.extent())
    map_item.setLayers([layer])
    layout.addLayoutItem(map_item)

    map_item.attemptMove(
        QgsLayoutPoint(5, 25 + y_offset, QgsUnitTypes.LayoutMillimeters)
    )
    map_item.attemptResize(
        QgsLayoutSize(200, 180, QgsUnitTypes.LayoutMillimeters)
    )

    # ---------------- TITLE ----------------
    title = QgsLayoutItemLabel(layout)
    title.setText(layer.name())
    title.setFont(QFont("Arial", 14))
    title.adjustSizeToText()
    layout.addLayoutItem(title)

    title.attemptMove(
        QgsLayoutPoint(5, 8 + y_offset, QgsUnitTypes.LayoutMillimeters)
    )

# -------------------------------
# Export PDF
# -------------------------------
layout.refresh()

exporter = QgsLayoutExporter(layout)
pdf_settings = QgsLayoutExporter.PdfExportSettings()
pdf_settings.rasterizeWholeImage = True

exporter.exportToPdf(output_pdf, pdf_settings)

print("✅ NDVI time-series PDF exported successfully")
print(output_pdf)
