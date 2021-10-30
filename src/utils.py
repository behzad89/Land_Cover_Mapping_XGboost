import rasterio as rs
from rasterio.windows import from_bounds
from rasterio import mask
from rasterio import merge
import geopandas as gpd
from geoutils import grid
from owslib.wms import WebMapService
import imageio
from io import BytesIO
import numpy as np
import math
import os
import sys
from typing import List,Tuple



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
           nodata=65535,
           crs="epsg:3301",) as output_file:
        output_file.write(out_image)
        
        
def stack(images,path_out):
    transform = rs.open(images[0]).transform
    width = rs.open(images[0]).width
    height = rs.open(images[0]).height
    stack = np.concatenate([rs.open(img).read() for img in images])
    with rs.open(path_out, "w",
                       driver='GTiff',
                       count=stack.shape[0],
                       transform = transform,
                       width=width,
                       height=height,
                       nodata=65535,
                       dtype=stack.dtype,
                       crs="epsg:3301",) as output_file:
        output_file.write(stack)
        

        
        
def mosaic(path,file_name):
    items = os.listdir(path)
    img_list  = [names for names in items if names.endswith(".tif")]
    images = [rs.open(path+fname) for fname in img_list]
    full_image, transform = merge.merge(images)
    with rs.open(file_name, "w",
                       driver='GTiff',
                       count=full_image.shape[0],
                       transform = transform,
                       width=full_image.shape[2],
                       height=full_image.shape[1],
                       dtype=full_image.dtype,
                       crs="epsg:3301",) as output_file:
            output_file.write(full_image[::-1])
            
            
def exract_boundry(original_img,source_img, out_path):
    """
    original_img: The image should be mapped to the source image
    source_image: The image which should not be changed
    """
    original_ = rs.open(original_img)
    source_ = rs.open(source_img)
    minx,miny,maxx,maxy = source_.bounds
    window = from_bounds(minx, miny, maxx, maxy, transform=original_.transform)
    width=source_.width
    height=source_.height
    transform = rs.transform.from_bounds(minx,miny,maxx,maxy, width, height)
    result = original_.read(window=window,out_shape=(height,width),resampling=0)
    out_path = out_path
    with rs.open(out_path, "w",
               driver='GTiff',
               count=1,
               transform = transform,
               width=width,
               height=height,
               dtype=result.dtype,
               crs="epsg:3301",) as output_file:
        output_file.write(result)

        
        
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


def fetch_Esti_ortho(box:Tuple[float],res,out_path):
    """
    Example:
    
    def fetch_data(patch,out_path):
        minx,miny,maxx,maxy = patch.bounds
        grid_ = grid.grid(minx,maxx,miny,maxy,cell_size=500,crs=3301).generate_grid()
        for i in tqdm(range(grid_.shape[0])):
            ut.fetch_Esti_ortho(grid_.iloc[i,0].bounds,0.2,out_path)
        
    for i in range(4):
        patch = aois.iloc[i,1]
        out_path = f'../data/esti_ortho/patch_0{i+1}'
        fetch_data(patch,out_path)
        
    """
    wms = WebMapService('https://kaart.maaamet.ee/wms/alus?', version='1.1.1')
    
    east1, north1, east2, north2 = box
    width, height = round(abs(east2 - east1) / res), round(abs(north2 - north1) / res)
    
    img = wms.getmap(layers=['of10000'],
                     srs='EPSG:3301',
                     bbox=box,
                     size=(width, height),
                     format='image/png')
    
    transform = rs.transform.from_bounds(east1, north1, east2, north2, width, height)
    img = imageio.imread(BytesIO(img.read()))
    
    file_name = str(out_path+'/ee_orth_{}_{}.tif').format(int(east1),int(north1))
    with rs.open(file_name, "w",
                   driver='GTiff',
                   count=3,
                   transform = transform,
                   width=width,
                   height=height,
                   dtype='uint8',
                   crs="epsg:3301",) as output_file:
        output_file.write(np.moveaxis(img[:,:,:3],-1,0))

        
def deg2num(lat_deg, lon_deg, zoom):
    """
    ytile:row
    xtile:columns
    """
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.asinh(math.tan(lat_rad)) / math.pi) / 2.0 * n)
    return (xtile, ytile)


def num2deg(xtile, ytile, zoom):
    n = 2.0 ** zoom
    lon_deg = xtile / n * 360.0 - 180.0
    lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
    lat_deg = math.degrees(lat_rad)
    return (lat_deg, lon_deg)



