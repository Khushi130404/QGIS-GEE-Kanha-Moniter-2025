/***************************************
 * GAP-FILL FUNCTION (KEY PART)
 ***************************************/
function gapFill(date) {
  date = ee.Date(date);

  // ±5 day window
  var ndvi = landsat
    .filterBounds(kanha)
    .filterDate(date.advance(-5, "day"), date.advance(5, "day"))
    .map(maskL8sr)
    .map(addNDVI)
    .median();

  // Monthly climatology
  var clim = climatology
    .filter(ee.Filter.eq("month", date.get("month")))
    .first();

  // Fill gaps
  return ndvi.unmask(clim).clip(kanha).set("system:time_start", date.millis());
}
