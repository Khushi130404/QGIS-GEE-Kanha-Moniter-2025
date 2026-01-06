/***************************************
 * GAP-FILL FUNCTION (KEY PART)
 ***************************************/
function gapFill(date) {
  date = ee.Date(date);

  var collection = landsat
    .filterBounds(kanha)
    .filterDate(date.advance(-5, "day"), date.advance(5, "day"))
    .map(maskL8sr)
    .map(addNDVI);

  var ndvi = ee.Image(
    ee.Algorithms.If(
      collection.size().gt(0),
      collection.median(),
      // create EMPTY NDVI image with correct band
      ee.Image(0).rename("NDVI").updateMask(ee.Image(0))
    )
  );

  var clim = climatology
    .filter(ee.Filter.eq("month", date.get("month")))
    .first();

  return ndvi.unmask(clim).clip(kanha).set("system:time_start", date.millis());
}
