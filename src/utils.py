import rasterio as rs
from rasterio.windows import from_bounds
from rasterio import mask
from rasterio import merge
import geopandas as gpd
from geoutils import grid
import numpy as np
import os
import sys



def clip_area_of_interest(geom,img,out_path):
    rast = rs.open(img)
    out_image, out_transform = mask.mask(rast, [geom], crop=True, nodata=-1)
    with rs.open(out_path, "w",
           driver='GTiff',
           count=rast.count,
           transform = out_transform,
           width=out_image.shape[2],
           height=out_image.shape[1],
           dtype=out_image.dtype,
           crs="epsg:3301",) as output_file:
        output_file.write(out_image)
        
        
def stack(images,path_out):
    transform = rs.open('../data/'+images[0]).transform
    width = rs.open('../data/'+images[0]).width
    height = rs.open('../data/'+images[0]).height
    stack = np.concatenate([rs.open('../data/'+img).read() for img in images])
    with rs.open(path_out, "w",
                       driver='GTiff',
                       count=11,
                       transform = transform,
                       width=width,
                       height=height,
                       nodata=65535,
                       dtype='uint16',
                       crs="epsg:3301",) as output_file:
        output_file.write(stack)

        
        
def list_files_with_absolute_paths(dirpath,endswith=None):
    if endswith is None:
        files = []
        for dirname, dirnames, filenames in os.walk(dirpath):
            files += [os.path.join(dirname, filename) for filename in filenames]
    else:
        files = []
        for dirname, dirnames, filenames in os.walk(dirpath):
            files += [os.path.join(dirname, filename) for filename in filenames if filename.endswith(endswith)]
    return files


def ndvi(cols):
    # Normalized Difference NIR/Red Normalized Difference Vegetation Index, Calibrated NDVI - CDVI (abbrv. NDVI)
    b08 = cols[0]
    b04 = cols[1]
    index_ndvi = (b08 - b04) / (b08 + b04)
    return index_ndvi


def ndwi(cols):
    # Normalized Difference NIR/Red Normalized Difference Vegetation Index, Calibrated NDVI - CDVI (abbrv. NDVI)
    b08 = cols[0]
    b12 = cols[1]
    index_ndvi = (b08 - b12) / (b08 + b12)
    return index_ndvi