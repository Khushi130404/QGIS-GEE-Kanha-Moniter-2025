import matplotlib.pyplot as plt
import numpy as np
from qgis.core import QgsProject

# ------------------------
# GET MEMORY LAYER
# ------------------------
layer_name = "Kanha_NW_TimeSeries_ROI"
layer = QgsProject.instance().mapLayersByName(layer_name)[0]

# ------------------------
# CUSTOM MONTH ORDER
# ------------------------
month_order = ["Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov",
               "Dec", "Jan", "Feb", "Mar"]
month_map = {1: "Jan", 2: "Feb", 3: "Mar", 4: "Apr",
             5: "May", 6: "Jun", 7: "Jul", 8: "Aug",
             9: "Sep", 10: "Oct", 11: "Nov", 12: "Dec"}

# ------------------------
# CREATE FULL DATE GRID
# ------------------------
full_dates = []
for m in month_order:
    for d in [5, 15, 25]:
        full_dates.append(f"{m}-{d}")

x_positions = np.arange(len(full_dates))  # numeric positions for all dates

# ------------------------
# MAP EXISTING DATA TO FULL GRID
# ------------------------
data_dict = {}
for f in layer.getFeatures():
    day = f["day"]
    month = f["month"]
    median_ndvi = f["median_ndvi"]
    month_str = month_map[month]
    key = f"{month_str}-{day}"
    data_dict[key] = median_ndvi

# y-values: NaN for missing dates
y_vals = [data_dict.get(date, np.nan) for date in full_dates]

# ------------------------
# PLOT
# ------------------------
plt.figure(figsize=(14,5))

# Plot points only where NDVI exists
for i, y in enumerate(y_vals):
    if not np.isnan(y):
        plt.plot(i, y, marker='o', color='green')

# Draw line connecting existing points
existing_indices = [i for i, y in enumerate(y_vals) if not np.isnan(y)]
existing_y = [y_vals[i] for i in existing_indices]
plt.plot(existing_indices, existing_y, linestyle='-', color='green')

# X-axis labels
plt.xticks(x_positions, full_dates, rotation=45)
plt.xlabel("Date (Month-Day)")
plt.ylabel("Median NDVI")
plt.title("NDVI Time Series (Apr → Mar) — Kanha North West")
plt.grid(True)
plt.tight_layout()
plt.show()
