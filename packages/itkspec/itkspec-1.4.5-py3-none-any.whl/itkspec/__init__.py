import itkdb
from fastapi import HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import json
import requests
import csv
from io import StringIO

__version__ = "1.4.5"

#################
### FUNCTIONS ###
#################

#### authenticate user
def create_client(accessCode1: str, accessCode2: str):
    user = itkdb.core.User(access_code1=accessCode1, access_code2=accessCode2)
    try:
        user.authenticate()
    except Exception as e:
        print(e)
        raise HTTPException(status_code=401, detail="Authentication failed")
    return {"accessCode1": accessCode1, "accessCode2": accessCode2}

### get single spec
def retrieve_spec(client, data: Dict[str, str]):
    url = "https://key-version-tester.app.cern.ch/spec"
    json = {**client, **data} #includes verified access codes
    
    response = requests.post(url, json=json)
    try:
        data = response.json()
        print(data)
    except ValueError:
        print("Response is not valid JSON:")
        print(response.text)

### get multiple specs
def retrieve_specList(client, data):
    url = "https://key-version-tester.app.cern.ch/speclist"
    json = {**client, **data} #includes verified access codes

    response = requests.post(url, json=json)
    print(response.json())

### api help
def api_help():
    url = "https://key-version-tester.app.cern.ch/help"
    response = requests.get(url)
    print(response.text)

### server check
def health_check():
    url = "https://key-version-tester.app.cern.ch/health"
    response = requests.get(url)
    print(response.text)

### help
def help():
    help_text = """These are the functions available:
    1. authenticate_user - returns a client if the user is verified
    2. retrieve_spec - Get specification for a single parameter
    3. retrieve_specList - Get specifications for multiple parameters
    4. api_help - List the available API endpoints
    5. health_check - Check for API server status
    6. Exit
    """
    print(help_text)

    while True:
        choice = input("Enter the number of the function you would like an example of (or type 'exit' to quit): ").strip().lower()
        if choice in ["6", "exit"]:
            print("Exiting help menu.")
            break
        details = {
            "1": "Example: itkspec.authenticate_user('your_access_code1', 'your_access_code2')",
            "2": "Example: itkspec.retrieve_spec(client, {'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION', 'parameter':'BOW1'}",
            "3": "Example: itkspec.retrieve_specList(client, {'project':'P', 'componentType':'PCB', 'testType':'METROLOGY', 'stage':'PCB_RECEPTION'}",
            "4": "Example: itkspec.api_help()",
            "5": "Example: itkspec.health_check()",
        }
        print(details.get(choice, "Invalid selection. Please enter a number from 1 to 6."))

### data backup from EOS
def get_from_EOS(filename):
    url = f'https://eddossan.web.cern.ch/itk-specs/{filename}'
    reqs = requests.get(url)
    if reqs.status_code != 200:
        print(f"Failed to retrieve the URL: {url}")
        return []
    csv_content = reqs.text
    print(f"Fetched content from {url}:\n{csv_content[:500]}...")

    # Parse the CSV content
    data = []
    csv_reader = csv.reader(StringIO(csv_content))
    headers = ["project", "componentType", "testType", "stage", "parameter", "spec"]
    for row in csv_reader:
        if row:
            row_data = {headers[i]: row[i] for i in range(len(headers))}
            if row_data["spec"]:
                try:
                    row_data["spec"] = json.loads(row_data["spec"].replace("'", "\""))  # Convert spec string to dictionary
                except json.JSONDecodeError:
                    print(f"Failed to decode spec: {row_data['spec']}")
                    row_data["spec"] = {}
            else:
                row_data["spec"] = {}
            data.append(row_data)

    print(f"Data: {data}")
    return data