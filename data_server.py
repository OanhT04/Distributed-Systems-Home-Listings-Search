from socket import *
import json
import argparse
import socket

#Data layer contains the data that a client wants to manipulate through the application components
# =============================================================================
# Start TCP server
#The socket will wait for a connection from the application layer
# =============================================================================

# DATA LAYER:
HOST = "127.0.0.1"
PORT = 5001



# =============================================================================
# Ensure all responses end with END (required by application layer)
# =============================================================================
def ensureEnd(msg: str) -> str:
    return msg if msg.endswith("\nEND\n") else msg.rstrip("\n") + "\nEND\n"

#==============================================================================
# 1. create server socket and use TCP
# 2. set socket option to allow re use of the same address
# 3. attach socket to port and IP address
# 4. allow five incoming connections to wait; one client at a time
# 5. accept new connection from app server to talk to data server through connection socket
# ==============================================================================

def runServer(host, port, listings):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen(5)
    print(f"Data Server listening on {host}:{port}")
    while True:
        conn, addr = server.accept()
        print(f"Connection from {addr}")
        with conn:
            buffer = ""
            while True:
                data = conn.recv(4096)
                if not data:
                    break
                buffer += data.decode("utf-8", errors="replace")
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    request = line.strip()
                    if not request:
                        continue
                    response = processCommand(request, listings)
                    conn.sendall(
                        ensureEnd(response).encode("utf-8")
                    )


# =============================================================================
#load JSON data
# =============================================================================
def loadJSON(db_file: str) -> list[dict]:
    try:
        with open(db_file, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        return []




# =======================================================================================
# querying data: simple filtering based on city and price; no formatting
# =======================================================================================
def searchRawData(listings, city, max_price):
    results = []
    for item in listings:
        try:
            if item.get("city", "").lower() == city.lower() and float(item.get("price", 1e18)) <= float(max_price):
                results.append(item)
        except:
            continue
    return results


# =============================================================================
# response formatting for application layer
# =============================================================================
def responseFormatter(rows: list[dict]) -> str:
    msg = f"OK RESULT {len(rows)}\n"
    for item in rows:
        msg += (
            f"id={item.get('id')};"
            f"city={item.get('city')};"
            f"address={item.get('address')};"
            f"price={item.get('price')};"
            f"bedrooms={item.get('bedrooms')}\n"
        )
    msg += "END\n"
    return msg


# =============================================================================
# Error handling for formats and commands
# =============================================================================
def formatError(message):
    return ensureEnd(f"ERROR: {message}")


# =============================================================================
# Command processing for application layer
# =============================================================================
def processCommand(line: str, listings: list[dict]) -> str:
    parts = line.strip().split()  # split by whitespace
    if not parts:
        return formatError("malformed command")
    command = parts[0].upper()
    
    if command == "RAW_LIST":  # command from application layer to get all listings without formatting
        if len(parts) != 1:
            return formatError("malformed command")
        return responseFormatter(listings)

    elif command == "RAW_SEARCH":  # command from application layer to search listings without formatting
        if len(parts) != 3:
            return formatError("SEARCH command requires 2 arguments: city and max_price")

        city = parts[1]
        try:  # checks if max_price is a valid number
            max_price = float(parts[2])
        except ValueError:
            return formatError("Invalid max_price value")

        results = searchRawData(listings, city, max_price)  # list of homes matching search criteria
        return responseFormatter(results)  # return formatted response for application layer to prepare for client

    else:
        return formatError("unknown command")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=HOST, help ="IP address")
    ap.add_argument("--port", type=int, default=PORT)
    ap.add_argument("--db", default="listings.json", required = True)
    args = ap.parse_args()
    listings = loadJSON(args.db)
    runServer(args.host, args.port, listings)


if __name__ == "__main__":
    main()
