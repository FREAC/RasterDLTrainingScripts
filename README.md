# Raster Deep Learning Training Scripts

The Raster Deep Learning Training Scripts provide a workflow for preparing and evaluating raster data for use in deep-learning applications. The tools are designed to simplify the process of processing raster datasets, creating training chips, and checking those chips for data quality before they are used to train a model. The workflow was initially developed to support shipwreck detection using .bag raster data, but the tools can also be adapted for other raster-based deep-learning applications.

# 1\. Export Chips From Mosaic

This tool provides a customizable workflow for mosaicking raster datasets in preparation for deep learning training chip extraction, with a focus on .bag raster files. It allows users to configure and process the data specifically for deep-learning applications, initially supporting shipwreck detection. The tool generates the raster training chips required to develop and train deep-learning models.

Individual mosaicked bands can be found in the output staging rasters geodatabase, final mosaic within the output mosaic geodatabase, training chips within the chips folder, and parameters used within the parameters.txt document.

For help with these composite scripts, check the documentation for the following methods:

\- [Export Training Data for Deep Learning](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/spatial-analyst/export-training-data-for-deep-learning.html?tabs=dialog)

\- [Raster Convolutions](https://doc.esri.com/en/arcgis-pro/latest/help/analysis/raster-functions/convolution-function.html)

\- [Shaded Relief](https://doc.esri.com/en/arcgis-pro/latest/help/analysis/raster-functions/shaded-relief-function.html)

## Default settings

<img width="592" height="569" alt="image" src="https://github.com/user-attachments/assets/02fbd288-51cd-4379-9d38-08579343d3c8" />


Parameters:

- Output Folder: The folder where the output image chips and metadata will be stored. The folder can also be a folder URL that uses a cloud storage connection file (\*.acs)
- Folder or Individual Rasters: Whether the input rasters is from a folder or individual raster layers from the ArcGIS project
- Rasters: Specific folder or set of raster layers

## Export Settings

<img width="589" height="419" alt="image" src="https://github.com/user-attachments/assets/2516394f-b1ac-41ff-b472-de098f7340cb" />


Parameters:

- Metadata Format: Specifies the format that will be used for the output metadata labels. Default is RCNN_Masks for this tool, but more information on the different kinds of metadata format options can be found in the documentation for [Export Training Data for Deep Learning](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/spatial-analyst/export-training-data-for-deep-learning.html?tabs=dialog).
- Tile Size X and Y: The size of the image chips for the x- and y-dimensions.
- Stride X and Y: The distance to move in the x- and y-direction when creating the next image chips. When stride is equal to tile size, there will be no overlap. When stride is equal to half the tile size, there will be 50 percent overlap.
- Add Chip Names: (Optional) Adds a string to the beginning of all chips exported by this tool after completion.

## Optional Export Settings

<img width="569" height="994" alt="image" src="https://github.com/user-attachments/assets/04adc70b-adb3-44de-907c-4b85f5c567cd" />


All these settings are not necessary for running the code but do allow for more specific control of the Export Training Data tool if desired. All are parameters within the [Export Training Data for Deep Learning](https://doc.esri.com/en/arcgis-pro/latest/tool-reference/spatial-analyst/export-training-data-for-deep-learning.html?tabs=dialog) tool.

## Mosaic Settings

<img width="598" height="403" alt="image" src="https://github.com/user-attachments/assets/53309151-cda7-46b3-99b6-07f5bbaed41b" />


Parameters:

- Elevation Band: Which numbered band (1 or 2) as input from the bag files to be used for the first band of the final output mosaic. Same concept is used for the second band (Uncertainty) and the third band (Convolution), though different convolutions can be applied to any band.
- Calculation (Elevation): Raster calculation to be completed on the Elevation band (.
  - Standard—No calculation, just the band as it is
  - Sobel Convolution—Detects vertical edges, frequently used in shipwreck
  - Shaded Relief—All three bands become shaded relief (only available for first Elevation band)
  - Custom Convolution—write or insert a user-defined convolution

<img width="581" height="202" alt="image" src="https://github.com/user-attachments/assets/1b250067-bba3-4f74-be86-f9806dd7bd87" />

- Convolution: Only visible if Calculation is set to Custom Convolution. This table shows how each pixel will be weighted in the filtering process in a 3x3 or 5x5 grid. This table can be edited as you choose. For more information, check the documentation on [convolution functions](https://doc.esri.com/en/arcgis-pro/latest/help/analysis/raster-functions/convolution-function.html).

## Shaded Relief Settings

<img width="602" height="686" alt="image" src="https://github.com/user-attachments/assets/730aafc3-2e5b-4107-8007-3ba9fa2af6b8" />


All these settings are not necessary for running the code but do allow for more specific control if desired. All are parameters within the [Shaded Relief](https://doc.esri.com/en/arcgis-pro/latest/arcpy/image-analyst/shadedrelief.html) raster function.

# 2\. Inspect Chips

This tool checks raster/TIFF chip files (created by the Export Training Data for Deep Learning or Export Chips From Mosaic tools) for data quality problems before they are used for further deep-learning model training and other workflows. The results of this are then outputted as the Output CSV and Bad Files CSV.

It examines each raster chip to determine how much of the image contains usable data and identifies pixels that may represent NoData, suspicious/extreme values, or fill values. Each chip is then classified as either:

\- Good — enough usable data is present.

\- Remove — too much of the chip contains invalid or questionable data.

The tool can also create a "Remove Chips" group layer in the current ArcGIS Pro map so that problem chips can be easily identified and reviewed.

## Default settings

<img width="591" height="592" alt="image" src="https://github.com/user-attachments/assets/f23f4bd7-f0dc-4249-aaa8-e72e86f13017" />

Parameters:

- Folder or Individual Chips: One or the other
- Chips: Specific folder or set of chip raster layers
- Output CSV: Output summary of all inspected chips
- Bad Files CSV: Output list of all chips deemed fit for removal
- Group Inspected Chips: Groups inspected chips deemed fit for removal in the ArcGIS pro project (placed into the specified groupings map)



Optional Parameters:

- No Data Threshold: Identifies extremely large-magnitude pixel values that are treated as NoData/invalid values.
- Suspect Threshold: Defines the upper magnitude limit for data to be considered valid.
- FILL_VALUE: Identifies specific pixel value used to represent filled, padded, or otherwise non-data areas.
- Remove Valid Percent: Threshold for deeming a chip fit for removal. If the chip's percent of valid pixels (containing data, not a No Data value) are below this, it will be marked "Remove" in the Output CSV and placed in the Bad Files CSV.
