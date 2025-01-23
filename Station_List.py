import numpy as np
import pandas as pd
import geopandas as gpd
import datetime
import time
import requests
import json
from shapely import Point
import urllib.parse

#remove on github upload
MAPBOX_API_KEY = None #insert API key here

class Station_List:
    def __init__(self,cached=False):
        self.postal_codes = pd.read_csv('FSACodes_GTA.csv')['FSA'].tolist() #don't need this
        self.address_count = 1 #used for output filenames for debugging
        if(cached==False):
            self.update_cache()
        self.stations_df = pd.merge(self.get_stations_info(),self.get_stations_status(),on="station_id")
        self.stations_gdf = gpd.GeoDataFrame(self.stations_df, geometry=gpd.points_from_xy(self.stations_df['lon'], self.stations_df['lat']))
        self.current_query_json = None
        #TODO: self.lastUpdate = right.now (use datetime)
    #! Utility Functions !#
    def get_stations_info(self):
        with open('stations_info.json') as f:
            r_json = json.load(f)
        return pd.DataFrame(r_json['data']['stations'])[['station_id', 'name', 'lat', 'lon','address','post_code']].astype({
            'station_id': 'string',
        })
    def get_stations_status(self):
        with open('stations_status.json') as f:
            r_json = json.load(f)
        return pd.DataFrame(r_json['data']['stations'])[['station_id', 'num_bikes_available', 'num_docks_available','num_docks_disabled','status']].astype({
            'station_id': 'string',
        })
    def update_stations(self):
        #update stations with realtime data by calling the status ones again.
        updated_df = pd.merge(self.stations_info_df,get_stations_status(),on="station_id")
        #self.lastUpdate = right.now
        return updated_df
    
    def update_cache(self):
        self.save_request('https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_status.json','stations_status.json')
        self.save_request('https://tor.publicbikesystem.net/ube/gbfs/v1/en/station_information','stations_info.json')

    def save_request(self,url,filename):
        r = requests.get(url)
        r_json = json.loads(r.content)
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(r_json, f, ensure_ascii=False, indent=4)

    #! Query Functions !#
    def find_nearest_station_id(self,lat,long):
        # Searches for nearest station based on lat, long 
        # returns station id of nearest station.
        # Create a GeoDataFrame for the input coordinates
        input_point = gpd.GeoDataFrame(
            geometry=[Point(long, lat)], 
            crs=self.stations_gdf.crs
        )
        # Calculate distances and find the nearest station
        self.stations_gdf['distance'] = self.stations_gdf.geometry.distance(input_point.iloc[0].geometry)
        nearest_station = self.stations_gdf.loc[self.stations_gdf['distance'].idxmin()]
        #in final release fix this to be more user friendly 
        print("Stations_List.find_nearest_station_id: Nearest Station is: ",nearest_station['name'],"id:",nearest_station['station_id'])
        return nearest_station['station_id']
    
    def query_address(self,address):
        address.replace(' ', '%20')
        """
        Takes an address and returns the latitude and longitude coordinates.
        """
        url = 'https://api.mapbox.com/search/geocode/v6/forward?'
        params = {
            'q': address,
            'country': 'ca',
            'format': 'json',
            'type': 'address',
            'language': 'en',
            'region': 'CA-ON',
            'bbox': '-79.72438336908286,43.58464103518415,-79.0036031215346,43.84985154043082',
            'access_token': MAPBOX_API_KEY
        }
        response = requests.get(url, params=params)
        #print(url+urllib.parse.urlencode(params))
        try:
            data = response.json()
        except:
            data = None
            print("API request failed")
        if data:
            with open('output/out_data_address_'+str(self.address_count)+'.json', 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
                self.address_count+=1
            self.current_query_json = data
            return self.get_address_list_string() #return string of list of addresses
        else:
            return None
        
    def return_address(self,index): 
        data = self.current_query_json
        try:
            lat = data['features'][index]['coordinates']['latitude']
            lon = data['features'][index]['coordinates']['longitude']
            return ((float(lat), float(lon)), data['features'][index]['full_address'])
        except: 
            print("There are no more address")
            self.current_query_json = None
            return (None,None)
        
    
    def get_address_list_string(self):
        list_string = "List of Addresses found \n"
        for i in range(0,self.get_max_index()):
            list_string += str(i+1) +". "+self.return_address(i)[1] +"\n"
        return list_string


    def google_url(self,id1,id2):
        id1_coords = self.id_to_coord(id1)
        id2_coords = self.id_to_coord(id2)        
        #generate google maps url
        url = 'https://www.google.com/maps/dir/?'
        params = {
            'api': 1,
            'origin': str(id1_coords[0])+','+str(id1_coords[1]),
            'destination': str(id2_coords[0])+','+str(id2_coords[1]),
            'travelmode': 'bicycling'
        }
        return(url+urllib.parse.urlencode(params))
    
    def id_to_coord(self,id):
        return self.stations_df.iloc[np.where(self.stations_df.station_id==id)].values[0][2:4]
    def reset_query_data(self):
        self.current_query_json = None
    def get_max_index(self):
        return len(self.current_query_json['features'])
    
