# RasterDLTrainingScripts
Raster Deep Learning Training Geoprocessing Scripts

1. Export Chips From Mosaic
This tool merges mosaicking rasters together in a customized way for the end user to analyze for deep learning training specifically designed for .bag raster files, initially for shipwreck detection. This tool outputs training chips necessary for training deep learning model.
Individual mosaicked bands can be found in the output staging rasters geodatabase, final mosaic within the output mosaic geodatabase, training chips within the chips folder, and parameters used within the parameters.txt document.
For help on these composite scripts, check the documentation for the following methods: 
- Export Training Data for Deep Learning: https://doc.esri.com/en/arcgis-pro/latest/tool-reference/spatial-analyst/export-training-data-for-deep-learning.html?tabs=dialog
- Raster Convolutions: https://doc.esri.com/en/arcgis-pro/latest/help/analysis/raster-functions/convolution-function.html
- Shaded Relief: https://doc.esri.com/en/arcgis-pro/latest/help/analysis/raster-functions/shaded-relief-function.html

2. Inspect Chips
This tool checks raster/TIFF chip files (created by the Export Training Data for Deep Learning tool) for data quality problems before they are used for further deep-learning model training and other workflows. The results of this are then outputted as the Output CSV and Bad Files CSV.
It examines each raster chip to determine how much of the image contains usable data and identifies pixels that may represent NoData, suspicious/extreme values, or fill values. Each chip is then classified as either:
- Good — enough usable data is present.
- Remove — too much of the chip contains invalid or questionable data.
The tool can also create a "Remove Chips" group layer in the current ArcGIS Pro map so that problem chips can be easily identified and reviewed.