def fetch_ESRI_ortho(xtile, ytile, zoom,out_path,tile_size=256):
    
    """
    Useful links:
    https://gis.stackexchange.com/questions/403162/how-to-determine-zoom-height-to-request-a-tile-from-a-wmts-server
    https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Lon..2Flat._to_tile_numbers_2
    https://docs.opengeospatial.org/is/17-083r2/17-083r2.html#61
    https://enonline.supermap.com/iPortal9D/API/WMTS/wmts_introduce.htm
    """
    
    USER_CLIENT = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"
    DEF_HEADERS = {'User-Agent': USER_CLIENT}
    
    wmts = WebMapTileService("http://server.arcgisonline.com/arcgis/rest/services/World_Imagery/MapServer/WMTS/1.0.0/WMTSCapabilities.xml",headers=DEF_HEADERS)
    tile = wmts.gettile(layer='World_Imagery', tilematrix=str(zoom), row=ytile, column=xtile, format="image/jpeg")
    
    max_lat, min_lng = num2deg(xtile, xtile, zoom)
    min_lat, max_lng = num2deg(xtile + 1, xtile + 1, zoom)
    
    transform = rs.transform.from_bounds(min_lng, min_lat, max_lng, max_lat, tile_size, tile_size)
    img = imageio.imread(BytesIO(tile.read()))

    file_name = str(out_path+'/Esri_orth_{}_{}_{}.tif').format(int(xtile),int(ytile),zoom)
    if not os.path.exists(file_name):
        with rs.open(file_name, "w",
                       driver='GTiff',
                       count=3,
                       transform = transform,
                       width=tile_size,
                       height=tile_size,
                       dtype='uint8',
                       crs="epsg:4326") as output_file:
            output_file.write(np.moveaxis(img,-1,0))
            
            
class index_calculator:
    """
    The following collection of remote sensing indices has been constructed from the information available at the https://aaltodoc.aalto.fi/handle/123456789/40777?locale-attribute=fi thesis
    for Sentinel-2 satellite specifically for wind damage detection.
    """
    def __init__(self,array):
        self.arr = array
        
        self.B02 = self.arr[2,:,:] #blue
        self.B03 = self.arr[1,:,:] #Green
        self.B04 =  self.arr[0,:,:] #red
        self.B05 =  self.arr[3,:,:] #Vegetation Red Edge 01
        self.B06 =  self.arr[4,:,:] #Vegetation Red Edge 02
        self.B07 =  self.arr[5,:,:] #Vegetation Red Edge 03
        self.B08 =  self.arr[6,:,:] #NIR
        self.B08a =  self.arr[7,:,:] #Vegetation Red Edge
        self.B11 =  self.arr[8,:,:] #SWIR1
        self.B12 =  self.arr[9,:,:] #SWIR2
        
    def ndvi(self):
        # Normalized Difference NIR/Red Normalized Difference Vegetation Index, Calibrated NDVI - CDVI (abbrv. NDVI)
        index_ndvi = (self.B08 - self.B04) / (self.B08 + self.B04)
        return index_ndvi
    
    def ndre(self):
        # Normalized Difference NIR/Rededge Normalized Difference Red-Edge (abbrv. NDRE)
        index_ndre = (self.B08 - self.B05) / (self.B08 + self.B05)
        return index_ndre
    
    def evi(self):
        # Enhanced Vegetation Index  (abbrv. EVI)
        index_evi = 2.5 * (self.B08 - self.B04) / ((self.B08 + 6.0 * self.B04 - 7.5 * self.B02) + 1.0)
        return index_evi
    
    def sbi(self):
        # Tasselled Cap - brightness  (abbrv. SBI)
        index_sbi = 0.3037 * self.B02 + 0.2793 * self.B03 + 0.4743 * self.B04 + 0.5585 * self.B08 + 0.5082 * self.B11 + 0.1863 * self.B12
        return index_sbi
    
    def gvi(self):
        # Tasselled Cap - vegetation  (abbrv. GVI)
        index_gvi = -0.2848 * self.B02 - 0.2435 * self.B03 - 0.5436 * self.B04 + 0.7243 * self.B08 + 0.084 * self.B11 - 0.18 * self.B12
        return index_gvi
    
    def wet(self):
        # Tasselled Cap - wetness  (abbrv. WET)
        index_wet = 0.1509 * self.B02 + 0.1973 * self.B03 + 0.3279 * self.B04 + 0.3406 * self.B08 - 0.7112 * self.B11 - 0.4572 * self.B12;
        return index_wet
    
    def satvi(self):
        # Soil-Adjusted Total Vegetation Index (SATVI)
        index_satvi = (((self.B11 - self.B04) / (self.B11 + self.B04 + 0.5)) * (1 + 0.5)) - (self.B12 / 2)
        return index_satvi
    
    def ndmi(self):
        # Normalized Difference 820/1600 Normalized Difference Moisture Index (abbrv. NDMI)
        index_ndmi = (self.B08 - self.B11) / (self.B08 + self.B11)
        return index_ndmi
    
    def all_indexes(self):
        ndvi = self.ndvi()
        ndre = self.ndre()
        evi = self.evi()
        sbi = self.sbi()
        gvi = self.gvi()
        wet = self.wet()
        satvi = self.satvi()
        ndmi = self.ndmi()
        
        stacked_all_indexes = np.stack([ndvi,ndre,evi,sbi,gvi,wet,satvi,ndmi],axis=0)
        
        return stacked_all_indexes
