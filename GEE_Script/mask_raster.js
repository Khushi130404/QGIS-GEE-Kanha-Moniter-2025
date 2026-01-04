/***************************************
 * Functions
 ***************************************/
function maskL8sr(image) {
  var qa = image.select("QA_PIXEL");

  // Bit 3 = cloud, Bit 4 = cloud shadow
  var cloud = qa.bitwiseAnd(1 << 3).eq(0);
  var shadow = qa.bitwiseAnd(1 << 4).eq(0);

  return image
    .updateMask(cloud)
    .updateMask(shadow)
    .select(["SR_B4", "SR_B5"])
    .multiply(0.0000275)
    .add(-0.2)
    .copyProperties(image, ["system:time_start"]);
}
