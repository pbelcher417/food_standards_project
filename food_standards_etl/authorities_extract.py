import requests
import pandas as pd
import json
import xml.etree.ElementTree as ET

# Base URL for the API
BASE_URL = 'https://api.ratings.food.gov.uk/'

# Headers including the API key for authorization
headers = {
    'x-api-version': '2',  # Version 2 of the API
    'accept': 'application/json'
}

# Endpoint to get local authority data
endpoint = 'Authorities'

#Function to return authority data
def get_authorities():
    try:
        response = requests.get(BASE_URL + endpoint, headers=headers)
        
        # Check if the request was successful
        if response.status_code == 200:
            authorities = response.json()  # Convert response to JSON
            return authorities
        else:
            print(f"Failed to retrieve data: {response.status_code}")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
        

def parse_establishment(element):
    establishments = []
    for est in element:
        est_data = {child.tag: child.text for child in est}
        
        # Flatten Geocode
        geocode = est.find('Geocode')
        if geocode is not None:
            est_data['Longitude'] = geocode.findtext('Longitude')
            est_data['Latitude'] = geocode.findtext('Latitude')
        
        establishments.append(est_data)
    return establishments 

def xml_to_df(xml_url):

    response = requests.get(xml_url)
    xml_data = response.content
    
    root = ET.ElementTree(ET.fromstring(xml_data)).getroot()
    # Parse the XML data from the EstablishmentCollection
    records = parse_establishment(root.find('EstablishmentCollection'))

    return records

if __name__ == '__main__':
    for authority in authority_data['authorities']:
        #print(authority['FileName']
        result = xml_to_df(authority['FileName'])
    
        results.extend(result)
    
    df = pd.DataFrame(results)