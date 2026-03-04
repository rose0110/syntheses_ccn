
import requests
import json
import os

API_KEY = "uwE0WHrZ5TtUA7I5UVdzNYstKVt46RHniczf8E6mJeo"
IDCC = "1486"

local_url = f"http://127.0.0.1:8000/conventions/idcc/{IDCC}"
remote_url = f"https://sdp-conventions-api.onrender.com/conventions/idcc/{IDCC}"

headers = {"X-API-Key": API_KEY}

def test_api(name, url):
    print(f"--- Testing {name} API ---")
    try:
        response = requests.get(url, headers=headers, timeout=60)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            # print top level keys
            print(f"Keys: {list(data.keys())}")
            # print some meta
            meta = data.get('metadata', {})
            print(f"Name: {meta.get('name')}")
            print(f"IDCC: {meta.get('idcc')}")
            print(f"TOC Entries: {len(data.get('toc', []))}")
            print(f"Sections Count: {len(data.get('sections', []))}")
            print(f"Status Field: {data.get('status')}")
            return data
        else:
            print(f"Error: {response.text}")
    except Exception as e:
        print(f"Expection: {e}")
    return None

local_data = test_api("Local", local_url)
print("\n")
remote_data = test_api("Remote (Boss)", remote_url)

if local_data and remote_data:
    print("\n--- Comparison ---")
    if local_data.keys() == remote_data.keys():
        print("Success: API keys match structure.")
    else:
        print(f"Diff keys: Local={list(local_data.keys())} vs Remote={list(remote_data.keys())}")
