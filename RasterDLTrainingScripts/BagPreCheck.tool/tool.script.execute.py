"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import os
import csv
from osgeo import gdal
from collections import Counter
valtypes = {
    '0':  "1-bit Unsigned",
    '1':  "2-bit Unsigned",
    '2':  "4-bit Unsigned",
    '3':  "8-bit Unsigned",
    '4':  "8-bit Signed",
    '5':  "16-bit Unsigned",
    '6':  "16-bit Signed",
    '7':  "32-bit Unsigned",
    '8':  "32-bit Signed",
    '9':  "32-bit Float",
    '10': "64-bit Double",
    '11': "8-bit complex",
    '12': "16-bit complex",
    '13': "32-bit complex",
    '14': "64-bit complex"
}
#value_counts = dict(Counter(round(y, 6) for y in cell_ys))
def assign_to_bag(params):
    gdal_params = {
        "CELLSIZEY": "yRes",
        "CELLSIZEX": "xRes",
        "FORMAT": "format",
        "PIXELTYPE": "outputType",
        "PROJECTION": "dstSRS"
    }
    pixel_types = {
        "8-bit Unsigned": gdal.GDT_Byte,
        "8-bit Signed": getattr(gdal, "GDT_Int8", gdal.GDT_Byte),
        "16-bit Unsigned": gdal.GDT_UInt16,
        "16-bit Signed": gdal.GDT_Int16,
        "32-bit Unsigned": gdal.GDT_UInt32,
        "32-bit Signed": gdal.GDT_Int32,
        "32-bit Float": gdal.GDT_Float32,
        "64-bit Double": gdal.GDT_Float64,
        "8-bit complex": gdal.GDT_CInt16,
        "16-bit complex": gdal.GDT_CInt16,
        "32-bit complex": gdal.GDT_CInt32,
        "64-bit complex": gdal.GDT_CFloat64
    }
    bag = params[0][0]
    warp_kwargs = {}
    for bag, param, assign_var in params:
        if param == "BANDCOUNT":
            current_bands = arcpy.management.GetRasterProperties(bag,"BANDCOUNT").getOutput(0)
            arcpy.AddMessage(f"Cannot coerce band count {current_bands} into {assign_var}")
            continue
        if param == "FORMAT":
            current_format = arcpy.Describe(bag).format
            if current_format != assign_var:
                arcpy.AddMessage(f"Cannot coerce format {current_format} into {assign_var}")
            continue
        if param == "CELLSIZEY" or param == "CELLSIZEX":
            warp_kwargs[gdal_params[param]] = float(assign_var)
        if param == "PIXELTYPE":
            warp_kwargs[gdal_params[param]] = pixel_types[assign_var]
        elif param == "PROJECTION" and assign_var != 0:
            warp_kwargs["dstSRS"] = assign_var
    out_bag = bag[:-4] + "_fixed.bag"
    arcpy.AddMessage(f"Fixing bag: {bag}")
    options = gdal.WarpOptions(**warp_kwargs)
    out = gdal.Warp(out_bag,bag,options=options)
    if out is None:
        arcpy.AddWarning(f"{gdal.GetLastErrorMsg()}, no fixed BAG created")
    
