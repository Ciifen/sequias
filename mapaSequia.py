#!/usr/bin/env python
import numpy as np
import rasterio
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.colors as clr
from mpl_toolkits.basemap import Basemap
import sys
import subprocess
from osgeo import osr
from osgeo import ogr
from PIL import Image
import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import rasterio.features
from shapely.geometry import box
import gdal

nombre_a= "2023_12_01"
periodo="1 mes"
raster_path = nombre_a+".tif"
raster_path2 = "dezembro2023.tif"

shapefile = "/var/py/volunclima/monitor/dezembro2023/dezembro23.shp"

def shp_to_geotiff(input_shp, output_geotiff):
    # Registrar los formatos de datos
    gdal.AllRegister()

    # Abrir el archivo Shapefile
    driver = ogr.GetDriverByName('ESRI Shapefile')
    shp_dataset = driver.Open(input_shp, 0)  # 0 indica solo lectura

    if shp_dataset is None:
        print('No se pudo abrir el archivo Shapefile.')
        return
    print(shp_dataset)
    # Obtener la capa del Shapefile
    layer = shp_dataset.GetLayer()

    # Obtener la extensión espacial de la capa
    extent = layer.GetExtent()


    # Imprimir atributos
    layer.ResetReading()  # Asegurar que estamos al principio de la capa
    feature = layer.GetNextFeature()
    while feature:
        attributes = feature.items()
        print(attributes)
        feature = layer.GetNextFeature()
    # Crear el archivo GeoTIFF
    driver = gdal.GetDriverByName('GTiff')
    geotiff_dataset = driver.Create(output_geotiff, int((extent[1] - extent[0]) / 0.01), int((extent[3] - extent[2]) / 0.01), 1, gdal.GDT_Byte)

    # Definir la proyección del GeoTIFF
    geotiff_dataset.SetProjection(layer.GetSpatialRef().ExportToWkt())

    # Definir la transformación afín
    geotiff_dataset.SetGeoTransform((extent[0], 0.01, 0, extent[3], 0, -0.01))

    # Crear una banda en el GeoTIFF
    band = geotiff_dataset.GetRasterBand(1)
    band.SetNoDataValue(255)  # Valor sin datos

    # Rasterizar la capa del Shapefile en el GeoTIFF
    gdal.RasterizeLayer(geotiff_dataset, [1], layer, options=["ATTRIBUTE=Valor"])
    # Imprimir atributos
    geotiff_dataset.FlushCache()
    del geotiff_dataset

    # Cerrar los datasets
    shp_dataset = None
    geotiff_dataset = None

    print('Conversión completa.')

shp_to_geotiff(shapefile,raster_path2)




def merge_geotiffs(tiff1_path, tiff2_path, output_path):
    # Abrir los archivos GeoTIFF
    with rasterio.open(tiff1_path) as tiff1:
        with rasterio.open(tiff2_path) as tiff2:
            # Fusionar los archivos GeoTIFF
            merged_datasets, out_transform = merge([tiff1, tiff2])

            # Copiar las metadatos de uno de los archivos (usaremos tiff1)
            out_meta = tiff1.meta.copy()
            out_meta.update({
                "driver": "GTiff",
                "height": merged_datasets.shape[1],
                "width": merged_datasets.shape[2],
                "transform": out_transform
            })

            # Crear el archivo GeoTIFF combinado
            with rasterio.open(output_path, "w", **out_meta) as dest:
                dest.write(merged_datasets)


            
output_path = "output.tif"
merge_geotiffs(raster_path, raster_path2, output_path)

#nameTif = "/var/py/castehr/data/indices/mon/tif/"+sys.argv[1]+".tif"

rrqpeDat = rasterio.open(output_path)





rrqpeTmp = rrqpeDat.read(1) #carga la info del tif
rrqpeTmp = rrqpeTmp[::-1]
rrqpeTmp = np.ma.array(rrqpeTmp,mask=(rrqpeTmp < 0))

latIni = rrqpeDat.bounds.bottom
latFin = rrqpeDat.bounds.top
lonIni = rrqpeDat.bounds.left
lonFin = rrqpeDat.bounds.right

py1, px1 = rrqpeDat.index(lonIni,latIni)
py2, px2 = rrqpeDat.index(lonFin,latFin)
nx = px2 - px1
ny = py1 - py2
dis = (lonFin - lonIni) / float(nx)

grid_lon = np.linspace(lonIni, lonFin, nx)
grid_lat = np.linspace(latIni, latFin, ny)
xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

