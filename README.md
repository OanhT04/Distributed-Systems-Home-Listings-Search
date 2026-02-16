# Distributed-Systems-Home-Listings-Search
This project is a three-tier distributed system built using Python sockets. It allows users to interact through a user interface to view all home listings and search listings by city and price. 



## Usage Instructions: Using default Host (<127.0.0.1>) and Ports!

1. Open Terminal and enter the command:
   
```bash
python data_server.py --db listings.json
```
uses default host and port

2. Open a second Terminal and enter command:
```bash
   python application_server.py 
```
uses default host and port and connects to default host and port in data layer

3. Open a third Terminal and run:
```bash   
   python client.py
```
connects to default application host and port 

Note: If you want to use a different data listing file; replace listings.json with custom json file. 

## Configuration Options - All have defaults however can be customized with command line arguments
```bash   
   python data_server.py --host <127.0.0.1> --port <DATA_PORT> --db <JSON_FILE>
   python app_server.py --host <127.0.0.1>  --port <APP_PORT>  --data-host <127.0.0.1> --data-port <DATA_PORT>
   python client.py --127.0.0.1 --port <APP_PORT>
```
use 127.0.0.1 as host for all which is also default... 

#### example:

         # Start Data Server
         python data_server.py --host 127.0.0.1 --port 7001 --db listings.json
         
         # Start Application Server
         python app_server.py --host 127.0.0.1 --port 8002 --data-host 127.0.0.1 --data-port 7001
         
         # Start Client
         python client.py --host 127.0.0.1 --port 8002

## Implementation

#### Client:
- The client consists of the user interface and it connects to the application layer only to send client requests and recieve responses. 
- Provides interactive menu interface
- Sends LIST, SEARCH, and QUIT commands
- Formats results into a clean table
- Measures response time for performance tracking
- Maintains a persistent socket connection

#### Application Layer
- The Application Server acts as the middle-tier server between the Client and the Data Server.
- Acts as middleware between Client and Data Server
- Converts client commands:
-    LIST → RAW_LIST
-    SEARCH <city> <max_price> → RAW_SEARCH <city> <max_price>
- Sorts results: Price ascending, Bedrooms descending
- Implements caching for repeated queries
- Logs all requests and responses (app_server.log)
- Handles errors and timeouts
  
#### Data Layer
- Loads home data from JSON file
- Processes:
-    RAW_LIST and RAW_SEARCH
- Filters listings based on city and max price
- Sends formatted responses back to Application Layerication Layer.

#### Error Handling Implemented at Data Layer, Application Layer and Client Layer

## Example Inputs and Outputs  
<img width="800" height="261" alt="image" src="https://github.com/user-attachments/assets/6ff2bc93-0b3e-4f01-97ea-992653d645a9" />

### Search

#### Listings in City and within Maximum Price 
<img width="800" height="500" alt="image" src="https://github.com/user-attachments/assets/1909c164-9cb9-4e69-91a6-7835fbde9c65" />

#### No listings found in City:
<img width="800" height="429" alt="image" src="https://github.com/user-attachments/assets/02359a21-c4a8-4a23-88a3-ee9747d66ed9" />


#### No Listings Found under Maximum Price
<img width="800" height="444" alt="image" src="https://github.com/user-attachments/assets/1f481a48-0a32-45f1-b2b8-743155673afa" />


### All Listings Retrieving from Cache Memory 
#### The first request from client to query all home listings took 16.60 ms; after the query was saved in a cache, and upon requesting a list of all listings, it took 5.60 ms...
D<img width="1656" height="1059" alt="image" src="https://github.com/user-attachments/assets/60adf4f6-0096-4e61-b4de-5a5b75b507ac" /> <img width="1324" height="938" alt="image" src="https://github.com/user-attachments/assets/63f5a7d5-d98f-4b9b-a809-c76abdf07818" />

### Example Log 
<img width="2647" height="592" alt="image" src="https://github.com/user-attachments/assets/d990976a-3117-4a30-a607-c85d52597540" />




