"""
Script documentation
- Tool parameters are accessed using arcpy.GetParameter() or arcpy.GetParameterAsText()
- Update derived parameter values using arcpy.SetParameter() or arcpy.SetParameterAsText()
"""
from pathlib import Path
import sys
import csv
import rasterio
import numpy as np
import arcpy

def script_tool(
    dir_or_files,
    IMAGE_DIR, 
    OUT_CSV, BAD_FILES_CSV, 
    NODATA_THRESHOLD, SUSPECT_THRESHOLD, FILL_VALUE, 
    REMOVE_VALID_PERCENT, 
    #MARGINAL_VALID_PERCENT, GOOD_VALID_PERCENT, EXCELLENT_VALID_PERCENT, 
    group_chips, group_map
):
    if dir_or_files == "Folder":
        image_files = sorted(Path(IMAGE_DIR).glob("*.tif"))
    else:
        bag_list = []
        for bag in IMAGE_DIR:
            bag_list.append(bag.dataSource)
        image_files = bag_list
    def classify_valid_percent(valid_percent):
        
        #if valid_percent >= EXCELLENT_VALID_PERCENT:
        #    return "Excellent"
        #if valid_percent >= GOOD_VALID_PERCENT:
        #    return "Good"
        #if valid_percent >= MARGINAL_VALID_PERCENT:
        #    return "Edge Tile"
        
        if valid_percent >= REMOVE_VALID_PERCENT:
            return "Good" #Marginal
        return "Remove"
    NODATA_THRESHOLD = int(NODATA_THRESHOLD)
    SUSPECT_THRESHOLD = int(SUSPECT_THRESHOLD)
    FILL_VALUE = int(FILL_VALUE)
    
    REMOVE_VALID_PERCENT = np.float64(REMOVE_VALID_PERCENT)
    #MARGINAL_VALID_PERCENT = np.float64(MARGINAL_VALID_PERCENT)
    #GOOD_VALID_PERCENT = np.float64(GOOD_VALID_PERCENT)
    #EXCELLENT_VALID_PERCENT = np.float64(EXCELLENT_VALID_PERCENT)
    
    image_files = sorted(Path(IMAGE_DIR).glob("*.tif"))
    #2,500
    arcpy.AddMessage(group_map)
    arcpy.AddMessage(f"TIFFs Found: {len(image_files)}")
    
    rows = []
    affected_files = set()
    file_quality_lookup = {}
    
    total_nodata_pixels = 0
    total_suspect_pixels = 0
    total_fill_pixels = 0
    
    quality_counts = {"Good": 0,"Remove": 0} #{"Excellent": 0,"Good": 0,"Edge Tile": 0,"Marginal": 0,"Remove": 0}
    
    for idx, tif in enumerate(image_files, start=1):
        try:
            file_valid_percents = []
            with rasterio.open(tif) as src:
                for band_num in range(1, src.count + 1):
                    band = src.read(band_num).astype(np.float64)
                    masked_band = src.read(band_num, masked=True)
                    total_pixels = band.size
    
                    # ====================================================
                    # IMPORTANT FIX:
                    # np.ma.getmaskarray guarantees a full pixel mask.
                    # Without this, some files return a scalar False mask,
                    # causing valid pixels to be counted incorrectly.
                    # ====================================================
    
                    rasterio_mask = np.ma.getmaskarray(masked_band)
    
                    nodata_pixels = int(np.sum(np.abs(band) > NODATA_THRESHOLD))
                    suspect_pixels = int(np.sum(np.abs(band) >= SUSPECT_THRESHOLD))
                    fill_pixels = int(np.sum(band == FILL_VALUE))
    
                    # Valid data must be:
                    # 1. Not masked by Rasterio
                    # 2. Finite
                    # 3. Not an extreme NoData value
                    # 4. Not a 1,000,000 fill value
    
                    valid_mask = ~rasterio_mask
                    valid_mask &= np.isfinite(band)
                    valid_mask &= np.abs(band) < SUSPECT_THRESHOLD
    
                    valid_pixels = int(np.sum(valid_mask))
    
                    valid_percent = round((valid_pixels / total_pixels) * 100, 6)
                    bad_percent = round(100.0 - valid_percent, 6)
    
                    file_valid_percents.append(valid_percent)
    
                    interpretation = classify_valid_percent(valid_percent)
    
                    if nodata_pixels > 0 or suspect_pixels > 0 or fill_pixels > 0:
                        affected_files.add(tif.name)
                        total_nodata_pixels += nodata_pixels
                        total_suspect_pixels += suspect_pixels
                        total_fill_pixels += fill_pixels
    
                    if ((nodata_pixels > 0 or suspect_pixels > 0 or fill_pixels > 0 or interpretation in ["Remove"]) and len(image_files) < 2500):
                        arcpy.AddMessage(
                            f"{tif.name} \n| Band {band_num} | NoData: {nodata_pixels:,} | Suspect: {suspect_pixels:,} | Fill: {fill_pixels:,} | Valid: {valid_percent:.2f}% | {interpretation}"
                        )
                    rows.append([
                        tif.name, band_num, nodata_pixels, suspect_pixels, fill_pixels, valid_pixels, total_pixels,
                        bad_percent, valid_percent, interpretation, src.width, src.height
                    ])
    
            worst_valid_percent = min(file_valid_percents)
            file_quality = classify_valid_percent(worst_valid_percent)
    
            file_quality_lookup[tif.name] = file_quality
            quality_counts[file_quality] += 1
            
            if idx % 100 == 0:
                arcpy.AddMessage(f"==========Processed {idx:,} / {len(image_files):,}==========")
    
        except Exception as e:
            arcpy.AddMessage(f"Failed: {tif.name}")
            arcpy.AddMessage(e)
    
    with open(OUT_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "File","Band","NoDataPixels","SuspectPixels","FillPixels","ValidPixels","TotalPixels",
            "BadPercent","ValidPercent","Interpretation","Width","Height"
        ])
        writer.writerows(rows)
    bad_files = sorted([file_name for file_name, quality in file_quality_lookup.items() if quality == "Remove"])
    #marg_files = sorted([file_name for file_name, quality in file_quality_lookup.items() if quality == "Marginal"])
    #edge_files = sorted([file_name for file_name, quality in file_quality_lookup.items() if quality == "Edge Tile"])
    #good_files = sorted([file_name for file_name, quality in file_quality_lookup.items() if quality == "Good"])
    #exln_files = sorted([file_name for file_name, quality in file_quality_lookup.items() if quality == "Excellent"])
    
    with open(BAD_FILES_CSV, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["File"])
        for file_name in bad_files:
            writer.writerow([file_name])
    
    def add_tifs_to_group(group_tifs, group_name):
        group_layer = group_map.createGroupLayer(group_name)
        iter = 0
        for tif in group_tifs:
            tif_path = Path(IMAGE_DIR) / tif
            raster_layer = group_map.addDataFromPath(str(tif_path))
            group_map.addLayerToGroup(group_layer,raster_layer,"BOTTOM")
            group_map.removeLayer(raster_layer)
            if iter % 10 == 0:
                arcpy.AddMessage(f"==========Processed {iter} / {len(image_files):,}==========")
            iter+=1
    if group_chips:
        add_tifs_to_group(bad_files, "Remove Chips")
        #add_tifs_to_group(marg_files, "Marginal Chips")
        #add_tifs_to_group(edge_files, "Edge Tile Chips")
        #add_tifs_to_group(good_files, "Good Chips")
        #add_tifs_to_group(exln_files, "Excellent Chips")
    
    arcpy.AddMessage("====================================")
    arcpy.AddMessage("SCAN COMPLETE")
    arcpy.AddMessage("====================================")
    
    arcpy.AddMessage(f"Files Scanned: {len(image_files)}")
    arcpy.AddMessage(f"Files With Issues: {len(affected_files)}")
    arcpy.AddMessage(f"Band Records: {len(rows)}")
    arcpy.AddMessage(f"Total NoData Pixels: {total_nodata_pixels:,}")
    arcpy.AddMessage(f"Total Suspect Pixels: {total_suspect_pixels:,}")
    arcpy.AddMessage(f"Total Fill Pixels: {total_fill_pixels:,}")
    arcpy.AddMessage(f"Bad Files (Remove): {len(bad_files)}")
    
    arcpy.AddMessage("FILE QUALITY SUMMARY")
    arcpy.AddMessage("====================================")
    
    for key, value in quality_counts.items():
        arcpy.AddMessage(f"{key}: {value:,}")
    
    arcpy.AddMessage("NoData Report:")
    arcpy.AddMessage(OUT_CSV)
    
    arcpy.AddMessage("Bad Files List:")
    arcpy.AddMessage(BAD_FILES_CSV)
    
    arcpy.AddMessage("Done.")
    return
