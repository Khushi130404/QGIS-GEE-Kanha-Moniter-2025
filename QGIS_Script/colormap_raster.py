from qgis.core import (
    QgsProject,
    QgsRasterShader,
    QgsColorRampShader,
    QgsSingleBandPseudoColorRenderer
)
from qgis.PyQt.QtGui import QColor

# ---- PATH TO YOUR COLOR MAP FILE ----
color_map_file = r"D:/QGIS_GEE_Kanha_Moniter_2025/pseudo_color.txt"

def load_color_map(file_path):
    items = []
    interpolation = QgsColorRampShader.Interpolated

    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            if line.startswith("INTERPOLATION"):
                if "DISCRETE" in line:
                    interpolation = QgsColorRampShader.Discrete
                elif "EXACT" in line:
                    interpolation = QgsColorRampShader.Exact
                continue

            parts = line.split(',')
            value = float(parts[0])
            r, g, b, a = map(int, parts[1:5])
            label = parts[5]

            items.append(
                QgsColorRampShader.ColorRampItem(
                    value,
                    QColor(r, g, b, a),
                    label
                )
            )

    return items, interpolation


# Load color map
color_items, interpolation_type = load_color_map(color_map_file)

# Apply to all raster layers
for layer in QgsProject.instance().mapLayers().values():
    if layer.type() == layer.RasterLayer:

        shader = QgsRasterShader()
        color_ramp = QgsColorRampShader()
        color_ramp.setColorRampType(interpolation_type)
        color_ramp.setColorRampItemList(color_items)

        shader.setRasterShaderFunction(color_ramp)

        renderer = QgsSingleBandPseudoColorRenderer(
            layer.dataProvider(),
            1,   # band number
            shader
        )

        layer.setRenderer(renderer)
        layer.triggerRepaint()

print("✅ Color map applied to all raster layers")
