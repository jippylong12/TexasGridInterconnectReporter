import json
import requests
# from topojson import feature  # Removed to avoid dependency issues

# Since we might not have topojson python library installed, we'll just inspect the raw JSON
# and infer the structure.

def analyze_structure():
    # 1. Working Test Data Structure (from our code)
    working_structure = {
        "type": "Feature",
        "id": "string ('48')",
        "properties": {"name": "string"},
        "geometry": {"type": "Polygon", "coordinates": "list"}
    }
    
    print("--- 1. Working Test Data Structure ---")
    print(json.dumps(working_structure, indent=2))

    # 2. Fetch URL Data
    url = "http://localhost:5173/data/counties-10m.json"
    print(f"\n--- 2. Fetching {url} ---")
    try:
        r = requests.get(url)
        if r.status_code != 200:
            print(f"Error fetching data: {r.status_code}")
            return
        
        topo_data = r.json()
        print("TopoJSON Type:", topo_data.get('type'))
        
        objects = topo_data.get('objects', {})
        print("Objects found:", list(objects.keys()))
        
        if 'counties' in objects:
            counties = objects['counties']
            geometries = counties.get('geometries', [])
            print(f"Total Geometries: {len(geometries)}")
            
            if len(geometries) > 0:
                sample = geometries[0]
                print("\n--- Sample Geometry (Raw TopoJSON) ---")
                print(json.dumps(sample, indent=2))
                
                print("\n--- Inferred Feature Structure ---")
                print(f"id type: {type(sample.get('id')).__name__}")
                print(f"properties: {sample.get('properties')}")
                
                # Check for Texas counties
                texas_counties = [g for g in geometries if str(g.get('id', '')).startswith('48')]
                print(f"\nTexas Counties found (id starts with '48'): {len(texas_counties)}")
                if texas_counties:
                    print("Sample Texas County:", json.dumps(texas_counties[0], indent=2))
                    
    except Exception as e:
        print(f"Analysis failed: {e}")

if __name__ == "__main__":
    analyze_structure()
