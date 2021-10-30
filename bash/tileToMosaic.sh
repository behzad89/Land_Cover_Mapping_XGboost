#! /bin/bash

# # Seperate the bands & generate mosaic seperately
bands=(B02 B03 B04 B05 B06 B07 B08 B11 B12 B8A)

rm -Rf ../features/mosaics
mkdir ../features/mosaics

for band in ${bands[@]};
do

echo ${band};
find ../data/S2GM_Q10_20200701_20200930_Esti_new_STD_v1.3.0_1500454/ -name "${band}*.tiff" >tmpfile.txt;
gdalbuildvrt -input_file_list tmpfile.txt ${band}_ee.vrt;
gdalwarp -r cubic -s_srs EPSG:4326 -t_srs EPSG:3301 -tr 10 10 -of gtiff -co BIGTIFF=YES -co COMPRESS=LZW -multi -wo NUM_THREADS=45 ${band}_ee.vrt ../features/mosaics/${band}_ee.tif

done;

rm -f tmpfile.*;
rm -f *.vrt;


# Stack all the generated bands together 
gdalbuildvrt -separate ../features/mosaics/all_bands_ee.vrt ../features/mosaics/*.tif ;
gdal_translate ../features/mosaics/all_bands_ee.vrt -tr 10 10 -of gtiff -co BIGTIFF=YES -co COMPRESS=LZW --config GDAL_CACHEMAX 20000 ../features/mosaics/all_bands_ee.tif


