"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or 
                                     arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or
                                        arcpy.SetParameterAsText()
"""
import arcpy
import arcgis
import os
import time
import datetime
import math
import ast
arcpy.env.overwriteOutput = True
def time_format(t): #only to tell time elapsed
    out = ""
    if t >= 3600:
        t = t / 3600 
        out+=str(math.floor(t))+" hours, "
        t-=math.floor(t)
        t = t*3600
    if t >= 60:
        t = t / 60 
        out+=str(math.floor(t))+" minutes, "
        t-=math.floor(t)
        t = t*60
    if t >= 0:
        out+=str(t)+" seconds."
    return out
def check_bags(bag_list):
    valtypes = {
        '0':  ("1-bit", "Unsigned"),
        '1':  ("2-bit", "Unsigned"),
        '2':  ("4-bit", "Unsigned"),
        '3':  ("8-bit", "Unsigned"),
        '4':  ("8-bit", "Signed"),
        '5':  ("16-bit", "Unsigned"),
        '6':  ("16-bit", "Signed"),
        '7':  ("32-bit", "Unsigned"),
        '8':  ("32-bit", "Signed"),
        '9':  ("32-bit", "Float"),
        '10': ("64-bit", "Double"),
        '11': ("8-bit", "complex"),
        '12': ("16-bit", "complex"),
        '13': ("32-bit", "complex"),
        '14': ("64-bit", "complex")
    }
    
    cell_ys = []
    cell_xs = []
    bformats = []
    pixel_depths = []
    pixel_types = []
    band_nums = []
    projections = []
    
    for bag in bag_list:
        cell_ys.append(arcpy.management.GetRasterProperties(bag, "CELLSIZEY").getOutput(0))
        cell_xs.append(arcpy.management.GetRasterProperties(bag, "CELLSIZEX").getOutput(0))
        bformats.append(arcpy.Describe(bag).format)
        pixel_depths.append(valtypes[arcpy.management.GetRasterProperties(bag, "VALUETYPE").getOutput(0)][0])
        pixel_types.append(valtypes[arcpy.management.GetRasterProperties(bag, "VALUETYPE").getOutput(0)][1])
        band_nums.append(arcpy.management.GetRasterProperties(bag, "BANDCOUNT").getOutput(0))
        projections.append(arcpy.Describe(bag).spatialReference.factoryCode)
        
    if len(set(cell_ys))>1:
        arcpy.AddError(f"Bags do not all have same cell ys: {cell_ys}")
        raise arcpy.ExecuteError
    if len(set(cell_xs))>1:
        arcpy.AddError(f"Bags do not all have same cell xs: {cell_xs}")
        raise arcpy.ExecuteError
    if len(set(bformats))>1:
        arcpy.AddError(f"Bags do not all have same formats: {bformats}")
        raise arcpy.ExecuteError
    if len(set(pixel_depths))>1:
        arcpy.AddError(f"Bags do not all have same pixel depths: {pixel_depths}")
        raise arcpy.ExecuteError
    if len(set(pixel_types))>1:
        arcpy.AddError(f"Bags do not all have same pixel types: {pixel_types}")
        raise arcpy.ExecuteError
    if len(set(band_nums))>1:
        arcpy.AddError(f"Bags do not all have same band counts: {band_nums}")
        raise arcpy.ExecuteError
    if len(set(projections))>1:
        arcpy.AddError(f"Bags do not all have same projections: {projections}")
        raise arcpy.ExecuteError
    arcpy.AddMessage(f"Bags compatibility passed")

def basic_band_mosaic(staged_mosaic: str, mosaic_band_out: str,band_num: int):
    band = arcpy.ia.ExtractBand(staged_mosaic, [band_num])
    #band_num = 1: elevation, band_num = 1: uncertainty
    band.save(mosaic_band_out)
    #no need to return but refer with mosaic_band_out
sobel_vertical = [
    [-1, 0, 1],
    [-2, 0, 2],
    [-1, 0, 1]
]
# convolution format: [[1,2,3],[4,5,6],[7,8,9]]
# in_mosaic needs to only have 1 band (e.g. an extracted mosaic)
def convolution_band_mosaic(in_mosaic: str, mosaic_band_out: str, band_num: int, conv=sobel_vertical):
    band = arcpy.ia.ExtractBand(in_mosaic, [band_num])
    result = arcgis.raster.functions.convolution(raster=arcgis.raster.Raster(band), kernel=conv)
    result.save(mosaic_band_out)
    #no need to return, just refer with mosaic_band_out
#in_mosaic needs to only have 1 band (e.g. an extracted mosaic)
def shadrel_band_mosaic(in_mosaic: str, mosaic_band_out: str, band_num: int, 
    azimuth=None, altitude=None, z_factor=None, colormap=None, colorramp=None, slope_type=None, ps_power=None, psz_factor=None, remove_edge_effect=None
    ):
    band = arcpy.ia.ExtractBand(in_mosaic, [band_num])
    shaded_relief_kwargs = {
        "raster": band
    }
    optional_args = {"azimuth": azimuth,"altitude": altitude,"z_factor": z_factor,"colormap": colormap,"colorramp": colorramp,"slope_type": slope_type,
        "ps_power": ps_power,"psz_factor": psz_factor,"remove_edge_effect": remove_edge_effect}
    for name, value in optional_args.items():
        if value not in (None, ""):
            shaded_relief_kwargs[name] = value
    shaded_relief = arcpy.sa.ShadedRelief(**shaded_relief_kwargs)
    shaded_relief.save(mosaic_band_out)
    #no need to return, just refer with mosaic_band_out
def which_band_mosaic(in_mosaic, out_mosaic, band_num, conv_type="No Calculation", conv=[], 
    azimuth=None, altitude=None, z_factor=None, colormap=None, colorramp=None, slope_type=None, ps_power=None, psz_factor=None, remove_edge_effect=None
    ):
    if conv_type == "No Calculation":
        basic_band_mosaic(in_mosaic,out_mosaic,band_num)
    if conv_type == "Sobel Vertical":
        convolution_band_mosaic(in_mosaic,out_mosaic,band_num,sobel_vertical)
    if conv_type == "Shaded Relief":
        shadrel_band_mosaic(in_mosaic,out_mosaic,band_num,azimuth=azimuth,altitude=altitude,z_factor=z_factor,
            colormap=colormap,colorramp=colorramp,slope_type=slope_type,ps_power=ps_power,psz_factor=psz_factor,remove_edge_effect=remove_edge_effect)
    if conv_type == "Custom Convolution":
        convolution_band_mosaic(in_mosaic,out_mosaic,band_num,conv)
    
       
def script_tool(
    # Main inputs
    project_folder,folderOrIndiv,bag_folder,shipwrecks_shp,
    # Band Settings
    band1,band1_calc,band1_conv,band2,band2_calc,band2_conv,band3,band3_calc,band3_conv,
    # Tile settings
    metadata_form,tile_size_x,tile_size_y,stride_x,stride_y,
    # Export Settings
    image_chip_format="TIFF", output_nofeature_tiles=None, class_value_field="ClassValue", buffer_radius=0, in_mask_polygons=None, rotation_angle=0, 
    reference_system="MAP_SPACE", processing_mode=None, blacken_around_feature="NO_BLACKEN", crop_mode="FIXED_SIZE", in_raster2=None, 
    in_instance_data=None, instance_class_value_field=None, min_polygon_overlap_ratio=None,
    # Shaded Relief Settings
    azimuth=None, altitude=None, z_factor=None, colormap=None, colorramp=None, slope_type=None, ps_power=None, psz_factor=None, 
    remove_edge_effect=None,
    # Chip Name Settings
    add_chip_names=False, chip_names=""
    ):
    
    band_order = [int(band1),int(band2),int(band3)]
    band_calc = [band1_calc,band2_calc,band3_calc]
    band_conv = [ast.literal_eval(band1_conv),ast.literal_eval(band2_conv),ast.literal_eval(band3_conv)]
    os.makedirs(project_folder, exist_ok=True)
    
    start_time = time.time()
    mosaic_gdb = os.path.join(project_folder,"MosaicRasters.gdb")
    if not arcpy.Exists(mosaic_gdb):
        arcpy.CreateFileGDB_management(project_folder, "MosaicRasters")
    staging_gdb = os.path.join(project_folder,"StagingRasters.gdb")
    if not arcpy.Exists(staging_gdb):
        arcpy.CreateFileGDB_management(project_folder, "StagingRasters")
    chip_folder = os.path.join(project_folder,"Chips")
    os.makedirs(chip_folder, exist_ok=True)
    arcpy.AddMessage(f"Begin: {datetime.datetime.now()}")
    
    if folderOrIndiv == "Folder":
        folder_names = [name for name in os.listdir(bag_folder) if os.path.isdir(os.path.join(bag_folder, name))]
        if len(folder_names)==0:
            bag_list = [os.path.join(bag_folder, file) for file in os.listdir(bag_folder) if file.endswith('.bag')]
            # non-enfolderificated
        else:
            bag_list = []
            for folder in folder_names:
                folder_dir = os.path.join(bag_folder, folder)
                bag_files = [file for file in os.listdir(folder_dir) if file.endswith('.bag')]
                for bag_file in bag_files:
                    bag_list.append(os.path.join(folder_dir, bag_file))
                    print(os.path.join(folder_dir, bag_file))
            # enfolderificated
        check_bags(bag_list)
    else:
        bag_list = []
        for bag in bag_folder:
            bag_list.append(bag.dataSource)
    # create staged mosaic from input mosaics
    staged_mosaic = os.path.join(staging_gdb,"init_mosaic_2b")
    if not arcpy.Exists(staged_mosaic):
        arcpy.management.CreateMosaicDataset(
            staging_gdb,"init_mosaic_2b",arcpy.Describe(bag_list[0]).spatialReference,
            num_bands=2,pixel_type="32_BIT_FLOAT")
    arcpy.management.AddRastersToMosaicDataset(staged_mosaic,"Raster Dataset",bag_list,update_boundary="NO_BOUNDARY")
    
    # create individual band mosaics
    bands = []
    for i in range(3):
        arcpy.AddMessage(f"Computing band {i+1} {band_calc[i]} after {time_format(time.time()-start_time)}")
        bands.append(os.path.join(staging_gdb, f"band{i+1}_{band_order[i]}{band_calc[i].replace(" ", "_")}"))
        if band_conv[i] != []:
            which_band_mosaic(staged_mosaic, bands[i], band_order[i], conv_type=band_calc[i], conv=band_conv[i], 
                azimuth=azimuth,altitude=altitude,z_factor=z_factor,colormap=colormap,colorramp=colorramp,slope_type=slope_type,
                ps_power=ps_power,psz_factor=psz_factor,remove_edge_effect=remove_edge_effect)
        elif band_calc[i] != None:
            which_band_mosaic(staged_mosaic, bands[i], band_order[i], conv_type=band_calc[i])
        if band_calc[i] == "Shaded Relief":
            band_order[1:] = ["NA"] * (len(arr)-1)
            band_calc[1:] = ["NA"] * (len(arr)-1)
            band_conv = ["NA"] * (len(arr))
            break
        if band_calc[i] != "Custom Convolution":
            band_conv[i] = "NA"
            
    # final mosaic
    final_mosaic = os.path.join(mosaic_gdb,"mosaic_3b")
    if not arcpy.Exists(final_mosaic):
        if band_calc[i] == "Shaded Relief":
            arcpy.management.CopyRaster(bands[0],final_mosaic)
        else:
            arcpy.management.CompositeBands(bands, final_mosaic)
    arcpy.AddMessage(f"Finished Mosaic {time_format(time.time()-start_time)}")
    
    # final chip extraction
    chips = os.path.join(project_folder,r"Chips\Train")
    export_kwargs = {
        "in_raster": final_mosaic,"out_folder": chips,"in_class_data": shipwrecks_shp,
        "image_chip_format": image_chip_format,"tile_size_x": tile_size_x,"tile_size_y": tile_size_y,"stride_x": stride_x,
        "stride_y": stride_y,"metadata_format": metadata_form,
        "class_value_field": class_value_field,"buffer_radius": buffer_radius,"rotation_angle": rotation_angle,
        "reference_system": reference_system,"blacken_around_feature": blacken_around_feature,"crop_mode": crop_mode,
    }
    optional_args = {
        "output_nofeature_tiles": output_nofeature_tiles,"in_mask_polygons": in_mask_polygons,"processing_mode": processing_mode,
        "in_raster2": in_raster2,"in_instance_data": in_instance_data,"instance_class_value_field": instance_class_value_field,
        "min_polygon_overlap_ratio": min_polygon_overlap_ratio,
    }
    
    for name, value in optional_args.items():
        if value not in (None, ""):
            export_kwargs[name] = value
    arcpy.ia.ExportTrainingDataForDeepLearning(**export_kwargs)
    arcpy.AddMessage(f"Extracted Chips {time_format(time.time()-start_time)}")
    parameter_txt = os.path.join(project_folder, "parameters.txt")
    parameters = {
        # Main inputs
        "project_folder": project_folder, "bag_folder": bag_folder, "shipwrecks_shp": shipwrecks_shp,
        # Band settings
        "band1": band_order[0], "band1_calc": band_calc[0], "band1_conv": band_conv[0],
        "band2": band_order[1], "band2_calc": band_calc[1], "band2_conv": band_conv[1],
        "band3": band_order[2], "band3_calc": band_calc[2], "band3_conv": band_conv[2],
        # Tile settings
        "metadata_form": metadata_form,"tile_size_x": tile_size_x,"tile_size_y": tile_size_y,
        "stride_x": stride_x,"stride_y": stride_y,
        # Export settings
        "image_chip_format": image_chip_format, "output_nofeature_tiles": output_nofeature_tiles,
        "class_value_field": class_value_field, "buffer_radius": buffer_radius, "in_mask_polygons": in_mask_polygons,
        "rotation_angle": rotation_angle, "reference_system": reference_system, "processing_mode": processing_mode,
        "blacken_around_feature": blacken_around_feature, "crop_mode": crop_mode, "in_raster2": in_raster2,
        "in_instance_data": in_instance_data, "instance_class_value_field": instance_class_value_field,
        "min_polygon_overlap_ratio": min_polygon_overlap_ratio, "add_chip_names": add_chip_names, "chip_names": chip_names
    }
    if band_calc[0] == "Shaded Relief":
        parameters.update({
            # Shaded relief settings
            "azimuth": azimuth, "altitude": altitude, "z_factor": z_factor, "colormap": colormap, "colorramp": colorramp, 
            "slope_type": slope_type, "ps_power": ps_power, "psz_factor": psz_factor, "remove_edge_effect": remove_edge_effect,
        })
    # Write parameters to text file for reference
    with open(parameter_txt, "w", encoding="utf-8") as f:
        for name, value in parameters.items():
            f.write(f"{name}: {value}\n")
    if add_chip_names:
        arcpy.AddMessage(f"Adding Chip Names {time_format(time.time()-start_time)}")
        out_chips = os.path.join(project_folder,r"Chips\Train\images")
        out_labels = os.path.join(project_folder,r"Chips\Train\labels\1")
        chip_list = [os.path.join(out_chips, file) for file in os.listdir(out_chips)]
        #label_list = [os.path.join(out_labels, file) for file in os.listdir(out_labels)]
        for chip in chip_list:
            new_chip_name = os.path.join(out_chips,chip_names+os.path.basename(chip))
            os.rename(chip,new_chip_name)
        #for label in label_list:
        #    new_label_name = os.path.join(out_labels,chip_names+os.path.basename(label))
        #    os.rename(label,new_label_name)
    return
if __name__ == "__main__":
    # Main inputs
    project_folder = arcpy.GetParameterAsText(0)
    folder_or_bags = arcpy.GetParameterAsText(1)
    bag_folder = arcpy.GetParameterAsText(2)
    indiv_bags = arcpy.GetParameter(3)
    shipwrecks_shp = arcpy.GetParameterAsText(4)
    
    if folder_or_bags == "Folder":
        out_rasters = bag_folder
    else:
        out_rasters = indiv_bags
    
    # Tile Settings
    metadata_form = arcpy.GetParameterAsText(5)
    tile_size_x = arcpy.GetParameterAsText(6)
    tile_size_y = arcpy.GetParameterAsText(7)
    stride_x = arcpy.GetParameterAsText(8)
    stride_y = arcpy.GetParameterAsText(9)
    # Export Settings
    class_value_field = arcpy.GetParameterAsText(10)
    buffer_radius = arcpy.GetParameterAsText(11)
    rotation_angle = arcpy.GetParameterAsText(12)
    reference_system = arcpy.GetParameterAsText(13)
    blacken_around_feature = arcpy.GetParameterAsText(14)
    crop_mode = arcpy.GetParameterAsText(15)
    image_chip_format = arcpy.GetParameterAsText(34)
    output_nofeature_tiles = arcpy.GetParameterAsText(35)
    in_mask_polygons = arcpy.GetParameterAsText(36)
    processing_mode = arcpy.GetParameterAsText(37)
    in_raster2 = arcpy.GetParameterAsText(38)
    in_instance_data = arcpy.GetParameterAsText(39)
    instance_class_value_field = arcpy.GetParameterAsText(40)
    min_polygon_overlap_ratio = arcpy.GetParameterAsText(41)
    # Chip Name Settings
    add_chip_names = bool(arcpy.GetParameterAsText(42))
    chip_names = arcpy.GetParameterAsText(43)
    # Band Settings
    band1 = arcpy.GetParameterAsText(16)
    band1_calc = arcpy.GetParameterAsText(17)
    band1_conv = arcpy.GetParameterAsText(18)
    band2 = arcpy.GetParameterAsText(19)
    band2_calc = arcpy.GetParameterAsText(20)
    band2_conv = arcpy.GetParameterAsText(21)
    band3 = arcpy.GetParameterAsText(22)
    band3_calc = arcpy.GetParameterAsText(23)
    band3_conv = arcpy.GetParameterAsText(24)
    # Shaded Relief
    azimuth = arcpy.GetParameterAsText(25)
    altitude = arcpy.GetParameterAsText(26)
    z_factor = arcpy.GetParameterAsText(27)
    colormap = arcpy.GetParameterAsText(28)
    colorramp = arcpy.GetParameterAsText(29)
    slope_type = arcpy.GetParameterAsText(30)
    ps_power = arcpy.GetParameterAsText(31)
    psz_factor = arcpy.GetParameterAsText(32)
    remove_edge_effect = arcpy.GetParameterAsText(33)
    
    script_tool(
        project_folder,folder_or_bags,out_rasters,shipwrecks_shp,
        
        band1,band1_calc,band1_conv,band2,band2_calc,band2_conv,band3,band3_calc,band3_conv,
        metadata_form,tile_size_x,tile_size_y,stride_x,stride_y,
        
        image_chip_format,output_nofeature_tiles,class_value_field,buffer_radius,in_mask_polygons,rotation_angle,reference_system, 
        processing_mode,blacken_around_feature,crop_mode,in_raster2,in_instance_data,instance_class_value_field,min_polygon_overlap_ratio,
        
        azimuth,altitude,z_factor,colormap,colorramp,slope_type,ps_power,psz_factor,remove_edge_effect, add_chip_names, chip_names
    )
