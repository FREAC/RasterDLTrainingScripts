Raster Deep Learning Training Scripts
===================================

The Raster Deep Learning Training Scripts provide a workflow for preparing
and evaluating raster data for use in deep-learning applications. The tools
simplify raster processing, training-chip creation, and chip quality
checking before model training.

The workflow was initially developed to support shipwreck detection using
``.bag`` raster data, but the tools can also be adapted for other
raster-based deep-learning applications.

Workflow
--------

The scripts provide two primary tools:

1. **Export Chips From Mosaic** — prepares raster mosaics and generates
   training chips.
2. **Inspect Chips** — evaluates generated chips for data-quality problems
   before they are used for model training.

Export Chips From Mosaic
------------------------

This tool provides a customizable workflow for mosaicking raster datasets
in preparation for deep-learning training-chip extraction, with a focus on
``.bag`` raster files. It generates the raster training chips required to
develop and train deep-learning models.

The tool produces the following outputs:

* Individual mosaicked bands are stored in the output staging rasters
  geodatabase.
* The final mosaic is stored in the output mosaic geodatabase.
* Training chips are stored in the ``chips`` folder.
* Processing parameters are stored in ``parameters.txt``.

For additional information about the composite workflow, consult the
documentation for:

* Export Training Data for Deep Learning
* Raster Convolutions
* Shaded Relief

Default Settings
~~~~~~~~~~~~~~~~

Output Folder
  The folder where output image chips and metadata are stored. The folder
  can also be a folder URL that uses a cloud storage connection file
  (``*.acs``).

Folder or Individual Rasters
  Specifies whether the input rasters come from a folder or from individual
  raster layers in the ArcGIS project.

Rasters
  Specifies the input folder or set of raster layers.

Export Settings
~~~~~~~~~~~~~~~

Metadata Format
  Specifies the format used for output metadata labels. The default for
  this tool is ``RCNN_Masks``. See the Export Training Data for Deep
  Learning documentation for additional metadata format options.

Tile Size X and Y
  Specifies the size of the image chips in the x- and y-dimensions.

Stride X and Y
  Specifies the distance moved in the x- and y-directions when creating
  the next image chip. When the stride equals the tile size, there is no
  overlap. When the stride equals half the tile size, there is 50 percent
  overlap.

Add Chip Names
  Optional. Adds a string to the beginning of all chips exported by the
  tool after completion.

Optional Export Settings
~~~~~~~~~~~~~~~~~~~~~~~~

The optional export settings are not required to run the code. They
provide additional control over the Export Training Data tool.

Mosaic Settings
~~~~~~~~~~~~~~~

Elevation Band
  Specifies which numbered band (1 or 2) from the ``.bag`` files is used
  for the first band of the final output mosaic. The same concept is used
  for the second band (Uncertainty) and the third band (Convolution),
  although different convolutions can be applied to any band.

Calculation (Elevation)
  Specifies the raster calculation applied to the Elevation band.

  * **Standard** — No calculation; the band is used as-is.
  * **Sobel Convolution** — Detects vertical edges and is frequently used
    for shipwreck detection.
  * **Shaded Relief** — Converts all three bands to shaded relief. This
    option is available only for the first Elevation band.
  * **Custom Convolution** — Allows a user-defined convolution to be
    entered.

Convolution
  Available when Calculation is set to Custom Convolution. The convolution
  table specifies how each pixel is weighted in a 3x3 or 5x5 grid and can
  be edited as needed.

Shaded Relief Settings
~~~~~~~~~~~~~~~~~~~~~~

These settings are optional and provide additional control over the
Shaded Relief raster function.

Inspect Chips
-------------

The Inspect Chips tool checks raster/TIFF chip files created by the
Export Training Data for Deep Learning or Export Chips From Mosaic tools.
It identifies data-quality problems before the chips are used for further
deep-learning model training or other workflows.

The tool examines each raster chip to determine how much of the image
contains usable data and identifies pixels that may represent NoData,
suspicious or extreme values, or fill values.

Each chip is classified as either:

* **Good** — enough usable data is present.
* **Remove** — too much of the chip contains invalid or questionable data.

The tool can also create a ``Remove Chips`` group layer in the current
ArcGIS Pro map so that problem chips can be identified and reviewed.

Default Settings
~~~~~~~~~~~~~~~~

Folder or Individual Chips
  Specifies whether chips are provided as a folder or as individual
  raster layers.

Chips
  Specifies the folder or set of chip raster layers to inspect.

Output CSV
  Specifies the output summary containing the inspection results for all
  chips.

Bad Files CSV
  Specifies the output list of chips deemed fit for removal.

Group Inspected Chips
  Groups inspected chips deemed fit for removal in the ArcGIS Pro project.
  The group is placed into the specified groupings map.

Optional Parameters
~~~~~~~~~~~~~~~~~~~

No Data Threshold
  Identifies extremely large-magnitude pixel values that are treated as
  NoData or otherwise invalid values.

Suspect Threshold
  Defines the upper magnitude limit for data to be considered valid.

FILL_VALUE
  Identifies a specific pixel value used to represent filled, padded, or
  otherwise non-data areas.

Remove Valid Percent
  Specifies the threshold for deeming a chip fit for removal. If the
  percentage of valid pixels is below this threshold, the chip is marked
  ``Remove`` in the Output CSV and placed in the Bad Files CSV.
