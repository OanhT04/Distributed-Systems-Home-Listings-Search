import socket
import time

#=============================================================================
#Oanh Tran 029661786
#CECS 327 - Distributed Systems
#=============================================================================

#=============================================================================
#host and port for application layer
#=============================================================================
HOST, PORT = "127.0.0.1", 5002


#=============================================================================
#print response from server in a nice format
#=============================================================================

def printQuery(resp: str):
    resp = resp.strip()
    if "QUITTING" in resp:
        return
    # No results
    if "OK RESULT 0" in resp:
        print("No homes found matching your criteria.")
        return
    # Parse rows
    rows = []
    for line in resp.splitlines():
        line = line.strip()
        if not line or line == "END" or line.startswith("OK RESULT"):
            continue
        item = {}
        for part in line.split(";"):
            if "=" in part:
                k, v = part.split("=", 1)
                item[k.strip()] = v.strip()
        if item:
            rows.append(item)
    # Table formatting
    cols = ["id", "city", "address", "price", "bedrooms"]
    widths = {c: len(c) for c in cols}
    for r in rows:
        for c in cols:
            widths[c] = max(widths[c], len(str(r.get(c, ""))))
    header = " | ".join(c.ljust(widths[c]) for c in cols)
    sep = "-+-".join("-" * widths[c] for c in cols)
    print(header)
    print(sep)
    for r in rows:
        print(" | ".join(str(r.get(c, "")).ljust(widths[c]) for c in cols))



#=============================================================================
#sending commands and receiving response from application
#=============================================================================
def run(sock, cmd):
    # send command to server
    sock.sendall((cmd.strip() + "\n").encode())
    data = ""
    while True:
        chunk = sock.recv(4096).decode()
        if not chunk:
            break
        data += chunk
        if "\nEND\n" in data or data.startswith("ERROR: APPLICATION"): #end of response or error response
            break
    print(f"\n> {cmd}")
    printQuery(data)



#=============================================================================
#client Search/List commands for user interface; also measure time taken for each command
# sends SEARCH, LIST to application layer to parse 
#=============================================================================
def search(sock, city, max_price):
    start_time = time.perf_counter()
    city = city.replace(" ", "") #remove spaces for command formatting as JSON files have no spaces in city names
    run(sock, f"SEARCH {city} {max_price}")
    end_time = time.perf_counter()
    total_ms = (end_time - start_time) * 1000
    print(f"\nSearch completed in {total_ms:.2f} ms.")


def listHomes(sock):
    start_time = time.perf_counter()
    print("-----------------------------Listing all homes: ------------------------------")
    run(sock, "LIST")
    end_time = time.perf_counter()
    total_ms = (end_time - start_time) * 1000
    print(f"\nTotal time: {total_ms:.2f} ms\n")
    

#============================================================================
#I want to keep one socket open until user exits rather than create a socket
#each request. Simpler user interface!
#============================================================================
def ClientMenu():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            print(f"Connected to application layer at {HOST}:{PORT}")

            while True:
                print("\n-----------------------------------")
                print("   Welcome to the Home Listings Search Tool")
                print("-----------------------------------")
                print("Please choose one of the options below:")
                print("  1. View all home listings")
                print("  2. Search for a home")
                print("  3. Exit")
                print("-----------------------------------")
                choice = input("Your choice (1-3): ").strip()
                if choice == "1":
                    print("\nFetching all available homes...\n")
                    listHomes(s)
                elif choice == "2":
                    print("\nSearch for a home")
                    print("-----------------")
                    city = input("City: ").strip()
                    if not city:
                        print("City cannot be empty.")
                        continue
                    max_price = input("Maximum price: ").strip()
                    if not max_price.isdigit():
                        print("Please enter a valid number for the price.")
                        continue
                    print("-----------------------------------------------")
                    print(f"\nSearching homes in {city} under {max_price}...")
                    search(s, city, max_price)
                elif choice == "3":
                    run(s, "QUIT") # CLOSE CONNECTION
                    break
                else:
                    print("Invalid selection. Please choose 1, 2, or 3.")  
            print("Bye!")        
    except ConnectionRefusedError:
        print("ERROR: Could not connect to Application Server.")
    except socket.timeout:
        print("ERROR: Connection timed out.")
    except OSError as e:
        print(f"Socket error: {e}")
if __name__ == "__main__":
    ClientMenu()

