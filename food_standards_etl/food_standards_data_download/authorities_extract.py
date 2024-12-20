import requests
import pandas as pd
import json
import xml.etree.ElementTree as ET
from google.cloud import storage
import os

def upload_to_gcs(bucket_name: str, source_file_name: str, destination_blob_name: str):
    """Uploads a file to from a local filepath to a blob on a defined GCS bucket

    Args:
        bucket_name (str): Name of the GCS Bucket
        source_file_name (str): Source file name to upload
        destination_blob_name (str): Name of the blob to be saved to
    """
    
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

   # Create a new blob (file object) and upload the file’s content
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)

    print(f"File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.")

#Function to return authority data
def get_authorities(base_url: str, endpoint: str, headers: str):
    """Makes an API request with associated endpoint and headers and returnes the JSON response

    Args:
        base_url (str): URL of the API
        endpoint (str): API Endpoint
        headers (str): Headers to be added to API request

    Returns:
        _type_: JSON object containing the returned JSON response
    """
    try:
        response = requests.get(base_url + endpoint, headers=headers)
        
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
    """Flattens returned JSON to find the geocode co-ordinats

    Args:
        element (_type_): XML to be flattened

    Returns:
        _type_: Flattened list
    """
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

def xml_to_list(xml_url: str):
    """Converts a flattened XML to a Python list

    Args:
        xml_url (str): URL Of XML to access

    Returns:
        _type_: Python list object of flattened XML
    """

    response = requests.get(xml_url)
    xml_data = response.content
    
    root = ET.ElementTree(ET.fromstring(xml_data)).getroot()

    # Parse the XML data from the EstablishmentCollection
    records = parse_establishment(root.find('EstablishmentCollection'))

    return records

if __name__ == '__main__':

    # Base URL for the API
    base_url = 'https://api.ratings.food.gov.uk/'

    # Headers including the API key for authorization
    headers = {
        'x-api-version': '2',  # Version 2 of the API
        'accept': 'application/json'
    }

    # Endpoint to get local authority data
    endpoint = 'Authorities'

    authority_data = get_authorities(base_url, endpoint, headers)

    results = []

    #Loop over 
    for authority in authority_data['authorities']:
        #print(authority['FileName']
        result = xml_to_list(authority['FileName'])
    
        results.extend(result)
    
    df = pd.DataFrame(results)

    df.to_parquet("food_standards_data.parquet")

    upload_to_gcs("food-standards-data", "food_standards_data.parquet", "food_standards_extract.parquet")
