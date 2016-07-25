import matplotlib
matplotlib.use('TkAgg')
import requests, sys, time
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


# Retrieve station's lat/lon
def fetch_latlon():
    url = 'http://qiita.com/butchi_y/items/3a6b70b38e13dc56ef13'
    data = pd.read_html(url)[0]
    data.columns = ['name', 'lat', 'lon']
    return data

# Retrieve the number of passenger
def fetch_passenger():
    # fetch data
    urls = ['http://www.jreast.co.jp/passenger/index.html', 'http://www.jreast.co.jp/passenger/2014_01.html']
    data = pd.DataFrame()
    for url in urls:
        df = None
        for i in range(5):
            try:
                df = pd.read_html(url)
                break
            except IncompleteRead as ir:
                time.sleep(0.1)
        # Sometimes fetching passenger fails
        if df is None:
            print('Failed to fetch passenger.')
            sys.exit(1)

        for i in range(2):
            # Delete rank column in the first table
            if url == urls[0]:
                df[i] = df[i].iloc[:, 1:]
                df[i].columns = [col for col in range(len(df[i].columns))]
            data = data.append(df[i])
    # arrange data
    data = data.iloc[2:, [0, 3]]
    data.columns = ['name', 'passenger']
    data.reset_index(inplace=True, drop=True)
    return data

# Retrieve lat/lon and passenger info and merge them into one data
def fetch_data():
    latlon = fetch_latlon()
    passenger = fetch_passenger()
    data = latlon.merge(passenger, how='inner', on='name')
    return data

# Retrive static OpenStreetMap
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


# main processing
def main__():
    data = fetch_data()
    fig = plt.figure(figsize=(15, 15))

    # minlat, minlon, maxlat, maxlon = 35.61, 139.67, 35.75, 139.80
    minlat, minlon, maxlat, maxlon = 35.68, 139.75, 35.75, 139.78
    bmap = Basemap(projection='merc', llcrnrlat=minlat, urcrnrlat=maxlat, llcrnrlon=minlon, urcrnrlon=maxlon, lat_ts=0,
                   resolution='l')

    x, y = bmap(data['lon'].values, data['lat'].values)

    file_name = 'osm.png'
    bg_img = None

    try:
        bg_img = Image.open(file_name)
    except FileNotFoundError as fnfe:
        bg_img = get_osm_img(minlat=minlat, minlon=minlon, maxlat=maxlat, maxlon=maxlon, scale=12000)
        bg_img.save(file_name)

    bmap.imshow(bg_img, origin='upper')
    bmap.scatter(x, y,
                 c=data['passenger'],
                 cmap=plt.cm.get_cmap('seismic'),
                 alpha=0.5,
                 s=data['passenger'].map(
                     lambda x: (x - data['passenger'].min()) / (data['passenger'].max() - data['passenger'].min()) * (MAX_SIZE - MIN_SIZE) + MIN_SIZE))

    plt.colorbar()
    plt.show()
    # fig.show()
    # plt.savefig('out.png')


def csv_loader():
    data = pd.read_csv('data.csv')
    result = {}
    result['lat'] = data['real latitute']
    result['lon'] = data['real longtitute']
    result['passenger'] = data['time']
    return result


def mapping_gps_data():
    fig = plt.figure(figsize=(15, 15))
    data = csv_loader()

    print(min(data['lat']))
    print(max(data['lat']))
    print(min(data['lon']))
    print(max(data['lon']))

    minlat, minlon, maxlat, maxlon = 35.01, 135.74, 35.02, 135.77
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