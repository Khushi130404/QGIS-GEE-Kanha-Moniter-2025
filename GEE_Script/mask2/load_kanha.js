/***************************************
 * AOI: Kanha Region
 ***************************************/
var kanha = ee.Geometry.Rectangle([80.53, 22.05, 81.2, 22.45]);
Map.centerObject(kanha, 8);
Map.addLayer(kanha, { color: "red" }, "Kanha AOI");

/***************************************
 * Landsat 8 + Landsat 9 Collection
 ***************************************/
var landsat = ee
  .ImageCollection("LANDSAT/LC08/C02/T1_L2")
  .merge(ee.ImageCollection("LANDSAT/LC09/C02/T1_L2"));

/***************************************
 * PARAMETERS
 ***************************************/
var year = 2025;
var months = ee.List.sequence(1, 12);
var days = ee.List([5, 15, 25]); // 3 dates per month

/***************************************
 * EXPORT NDVI (ALL LAND COVER, NO CLOUD)
 ***************************************/
months.evaluate(function (monthList) {
  monthList.forEach(function (month) {
    days.evaluate(function (dayList) {
      dayList.forEach(function (day) {
        var centerDate = ee.Date.fromYMD(year, month, day);
        var start = centerDate.advance(-5, "day");
        var end = centerDate.advance(5, "day");

        var collection = landsat
          .filterBounds(kanha)
          .filterDate(start, end)
          .map(maskL8sr)
          .map(addNDVI);

        collection.size().evaluate(function (count) {
          if (count > 0) {
            var ndviImage = collection.median().clip(kanha);

            var dateStr = centerDate.format("YYYY_MM_dd").getInfo();

            Export.image.toDrive({
              image: ndviImage,
              description: "NDVI_NoCloud_" + dateStr,
              folder: "GEE_NDVI_2025",
              fileNamePrefix: "NDVI_NoCloud_" + dateStr,
              region: kanha,
              scale: 30,
              crs: "EPSG:4326",
              maxPixels: 1e13,
            });
          } else {
            print("⚠️ No data for:", centerDate.format("YYYY-MM-dd"));
          }
        });
      });
    });
  });
});
