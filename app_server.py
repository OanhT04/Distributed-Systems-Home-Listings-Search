import socket
import argparse
from typing import List, Dict
import logging

# Oanh Tran 029661786

# =============================================================================
# APPLICATION LAYER: Default ports and IP
# =============================================================================
HOST = "127.0.0.2"
PORT = 5002

# DATA LAYER:
DATA_HOST = "127.0.0.1"
DATA_PORT = 5001

# persistent data socket (created in main) so it can stay connected to data server
dataSock = None

#==============================================================================
# Interceptor Logger (logs requests + replies)
#==============================================================================
logger = logging.getLogger("app_server")
logger.setLevel(logging.INFO)

_file_handler = logging.FileHandler("app_server.log", mode="a", encoding="utf-8")
_file_handler.setFormatter(logging.Formatter("%(asctime)s | %(message)s"))
logger.addHandler(_file_handler)
logger.propagate = False

# =============================================================================
# Interceptor helpers; just formatting the log
# =============================================================================
def logRequest(addr, cmd: str):
    logger.info(f"{addr} | REQUEST | {cmd}")

def logReply(addr, resp: str):
    one_line = resp.replace("\n", "\\n")
    logger.info(f"{addr} | REPLY   | {one_line}")


# =============================================================================
# Helpers
# =============================================================================
def ensureEnd(msg: str) -> str:
    return msg if msg.endswith("\nEND\n") else msg.rstrip("\n") + "\nEND\n"

def errorResponse(message: str) -> str:
    return ensureEnd(f"ERROR: APPLICATION {message}")

# =============================================================================
# sending commands to the DATA server and receiving responses
# =============================================================================
def send(conn, cmd: str) -> str:
    try:
        logRequest("APPLICATION->DATA", cmd)

        conn.sendall((cmd.strip() + "\n").encode("utf-8"))
        data = ""
        while True:
            raw = conn.recv(4096)
            if not raw:
                break
            data += raw.decode("utf-8", errors="replace")
            if "\nEND\n" in data:
                break

        response = ensureEnd(data)
        # LOG reply coming back from data server
        logReply("DATA->APPLICATION", response)

        return response

    except socket.timeout:
        resp = errorResponse("DATA server timed out")
        logReply("DATA->APPLICATION", resp)
        return resp
    except ConnectionRefusedError:
        resp = errorResponse("DATA server connection refused")
        logReply("DATA->APPLICATION", resp)
        return resp
    except OSError as e:
        resp = errorResponse(f"DATA server error ({e})")
        logReply("DATA->APPLICATION", resp)
        return resp

# =============================================================================
# Command processing function from Client; and reformat to send to Data Server
# =============================================================================
def formatClientRequest(cmd: str) -> str:
    cmd = cmd.strip()
    parts = cmd.split()
    if not parts:
        return errorResponse("Empty command")

    if cmd.upper() == "LIST":
        return "RAW_LIST"
    if parts[0].upper() == "SEARCH":
        if len(parts) != 3:
            return errorResponse("Usage: SEARCH <city> <max_price>")
        city = parts[1]
        max_price = parts[2]
        return f"RAW_SEARCH {city} {max_price}"


    return errorResponse("Unknown command")

# =============================================================================
# Upon receiving response from data server, process and format data
# before sending to client; sort by price ascending and bedrooms descending
# =============================================================================
def parseRows(resp: str) -> List[Dict]:
    lines = resp.splitlines()
    rows: List[Dict] = []
    for line in lines:
        line = line.strip()
        if not line or line == "END" or line.startswith("OK RESULT"):
            continue
        parts = [p for p in line.split(";") if p]
        item: Dict = {}

        for p in parts:
            if "=" not in p:
                continue
            k, v = p.split("=", 1)
            item[k.strip()] = v.strip()
            
        # convert numeric fields
        if "id" in item:
            try:
                item["id"] = int(item["id"])
            except ValueError:
                pass
        if "price" in item:
            try:
                item["price"] = int(item["price"])
            except ValueError:
                pass
        if "bedrooms" in item:
            try:
                item["bedrooms"] = int(item["bedrooms"])
            except ValueError:
                pass

        if item:
            rows.append(item)

    return rows

