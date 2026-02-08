# Distributed-Systems-Home-Listings-Search

## Usage Instructions

1. Open Terminal and enter the command:
   
```bash
python data.py --port 5001 --db listings.json
```

3. Open a second Terminal and enter command:
```bash
   python ApplicationLayer.py --port 5002
```

5. Open a third Terminal and run:
```bash   
   python client.py
```
Note: If you want to use a different data listing file; replace listings.json with custom json file. 

## Implementation

#### Client.py

#### Application Layer

#### Data.py

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


### All Listings

<img width="800" height="1049" alt="image" src="https://github.com/user-attachments/assets/f7011fc1-f2e8-4609-a744-ecca985ee23d" />
