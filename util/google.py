import urllib2
import json

def get_location(latitudade, longitude):

    url = "http://maps.googleapis.com/maps/api/geocode/json?latlng={},{}&sensor=false".format(latitudade, longitude)

    response = urllib2.urlopen(url)
    html = response.read()
    data = json.loads(html)

    if 'status' in data and data['status'] == 'OK':

        location = {}

        for i in data['results'][0]['address_components']:
            if 'administrative_area_level_2' in i['types']:
                location['city'] = i['long_name']
            elif 'administrative_area_level_1' in i['types']:
                location['state'] = i['short_name']
                location['state_name'] = i['long_name']
            elif 'country' in i['types']:
                location['country'] = i['long_name']
            elif 'sublocality_level_1' in i['types']:
                location['district'] = i['long_name']
            elif 'route' in i['types']:
                location['route'] = i['long_name']
            elif 'street_number' in i['types']:
                location['number'] = i['long_name']
            elif 'postal_code' in i['types']:
                location['cep'] = i['long_name']


        if 'formatted_address' in data['results'][0]:
            location['address'] = data['results'][0]['formatted_address']


    return location