def dataResponseSort(rows: List[Dict]) -> List[Dict]:
    # price ascending, bedrooms descending
    return sorted(rows, key=lambda x: (x.get("price", 10**18), -x.get("bedrooms", 0)))

def responseFormatter(rows: List[Dict]) -> str:
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
CACHE: Dict[str, str] = {}

# =============================================================================
# Handle one client connection (multiple commands until QUIT and close only client connection)
# so it does not require reconnection per command
# =============================================================================
def handleClient(conn: socket.socket):
    with conn:
        #interpret commands from client
        buffer = ""

        while True:
            data = conn.recv(4096)
            if not data:
                return
            buffer += data.decode("utf-8", errors="replace")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                cmd = line.strip()

                if cmd == "":
                    continue

                # LOG REQUEST
                logRequest("CLIENT->APPLICATION", line)

                # QUIT AND CLOSE CONNECTION
                if cmd.upper() == "QUIT":
                    reply = "QUITTING: OK BYE....\nEND\n"
                    logReply("APPLICATION->CLIENT", reply)
                    conn.sendall(reply.encode("utf-8"))
                    print('Closing Client Connection...')
                    conn.close()
                    return

                formatted_cmd = formatClientRequest(cmd)

                if formatted_cmd.startswith("ERROR: APPLICATION"):
                    reply = formatted_cmd
                    logReply("APPLICATION->CLIENT", reply)
                    conn.sendall(reply.encode("utf-8"))
                    continue

                cache_key = " ".join(cmd.upper().split())
                if cache_key in CACHE:
                    print(f"Cache hit for query: {cmd}")
                    reply = CACHE[cache_key]
                    logReply("APPLICATION->CLIENT", reply)
                    conn.sendall(reply.encode("utf-8"))
                    continue

                # call data server
                data_response = send(dataSock, formatted_cmd)

                if data_response.startswith("ERROR"):
                    reply = ensureEnd(data_response)
                    logReply("APPLICATION->CLIENT", reply)
                    conn.sendall(reply.encode("utf-8"))
                    continue

                # parse -> sort -> format
                try:
                    rows = parseRows(data_response)
                    sorted_rows = dataResponseSort(rows)
                    response = responseFormatter(sorted_rows)
                except Exception as e:
                    response = errorResponse("Internal processing error")
                    print(f"[APP ERROR] {e}")
                # cache valid commands
                if cmd.upper().startswith(("LIST", "SEARCH")):
                    CACHE[cache_key] = response

                reply = ensureEnd(response)
                logReply("APPLICATION->CLIENT", reply)

                conn.sendall(reply.encode("utf-8"))

# =============================================================================
# TCP server for receiving commands from clients and sending responses back
# =============================================================================
def startTcp(host: str, port: int):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((host, port))
        server.listen()
        print(f"APPLICATION listening on {host}:{port}...")

        while True:
            conn, addr = server.accept()
            handleClient(conn)

# =============================================================================
# Main
# =============================================================================
def main():
    global dataSock

    parser = argparse.ArgumentParser(description="Application Layer Server")
    parser.add_argument("--host", default=HOST, help="Host to listen on")
    parser.add_argument("--port", type=int, default=PORT, help="Port to listen on")

    # configurable Data Server endpoint (defaults preserved)
    parser.add_argument("--data-host", default=DATA_HOST, help="Data server host to connect to")
    parser.add_argument("--data-port", type=int, default=DATA_PORT, help="Data server port to connect to")

    args = parser.parse_args()

    dataSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    dataSock.settimeout(10)

    dataSock.connect((args.data_host, args.data_port))
    print(f"Connected to DATA server at {args.data_host}:{args.data_port}")

    startTcp(args.host, args.port)

if __name__ == "__main__":
    main()