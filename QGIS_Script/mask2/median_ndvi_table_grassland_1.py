import os
import numpy as np
from osgeo import gdal
from datetime import datetime

from qgis.core import (
    QgsVectorLayer,
    QgsField,
    QgsFeature,
    QgsProject
)
from PyQt5.QtCore import QVariant

# --------------------------------------------------
# USER INPUT
# --------------------------------------------------

ndvi_folder = r"D:\QGIS_GEE_Kanha_Moniter_2025\GEE_GeoPackage\GEE_NDVI_2025_Mask2"
roi_shp = r"D:\QGIS_GEE_Kanha_Moniter_2025\ROI\Grassland_1\kanha_grass_1.shp"

# --------------------------------------------------
# CREATE MEMORY TABLE
# --------------------------------------------------

table = QgsVectorLayer("None", "Kanha_Grass_TimeSeries_ROI_1", "memory")
pr = table.dataProvider()

pr.addAttributes([
    QgsField("date", QVariant.String),
    QgsField("year", QVariant.Int),
    QgsField("month", QVariant.Int),
    QgsField("day", QVariant.Int),
    QgsField("median_ndvi", QVariant.Double)
])
table.updateFields()

# --------------------------------------------------
# PROCESS EACH NDVI RASTER
# --------------------------------------------------

features = []

for file in sorted(os.listdir(ndvi_folder)):
    if not file.endswith(".tif"):
        continue

    print("Processing:", file)

    # Parse date
    parts = file.replace(".tif", "").split("_")
    year = int(parts[2])
    month = int(parts[3])
    day = int(parts[4])
    date_str = f"{year}-{month:02d}-{day:02d}"

    raster_path = os.path.join(ndvi_folder, file)

    # Warp raster to ROI in memory
    warped = gdal.Warp(
        "",
        raster_path,
        cutlineDSName=roi_shp,
        cropToCutline=True,
        dstNodata=np.nan,
        format="MEM"
    )

    band = warped.GetRasterBand(1)
    arr = band.ReadAsArray().astype(float)

    nodata = band.GetNoDataValue()
    if nodata is not None:
        arr[arr == nodata] = np.nan

    median_ndvi = np.nanmedian(arr)

    print("Median NDVI:", median_ndvi)

    f = QgsFeature()
    f.setAttributes([
        date_str,
        year,
        month,
        day,
        round(float(median_ndvi), 4)
    ])

    features.append(f)

# --------------------------------------------------
# ADD FEATURES TO TABLE
# --------------------------------------------------

pr.addFeatures(features)
table.updateExtents()

QgsProject.instance().addMapLayer(table)

print("✅ Median NDVI extracted using shapefile (no clipping layers created)")
print("Total features:", len(features))