rrqpe = rrqpeTmp[py2:py1,px1:px2]

fig = plt.figure(figsize=(10.4,8.6))
#fig.subplots_adjust(wspace=0.01, hspace=0.01,bottom=0.01, top=0.90, left=0.008, right=0.995)
ax = fig.add_subplot(1,1,1)
#print(rrqpe.data.max())
lstColors = ['#00000000','#fffe00','#fdd37f','#ffaa00','#fe0002','#710100','#710100'] 
#rgba_colors = [clr.to_rgba(color, alpha=0.6) for color in lstColors]
rgba_colors = lstColors

lstIntervals = [0,1,2,3,4,5,6]  # Ajusta según tus intervalos
cCmap = clr.ListedColormap(rgba_colors)  # Aplica la transparencia
cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)

print(latIni," ",latFin," ",lonIni," ",lonFin)
m = Basemap(projection='cyl',llcrnrlat=-57.375,urcrnrlat=12.375,llcrnrlon=-83,urcrnrlon=-33,lat_ts=7,resolution='i')#aqui cambio
()

###este archivo pesa mucho para subirlo al repositorio. hay que subirlo a un drive o algo así.
m.readshapefile('/var/py/volunclima/monitor/shapefile_brasil/Paises_OSABrasil','map_shapes',drawbounds=3, color='black', default_encoding='latin-1')

#en caso de no disponer del shapefile de los paises de sequia, comentar la linea de arriba y descomentar las de abajo
#m.drawcoastlines(linewidth=0.2)
#m.drawcountries(linewidth=0.5)


# Rutas de los archivos
png_input_path = "mapa.png"
cropped_png_output_path = "mapa_crop.png"

widthOfContainerElement=10800
heightOfContainerElement=5400
""" lonIni=(98.625*widthOfContainerElement)/360
lonFin=(122.625*widthOfContainerElement)/360
latIni=(102.375*heightOfContainerElement)/180
latFin=(61.625*heightOfContainerElement)/180 """

lonIni=2909#aqui cambio
lonFin=4420
latIni=4424
latFin=2326
background_extent = (lonIni, lonFin, latIni, latFin)

# Coordenadas de la región que deseas mantener (ajusta según tus necesidades)
crop_box = (lonIni, latFin, lonFin, latIni)

# Cargar la imagen PNG
image = Image.open(png_input_path)

# Recortar la imagen según las coordenadas especificadas
cropped_image = image.crop(crop_box)

# Guardar la imagen recortada
cropped_image.save(cropped_png_output_path)


png_background = "mapa_crop.png"
# Cargar la imagen PNG de fondo
background_img = plt.imread(png_background)
# Configurar las coordenadas de la imagen PNG



# Dibujar el fondo con la imagen PNG
m.imshow(background_img, origin='upper')
#

xx, yy = m(xintrp,yintrp)
grafica = m.pcolormesh(xx,yy,rrqpe, cmap = cCmap, norm=cNorm)
#grafica = m.contourf(xx, yy, rrqpe, cmap=cCmap, norm=cNorm, antialiased=True, levels = 6)
lstIntervalsLbls = ['Sequía excepcional','Sequía extrema','Sequía severa','Sequía moderada','Anormalmente seco','Normal']
custom_lines = [
			mpl.lines.Line2D([0], [0], color=lstColors[5], lw=5),
			mpl.lines.Line2D([0], [0], color=lstColors[4], lw=5),
			mpl.lines.Line2D([0], [0], color=lstColors[3], lw=5),
			mpl.lines.Line2D([0], [0], color=lstColors[2], lw=5),
			mpl.lines.Line2D([0], [0], color=lstColors[1], lw=5),
			mpl.lines.Line2D([0], [0], color=lstColors[0], lw=5)]
plt.legend(bbox_to_anchor=(1,1), loc="upper left",handles=custom_lines, labels=lstIntervalsLbls,title="   Intensidad de sequía   ",title_fontsize='large',fontsize='medium')

plt.title("\nMonitor de sequía Sudamérica: "+periodo+"\n Periodo: "+nombre_a)
plt.draw()
namePng = "osa_"+nombre_a+".png"
fig.savefig("auxiliard.png",format='png',dpi=120)
plt.close()
subprocess.call(["/usr/local/bin/convert","auxiliard.png","-trim",namePng])
subprocess.call(["cp",namePng,"/var/py/volunclima/monitor"])
