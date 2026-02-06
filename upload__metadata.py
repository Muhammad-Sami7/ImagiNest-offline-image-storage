import json
import requests

# CouchDB connection info
COUCHDB_URL = 'http://127.0.0.1:5984'
DB_NAME = 'database name' #replace this with your database name
USERNAME = 'user_name' #replace this with your user name
PASSWORD = 'password' #replace this with your user password

# Load the original file
with open("C:/Users/User/Desktop/DATA WAREHOUSE/metadata.json", "r") as f: 

    original_data = json.load(f)

# Wrap each metadata group into a CouchDB document
docs = [
    {
        "_id": "metadata_image_types",
        "type": "image_types",
        "data": original_data["image_types"]
    },
    {
        "_id": "metadata_image_resolutions",
        "type": "image_resolutions",
        "data": original_data["image_resolutions"]
    },
    {
        "_id": "metadata_image_classes",
        "type": "image_classes",
        "data": original_data["image_classes"]
    }
]

# Bulk upload the documents
response = requests.post(
    f"{COUCHDB_URL}/{DB_NAME}/_bulk_docs",
    auth=(USERNAME, PASSWORD),
    headers={"Content-Type": "application/json"},
    json={"docs": docs}
)

# Print response
print("Upload status:", response.status_code)
print("Result:", response.json())
