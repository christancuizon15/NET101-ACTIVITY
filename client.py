import requests

# The URL of your running Flask API
url = "http://127.0.0.1:5000"

print(f"Sending GET request to {url}...")

try:
    # 1. Make the request to the API
    response = requests.get(url)
    
    # 2. Check if the request was successful (Status Code 200)
    if response.status_code == 200:
        print("Successfully connected to the API!\n")
        
        # 3. Convert the JSON response into a Python dictionary
        data = response.json()
        
        # 4. Extract the specific command output we want
        # (The keys match the command strings inside your api.py)
        show_ver = data['data']['show version']
        show_ip = data['data']['show ip interface brief']
        
        # 5. Print the data nicely formatted
        print("=" * 50)
        print(" SHOW IP INTERFACE BRIEF ")
        print("=" * 50)
        print(show_ip)
        
        print("\n" + "=" * 50)
        print(" SHOW VERSION ")
        print("=" * 50)
        print(show_ver)
        
    else:
        print(f"Failed to get data. Status code: {response.status_code}")

except requests.exceptions.ConnectionError:
    print("Error: Could not connect to the API. Is api.py running in the other terminal?")
except Exception as e:
    print(f"An error occurred: {e}")