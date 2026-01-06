/***************************************
 * NDVI
 ***************************************/
function addNDVI(image) {
  return image
    .normalizedDifference(["SR_B5", "SR_B4"])
    .rename("NDVI")
    .copyProperties(image, ["system:time_start"]);
}
