#!/usr/bin/env python3
import httpx
import json

# Test RCSB PDB API with SNCA gene search
def test_snca_search():
    # Try full-text search
    query = {
        "query": {
            "type": "terminal",
            "service": "full_text",
            "parameters": {
                "value": "SNCA"
            }
        },
        "return_type": "entry",
        "request_options": {
            "paginate": {
                "start": 0,
                "rows": 10
            }
        }
    }
    
    print("Searching for SNCA structures...")
    response = httpx.post("https://search.rcsb.org/rcsbsearch/v2/query", json=query)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        results = data.get("result_set", [])
        print(f"Found {len(results)} structures for SNCA")
        for result in results[:5]:
            print(f"- {result['identifier']}")
    else:
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_snca_search()