def check_bags_no_params(bag_list, assign, output_csv=None, target_cell_y=None, target_cell_x=None, target_bformat=None, target_pixeltype=None, target_bandnum=None, target_projection=None, target_projection_text=None):
    cell_ys = []
    cell_xs = []
    bformats = []
    pixel_depths = []
    pixel_types = []
    band_nums = []
    projections = []
    for bag in bag_list:
        cell_ys.append(round(float(arcpy.management.GetRasterProperties(bag, "CELLSIZEY").getOutput(0)),6))
        cell_xs.append(round(float(arcpy.management.GetRasterProperties(bag, "CELLSIZEX").getOutput(0)),6))
        bformats.append(arcpy.Describe(bag).format)
        pixel_types.append(valtypes[arcpy.management.GetRasterProperties(bag, "VALUETYPE").getOutput(0)])
        band_nums.append(arcpy.management.GetRasterProperties(bag, "BANDCOUNT").getOutput(0))
        projections.append(arcpy.Describe(bag).spatialReference.factoryCode)
    err = False
    if len(set(cell_ys))>1 and target_cell_y is not None:
        most_common_cell_y = Counter(cell_ys).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same cell ys, majority: {most_common_cell_y}")
        non_majority_cell_ys = [(i, value) for i, value in enumerate(cell_ys) if value != most_common_cell_y]
        non_majority_bags = [(bag_list[i], cell_ys[i]) for i in range(len(bag_list)) if cell_ys[i] != most_common_cell_y]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the cell_y: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if len(set(cell_xs))>1 and target_cell_x is not None:
        most_common_cell_x = Counter(cell_xs).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same cell xs, majority: {most_common_cell_x}")
        non_majority_cell_xs = [(i, value) for i, value in enumerate(cell_xs) if value != most_common_cell_x]
        non_majority_bags = [(bag_list[i], cell_xs[i]) for i in range(len(bag_list)) if cell_xs[i] != most_common_cell_x]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the cell_x: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if len(set(bformats))>1 and target_bformat is not None:
        most_common_bformat = Counter(bformats).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same raster formats, majority: {most_common_bformat}")
        non_majority_bformats = [(i, value) for i, value in enumerate(bformats) if value != most_common_bformat]
        non_majority_bags = [(bag_list[i], bformats[i]) for i in range(len(bag_list)) if bformats[i] != most_common_bformat]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the bformat: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if len(set(pixel_types))>1 and target_pixeltype is not None:
        most_common_pixel_type = Counter(pixel_types).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same pixel types, majority: {most_common_pixel_type}")
        non_majority_pixel_depths = [(i, value) for i, value in enumerate(pixel_types) if value != most_common_pixel_type]
        non_majority_bags = [(bag_list[i], pixel_types[i]) for i in range(len(bag_list)) if pixel_types[i] != most_common_pixel_type]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the pixel type: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if len(set(band_nums))>1 and target_bandnum is not None:
        most_common_band_num = Counter(band_nums).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same band counts, majority: {most_common_pixel_type}")
        non_majority_band_nums = [(i, value) for i, value in enumerate(band_nums) if value != most_common_band_num]
        non_majority_bags = [(bag_list[i], band_nums[i]) for i in range(len(bag_list)) if band_nums[i] != most_common_band_num]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the band count: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if len(set(projections))>1 and target_projection_text is not None:
        most_common_projection = Counter(projections).most_common(1)[0][0]
        arcpy.AddMessage(f"Bags do not all have same projections, majority: {most_common_projection}")
        non_majority_projections = [(i, value) for i, value in enumerate(projections) if value != most_common_projection]
        non_majority_bags = [(bag_list[i], projections[i]) for i in range(len(bag_list)) if projections[i] != most_common_projection]
        for nm_bag in non_majority_bags:
            arcpy.AddMessage(f"{nm_bag[0]} has the band count: {nm_bag[1]}")
        #raise arcpy.ExecuteError
        err = True
    if err:
        raise arcpy.ExecuteError
    else:
        arcpy.AddMessage(f"Bags compatibility passed")
    
