import os
import numpy as np
from osgeo import gdal
from datetime import datetime

from qgis.core import QgsVectorLayer, QgsField, QgsFeature, QgsProject
from PyQt5.QtCore import QVariant

# ------------------------
# USER INPUT
# ------------------------
folder = r"D:\QGIS_GEE_Kanha_Moniter_2025\GEE_GeoPackage\GEE_NDVI_2025_Mask2"

# ------------------------
# CREATE MEMORY LAYER
# ------------------------
layer = QgsVectorLayer("None", "NDVI_2025_Table", "memory")
pr = layer.dataProvider()

pr.addAttributes([
    QgsField("date", QVariant.String),
    QgsField("year", QVariant.Int),
    QgsField("month", QVariant.Int),
    QgsField("day", QVariant.Int),
    QgsField("median_ndvi", QVariant.Double)
])
layer.updateFields()

# ------------------------
# PROCESS RASTERS
# ------------------------
results = []

files = sorted([f for f in os.listdir(folder) if f.lower().endswith(".tif")])

for file in files:
    try:
        # Extract year, month, day from filename
        parts = file.replace(".tif", "").split("_")
        year = int(parts[2])
        month = int(parts[3])
        day = int(parts[4])
        date_str = f"{day}-{month}-{year}"

        # Open raster
        ds = gdal.Open(os.path.join(folder, file))
        if ds is None:
            print("❌ Cannot open:", file)
            continue

        band = ds.GetRasterBand(1)
        arr = band.ReadAsArray().astype(float)

        nodata = band.GetNoDataValue()
        if nodata is not None:
            arr[arr == nodata] = np.nan

        # Median NDVI
        median_ndvi = float(np.nanmedian(arr))

        print(f"Processed {file} → Median NDVI: {median_ndvi:.4f}")

        # Add feature to memory layer
        f = QgsFeature()
        f.setAttributes([date_str, year, month, day, median_ndvi])
        pr.addFeature(f)

    except Exception as e:
        print("❌ Error processing", file, e)

# ------------------------
# ADD LAYER TO PROJECT
# ------------------------
QgsProject.instance().addMapLayer(layer)
print("✅ NDVI time-series table created successfully")
