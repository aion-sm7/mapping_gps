import matplotlib
matplotlib.use('TkAgg')
import requests
import sys
import time
from io import BytesIO
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from PIL import Image
import pandas as pd
from http.client import IncompleteRead

# constants
# min/max circle size of plot
MIN_SIZE = 20
MAX_SIZE = 200


# get OpenStreetMap image
def get_osm_img(minlat, minlon, maxlat, maxlon, scale=60000, img_format='png'):
    url = 'http://www.openstreetmap.org/export/finish'
    payload = {
        'mapnik_format': img_format,
        'mapnik_scale': scale,
        'minlon': minlon,
        'minlat': minlat,
        'maxlon': maxlon,
        'maxlat': maxlat,
        'format': 'mapnik'
    }
    response = requests.post(url, payload)
    return Image.open(BytesIO(response.content))


# load arduino GPS row txt data
# and return formatted data
def load_txt():
    col_names = ['c{0:02d}'.format(i) for i in range(50)]
    data = pd.read_csv('DATAGPS.TXT', names=col_names)
    data = data[data.c00 == '$GPGGA']
    data.columns = ['id', 'time', 'longitude', 'NorS', 'latitude', 'EorW'] + col_names[6:]
    # print(data.head(4))
    # print(data.latitude.apply(lambda x: x.split('.')[0][:-2] + '.' + str(float(x.split('.')[0][-2:])/60 + float(x.split('.')[1])/60)).head(5))
    # print(data.latitude.apply(lambda x: x.split('.')[0][:-2]).head(5))
    # print(data.latitude.apply(lambda x: float(x.split('.')[0][:-2]) + float(x.split('.')[0][-2:] + "." + x.split('.')[1])/60).head(5))
    data.latitude = data.latitude.apply(
        lambda x: float(x.split('.')[0][:-2]) + float(x.split('.')[0][-2:] + "." + x.split('.')[1]) / 60)
    # print(data.head(5))
    data.longitude = data.longitude.apply(
        lambda x: float(x.split('.')[0][:-2]) + float(x.split('.')[0][-2:] + "." + x.split('.')[1]) / 60)
    # print(data.head(5))
    data.time = data.time.apply(
        lambda x: float(x))
    # print(min(data.latitude))
    # print(max(data.latitude))
    result = {
        'lat': data.latitude,
        'lon': data.longitude,
        'passenger': data.time
    }
    return result


# main mapping function
def mapping_gps_data():
    fig = plt.figure(figsize=(15, 15))
    data = load_txt()

    print(min(data['passenger']))
    print(max(data['passenger']))
    print(min(data['lat']))
    print(max(data['lat']))
    print(min(data['lon']))
    print(max(data['lon']))

    minlat, minlon, maxlat, maxlon = 35.01, 135.75, 35.02, 135.76
    bmap = Basemap(projection='merc', llcrnrlat=minlat, urcrnrlat=maxlat, llcrnrlon=minlon, urcrnrlon=maxlon, lat_ts=0, resolution='l')
    x, y = bmap(data['lat'].values, data['lon'].values)

    file_name = 'osm_new.png'

    bg_img = None
    bg_img = get_osm_img(minlat=minlat, minlon=minlon, maxlat=maxlat, maxlon=maxlon, scale=12000)
    # try:
    #     bg_img = Image.open(file_name)
    # except FileNotFoundError as fnfe:
    #     bg_img = get_osm_img(minlat=minlat, minlon=minlon, maxlat=maxlat, maxlon=maxlon, scale=12000)
    #     bg_img.save(file_name)

    bmap.imshow(bg_img, origin='upper')
    bmap.scatter(x, y,
                 c=data['passenger'],
                 cmap=plt.cm.get_cmap('seismic'),
                 alpha=0.5,
                 s=data['passenger'].map(
                     lambda x: (x - data['passenger'].min()) / (data['passenger'].max() - data['passenger'].min()) * (MAX_SIZE - MIN_SIZE) + MIN_SIZE)
                 )
    # bmap.scatter(x, y, c='r', marker='o', s=80, alpha=1.0)

    plt.colorbar()
    plt.xlabel('Latitude')
    plt.ylabel('Longitude')
    plt.savefig('plotted.png', dpi=300)
    print('plot started')
    plt.show()


def main():
    mapping_gps_data()

main()