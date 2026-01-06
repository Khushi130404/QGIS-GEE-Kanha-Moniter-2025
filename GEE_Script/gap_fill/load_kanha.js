/***************************************
 * AOI: Kanha
 ***************************************/
var kanha = ee.Geometry.Rectangle([80.53, 22.05, 81.2, 22.45]);
Map.centerObject(kanha, 8);
Map.addLayer(kanha, { color: "red" }, "Kanha AOI");

/***************************************
 * Landsat 8 + 9 Collection (C2 L2)
 ***************************************/
var landsat = ee
  .ImageCollection("LANDSAT/LC08/C02/T1_L2")
  .merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"));

/***************************************
 * MONTHLY NDVI CLIMATOLOGY (2019–2024)
 ***************************************/
var climatology = ee.ImageCollection(
  ee.List.sequence(1, 12).map(function (month) {
    var clim = landsat
      .filterDate("2019-01-01", "2024-12-31")
      .filter(ee.Filter.calendarRange(month, month, "month"))
      .map(maskL8sr)
      .map(addNDVI)
      .median()
      .set("month", month);

    return clim;
  })
);

/***************************************
 * TARGET DATE STRINGS (5,15,25)
 ***************************************/
var year = 2025;

var dateStrings = ee.List.sequence(1, 12)
  .map(function (m) {
    return ee.List([5, 15, 25]).map(function (d) {
      return ee.Date.fromYMD(year, m, d).format("YYYY_MM_dd");
    });
  })
  .flatten();

/***************************************
 * EXPORT LOOP (CLIENT-SIDE SAFE)
 ***************************************/
dateStrings.evaluate(function (list) {
  list.forEach(function (dateStr) {
    var date = ee.Date.parse("YYYY_MM_dd", dateStr);
    var image = gapFill(date);

    Export.image.toDrive({
      image: image,
      description: "NDVI_GapFilled_" + dateStr,
      folder: "GEE_NDVI_2025",
      fileNamePrefix: "NDVI_GapFilled_" + dateStr,
      region: kanha,
      scale: 30,
      crs: "EPSG:4326",
      maxPixels: 1e13,
    });
  });
});