def check_bags_against_target(bag_list, assign, output_csv=None, target_cell_y=None, target_cell_x=None, target_bformat=None, target_pixeltype=None, target_bandnum=None, target_projection=None, target_projection_text=None):
    errors = []
    any_err = False
    for bag in bag_list:
        err = False
        assign_params = []
        
        bag_cell_y = arcpy.management.GetRasterProperties(bag, "CELLSIZEY").getOutput(0)
        if target_cell_y is not None and float(bag_cell_y) != float(target_cell_y):
            errors.append([bag, "CELLSIZEY", bag_cell_y, target_cell_y])
            err = True
            any_err = True
            if assign:
                assign_params.append([bag, "CELLSIZEY", target_cell_y])
        elif assign:
            assign_params.append([bag,"CELLSIZEY",bag_cell_y])
        
        bag_cell_x = arcpy.management.GetRasterProperties(bag, "CELLSIZEX").getOutput(0)
        if target_cell_x is not None and float(bag_cell_x) != float(target_cell_x):
            errors.append([bag, "CELLSIZEX", bag_cell_x, target_cell_x])
            err = True
            any_err = True
            if assign:
                assign_params.append([bag, "CELLSIZEX", target_cell_x])
        elif assign:
            assign_params.append([bag,"CELLSIZEX",bag_cell_x])
        
        bag_format = arcpy.Describe(bag).format
        if target_bformat is not None and str(bag_format) != str(target_bformat):
            errors.append([bag, "FORMAT", bag_format, target_bformat])
            err = True
            any_err = True
            if assign:
                assign_params.append([bag, "FORMAT", target_bformat])
        elif assign:
            assign_params.append([bag,"FORMAT",bag_format])
        #arcpy.AddMessage()
        bag_pixeltype = valtypes[arcpy.management.GetRasterProperties(bag, "VALUETYPE").getOutput(0)]
        if target_pixeltype is not None and str(bag_pixeltype) != str(target_pixeltype):
            errors.append([bag, "PIXELTYPE", bag_pixeltype, target_pixeltype])
            err = True
            any_err = True
            if assign:
                assign_params.append([bag, "PIXELTYPE", target_pixeltype])
        elif assign:
            assign_params.append([bag,"PIXELTYPE",bag_pixeltype])
        
        bag_bandnum = arcpy.management.GetRasterProperties(bag, "BANDCOUNT").getOutput(0)
        if target_bandnum is not None and int(bag_bandnum) != int(target_bandnum):
            errors.append([bag, "BANDCOUNT", bag_bandnum, target_bandnum])
            err = True
            any_err = True
            #if assign:
            #assign_params.append(bag, "BANDCOUNT", bag_bandnum)
        #elif assign:
        #assign_params.append([bag,"BANDCOUNT",bag_bandnum])
        
        bag_projection = arcpy.Describe(bag).spatialReference.factoryCode
        if target_projection_text is not None:
            target_proj_code = target_projection.factoryCode
            if str(bag_projection) != str(target_proj_code):
                errors.append([bag, "PROJECTION", bag_projection, target_proj_code])
                err = True
                any_err = True
                if assign:
                    assign_params.append([bag, "PROJECTION", target_projection_text])
        elif assign:
            assign_params.append([bag,"PROJECTION",bag_projection]) 
        if assign and err:
            assign_to_bag(assign_params)
            
    if err and output_csv is not None:
        with open(output_csv, "w", newline="") as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["bag_name","err_type","value","target"])
            writer.writerows(errors)
        arcpy.AddWarning(f"Compatibility check failed. Details written to {output_csv}")
        if not assign:
            raise arcpy.ExecuteError
    elif not any_err:
        arcpy.AddMessage(f"Bags compatibility passed")
def script_tool(folder_or_bags, in_rasters, assign_to_target, target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection, target_projection_text, output_csv):
    if folder_or_bags == "Folder":
        folder_names = [name for name in os.listdir(in_rasters) if os.path.isdir(os.path.join(in_rasters, name))]
        if len(folder_names)==0:
            bag_list = [os.path.join(in_rasters, file) for file in os.listdir(in_rasters) if file.endswith('.bag')]
            # non-enfolderificated
        else:
            bag_list = []
            for folder in folder_names:
                folder_dir = os.path.join(in_rasters, folder)
                bag_files = [file for file in os.listdir(folder_dir) if file.endswith('.bag')]
                for bag_file in bag_files:
                    bag_list.append(os.path.join(folder_dir, bag_file))
                    print(os.path.join(folder_dir, bag_file))
            # enfolderificated
    else:
        bag_list = []
        for bag in in_rasters:
            bag_list.append(bag.dataSource)
    if any(v is not None for v in (target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection_text)):
        check_bags_against_target(bag_list, assign_to_target, output_csv, target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection, target_projection_text)
    if any(v is None for v in (target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection_text)):
        check_bags_no_params(bag_list, assign_to_target, output_csv, target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection, target_projection_text)
    return
if __name__ == "__main__":
    folder_or_bags = arcpy.GetParameterAsText(0)
    folder = arcpy.GetParameterAsText(1)
    bags = arcpy.GetParameterAsText(2)
    
    if folder_or_bags == "Folder":
        in_rasters = folder
    else:
        in_rasters = bags
        
    output_csv = arcpy.GetParameterAsText(3) or None
    assign_to_target = arcpy.GetParameter(4)
    target_cell_y = arcpy.GetParameter(5) or None
    target_cell_x = arcpy.GetParameter(6) or None
    target_bformat = arcpy.GetParameterAsText(7) or None
    target_pixeltype = arcpy.GetParameterAsText(8) or None
    target_bandnum = arcpy.GetParameter(9) or None
    target_projection = arcpy.GetParameter(10) or None
    target_projection_text = arcpy.GetParameterAsText(10) or None
    script_tool(folder_or_bags, in_rasters, assign_to_target, target_cell_y, target_cell_x, target_bformat, target_pixeltype, target_bandnum, target_projection, target_projection_text, output_csv)