if __name__ == "__main__":
    folder_or_indiv = arcpy.GetParameterAsText(0)
    chips_folder = arcpy.GetParameterAsText(1)
    indiv_chips = arcpy.GetParameter(2)
    out_csv = arcpy.GetParameterAsText(3)
    bad_files_csv = arcpy.GetParameterAsText(4)
    if folder_or_indiv == "Folder":
        in_folder = chips_folder
    else:
        in_folder = indiv_chips
    
    NODATA_THRESHOLD = arcpy.GetParameterAsText(5)
    SUSPECT_THRESHOLD = arcpy.GetParameterAsText(6)
    FILL_VALUE = arcpy.GetParameterAsText(7)
    REMOVE_VALID_PERCENT = arcpy.GetParameterAsText(8)
    MARGINAL_VALID_PERCENT = arcpy.GetParameterAsText(9)
    GOOD_VALID_PERCENT = arcpy.GetParameterAsText(10)
    EXCELLENT_VALID_PERCENT = arcpy.GetParameterAsText(11)
    group_chips = bool(arcpy.GetParameterAsText(12))
    group_map = arcpy.GetParameterAsText(13)
    if group_chips and group_map == None:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        group_map = aprx.listMaps()[0]
    if group_map != None:
        aprx = arcpy.mp.ArcGISProject("CURRENT")
        group_map = next(m for m in aprx.listMaps() if m.name == group_map)
    
    script_tool(folder_or_indiv, in_folder, out_csv, bad_files_csv, 
        NODATA_THRESHOLD, SUSPECT_THRESHOLD, FILL_VALUE, REMOVE_VALID_PERCENT, 
        #MARGINAL_VALID_PERCENT, GOOD_VALID_PERCENT, EXCELLENT_VALID_PERCENT, 
        group_chips, group_map
    )
