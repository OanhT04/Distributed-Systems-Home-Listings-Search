# Distributed-Systems-Home-Listings-Search

## Usage Instructions

1. Open Terminal and enter the command:
   
```bash
python data_server.py --db listings.json
```
uses default host and port

3. Open a second Terminal and enter command:
```bash
   python application_server.py 
```
uses default host and port

5. Open a third Terminal and run:
```bash   
   python client.py
```
Note: If you want to use a different data listing file; replace listings.json with custom json file. 

## Implementation

#### Client:
The client consists of the user interface and it connects to the application layer only to send client requests and recieve responses. 
- Uses a persistent TCP connection and communicates directly with the application layer; using sockets to send "LIST", "SEARCH" and "QUIT" COMMANDS to application layer. 
- It is a menu driven interface for users to view all home listings or search home listings or quit the application.
- The client does not communicate directly with the Data Server. All requests are routed through the Application Layer.
- Results are printed in tabular format
- calculates time for each search to complete in ms

#### Application Layer
The Application Server acts as the middle-tier server between the Client and the Data Server.
- It accepts a persistent TCP connection from the client and continuously processes multiple commands during the same session until the client sends QUIT.
-  For each request, the Application Layer validates and formats the client command (formatClientRequest), checks a local in-memory cache for repeated LIST or SEARCH queries, and forwards cache-misses to the Data Server.
-  After receiving the Data Server response, it parses the returned rows, applies sorting/processing logic, formats the final application response, appends the END terminator, and sends it back to the client.
- enforces the protocol, improves performance with caching, and isolates the client from direct data access.
  
#### Data Layer
Data Server (data access layer) responsible for serving home listing data to the Application Layer.
- It listens for incoming TCP connections from the Application Layer and processes requests such as LIST and SEARCH. For LIST, it returns all available home records; for SEARCH, it filters records based on the provided city and maximum price.
-  returns results using a simple text-based response protocol and terminates each response with END so the Application Layer knows when the message is complete.
- does not interact with the client directly and focuses only on retrieving/filtering data and returning raw results (or errors) back to the Application Layer.

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




