#!/usr/bin/env python
# -*- coding: utf-8 -*-

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
from rasterio.merge import merge
from rasterio.plot import show
import rasterio.features
from shapely.geometry import box
import gdal
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import os

# Obtener la fecha actual
fecha_actual = datetime.now()

# Calcular el mes anterior
primer_dia_mes_actual = fecha_actual.replace(day=1)
#mes_anterior = primer_dia_mes_actual - relativedelta(months=1)
mes_anterior = primer_dia_mes_actual - timedelta(days=1)
anio = mes_anterior.year
mes = mes_anterior.month

# Lista de periodos de predicción
periodos = [1, 3, 6, 9, 12]

for periodo_num in periodos:
    # Ajustar las variables según el periodo y la fecha 
    nombre_a = f"{anio}_{mes:02d}_{periodo_num:02d}"
    nameJpeg = f"MON-SEQ_{periodo_num:02d}.jpeg"
    if periodo_num == 1:
        periodo_str = "1 mes"
        nameJpeg = f"MON-SEQ_{periodo_num:02d}_sin_brasil.jpeg"
    else:
        periodo_str = f"{periodo_num} meses"
    raster_path = "/var/sequia_reg/REG/tif/"+f"{nombre_a}.tif"

    # Aquí puedes agregar cualquier otra lógica relacionada con el periodo, si es necesario

    # Resto del código que utiliza las variables ajustadas
    # ----------------------------------------------------

    # Por simplicidad, supondré que no necesitas fusionar archivos TIFF adicionales
    # y que el archivo raster_path ya existe y está listo para ser procesado

    # Cargar el archivo TIFF
    rrqpeDat = rasterio.open(raster_path)

    rrqpeTmp = rrqpeDat.read(1)  # Carga la información del TIFF
    rrqpeTmp = rrqpeTmp[::-1]
    rrqpeTmp = np.ma.array(rrqpeTmp, mask=(rrqpeTmp < 0))

    latIni = rrqpeDat.bounds.bottom
    latFin = rrqpeDat.bounds.top
    lonIni = rrqpeDat.bounds.left
    lonFin = rrqpeDat.bounds.right

    py1, px1 = rrqpeDat.index(lonIni, latIni)
    py2, px2 = rrqpeDat.index(lonFin, latFin)
    nx = px2 - px1
    ny = py1 - py2
    dis = (lonFin - lonIni) / float(nx)

    grid_lon = np.linspace(lonIni, lonFin, nx)
    grid_lat = np.linspace(latIni, latFin, ny)
    xintrp, yintrp = np.meshgrid(grid_lon, grid_lat)

    rrqpe = rrqpeTmp[py2:py1, px1:px2]

    fig = plt.figure(figsize=(10.4, 8.6))
    ax = fig.add_subplot(1, 1, 1)

    lstColors = ['#00000000', '#fffe00', '#fdd37f', '#ffaa00', '#fe0002', '#710100', '#710100']
    rgba_colors = lstColors

    lstIntervals = [0, 1, 2, 3, 4, 5, 6]  # Ajusta según tus intervalos
    cCmap = clr.ListedColormap(rgba_colors)  # Aplica la transparencia
    cNorm = mpl.colors.BoundaryNorm(lstIntervals, cCmap.N)

    print(latIni, " ", latFin, " ", lonIni, " ", lonFin)
    m = Basemap(projection='cyl', llcrnrlat=-57.375, urcrnrlat=12.375,
                llcrnrlon=-83, urcrnrlon=-33, lat_ts=7, resolution='i')

    # Cargar el shapefile (asegúrate de que la ruta es correcta)
    m.readshapefile('/var/py/volunclima/monitor/shapefile_brasil/Paises_OSABrasil',
                    'map_shapes', drawbounds=3, color='black', default_encoding='latin-1')

    # Rutas de los archivos de imagen
    png_input_path = "mapa.png"
    cropped_png_output_path = "mapa_crop.png"

    widthOfContainerElement = 10800
    heightOfContainerElement = 5400

    lonIni_img = 2909
    lonFin_img = 4420
    latIni_img = 4424
    latFin_img = 2326
    background_extent = (lonIni_img, lonFin_img, latIni_img, latFin_img)

    # Coordenadas de la región que deseas mantener (ajusta según tus necesidades)
    crop_box = (lonIni_img, latFin_img, lonFin_img, latIni_img)

    # Cargar y recortar la imagen PNG
    image = Image.open(png_input_path)
    cropped_image = image.crop(crop_box)
    cropped_image.save(cropped_png_output_path)

    png_background = "mapa_crop.png"
    background_img = plt.imread(png_background)

    # Dibujar el fondo con la imagen PNG
    m.imshow(background_img, origin='upper')

    xx, yy = m(xintrp, yintrp)
    grafica = m.pcolormesh(xx, yy, rrqpe, cmap=cCmap, norm=cNorm)

    lstIntervalsLbls = ['Sequía excepcional', 'Sequía extrema', 'Sequía severa',
                        'Sequía moderada', 'Anormalmente seco', 'Normal']
    custom_lines = [
        mpl.lines.Line2D([0], [0], color=lstColors[5], lw=5),
        mpl.lines.Line2D([0], [0], color=lstColors[4], lw=5),
        mpl.lines.Line2D([0], [0], color=lstColors[3], lw=5),
        mpl.lines.Line2D([0], [0], color=lstColors[2], lw=5),
        mpl.lines.Line2D([0], [0], color=lstColors[1], lw=5),
        mpl.lines.Line2D([0], [0], color=lstColors[0], lw=5)
    ]

    # Puedes activar la leyenda si lo deseas
    # plt.legend(bbox_to_anchor=(1,1), loc="upper left",handles=custom_lines, labels=lstIntervalsLbls,title="   Intensidad de sequía   ",title_fontsize='large',fontsize='medium')

    plt.title(f"\nMonitor de sequía Sudamérica: {periodo_str}\n Periodo: {nombre_a}")
    plt.draw()
    output_image = f"auxiliard_{periodo_num:02d}.png"
    fig.savefig(output_image, format='png', dpi=120)
    plt.close()
    subprocess.call(["/usr/local/bin/convert", output_image, "-trim", nameJpeg])
    subprocess.call(["cp", nameJpeg, "/var/py/volunclima/monitor/salidas"])
    # Borrar el archivo auxiliard.png después de usarlo
    if os.path.exists(output_image):
        os.remove(output_image)
    print(f"Generado {nameJpeg} para el periodo {periodo_str}")
