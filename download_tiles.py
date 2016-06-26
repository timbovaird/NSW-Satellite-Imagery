"""
Download NSW satellite images for a specified region and a specified zoom level.

Utilises the Satellite imagery API from the NSW LPI
http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer
To Do:
- convert longitude / latitude and zoom level to to tile z/x/y
"""
from collections import namedtuple
import json
import neobunch
import png
import requests
import shutil
from pprint import pprint


def main(parameters):
    """Download all images for the specified region and zoom level."""
    metadata = get_metadata(parameters)
    # pprint(metadata)
    image_api = NswSatelliteImages(parameters, metadata)
    print('Zoom level:', image_api.zoom_level,
          'Resolution:', image_api.resolution,
          'Scale:', image_api.scale)
    image_api.download_tile(xtile=39000, ytile=60000)


def get_metadata(parameters):
    """Get metadata from local json file (from http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer?f=pjson)."""
    with open('MapServer.json') as data_file:
        data = json.load(data_file)
    # Objectorize data
    metadata = neobunch.bunchify(data)
    return metadata


class NswSatelliteImages:
    """Initalise connection to the API for a specified region and zoom level."""

    def __init__(self, parameters, metadata):
        """Prepare connection to API."""
        self.zoom_level = parameters.zoom_level
        self.latitude_bounds = parameters.latitude_bounds
        self.longitude_bounds = parameters.longitude_bounds
        self.num_tiles_saved = 0
        self.set_tile_parameters(metadata)

    def set_tile_parameters(self, metadata):
        """Setup tile data for zoom level."""
        tile_info = metadata.tileInfo.lods[self.zoom_level]
        self.scale = tile_info.scale
        self.resolution = tile_info.resolution
        self.cols = metadata.tileInfo.cols
        self.rows = metadata.tileInfo.rows
        Extent = namedtuple('Extent', 'x y')  # fullExtent or #initialExtent?
        self.extent = Extent(x=(metadata.fullExtent.xmin, metadata.fullExtent.xmax),
                             y=(metadata.fullExtent.ymin, metadata.fullExtent.ymax))
        self.mapname = metadata.mapName

    def calculate_min_max_tiles(self):
        """Calculate the extreme value tiles.

        Given a zoom level and longitude and latitude limits, calculate the
        upper-left and lower-right tiles in the APIs Z/X/Y format.
        """

    def download_tile(self, xtile, ytile):
        """Download an individual tile."""
        location = 'http://maps.six.nsw.gov.au/arcgis/rest/services/public/NSW_Imagery/MapServer/tile/'
        destination = 'downloaded_tiles/'
        save_name = str(self.zoom_level) + '_' + str(xtile) + '_' + str(ytile)
        tile_url = location + save_name.replace('_', '/')
        tile = requests.get(tile_url, stream=True)
        with open(destination + save_name + '.png', 'wb') as out_file:
            tile.raw.decode_content = True
            shutil.copyfileobj(tile.raw, out_file)
            tilepng = png.Reader(file=tile.raw)
            # shutil.copyfileobj(tilepng, out_file)
        del tile


if __name__ == '__main__':
    # Set parameters
    Parameters = namedtuple('Parameters', 'zoom_level latitude_bounds longitude_bounds')
    parameters = Parameters(zoom_level=16,
                            latitude_bounds=(-35.258028, -35.333125),  # Canberra CBD
                            longitude_bounds=(149.085308, 149.175259))  # Canberra CBD
    main(parameters)
