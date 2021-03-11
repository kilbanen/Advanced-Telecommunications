# Import libraries
import socket
import threading
import time

# Define constants
MAX_DATA_SIZE = 8192
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'ISO-8859-1'

blocked_urls = []

# Client handler
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")
    # Receive the request
    request = conn.recv(MAX_DATA_SIZE)
    # Convert it to a readable format
    msg = request.decode(FORMAT)
    print(f"[{addr}] {msg}")
    # Extract the webserver and port from the message
    method, webserver, port = parse_message(msg)
    outgoing = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    outgoing.connect((webserver, port))
    # Create outgoing socket and send request
    if(method == "CONNECT"):
        https_connection(conn, outgoing)
    else:
        outgoing.sendall(request)
        http_connection(conn, outgoing)
    print(f"[CLOSING CONNECTION] {addr} closed.")
    outgoing.close()
    conn.close()

def parse_message(message):
    # Default port
    port = 80
    first_line = message.split('\n')[0]
    method = first_line.split(' ')[0]
    # Check if CONNECT method
    if method == 'CONNECT':
        host_line = message.split('\n')[4]
    else:
        host_line = message.split('\n')[1]
    host = host_line.split(' ')[1]
    port_pos = host.find(":")
    if (port_pos != -1): 
    # Specific port
        port = int(host[(port_pos+1):])
    webserver = host[:port_pos]
    return method, webserver, port

def https_connection(conn, outgoing):
    ok = "HTTP/1.1 200 Connection established\r\nProxy-agent: Proxy\r\n\r\n".encode()
    conn.sendall(ok)
    conn.setblocking(0)
    outgoing.setblocking(0)
    start_time = time.perf_counter()
    while (time.perf_counter() - start_time < 2):
        try:
            request = conn.recv(MAX_DATA_SIZE)
            start_time = time.perf_counter()
            outgoing.sendall(request)
        except socket.error as e:
            pass
        try:
            response = outgoing.recv(MAX_DATA_SIZE)
            start_time = time.perf_counter()
            conn.sendall(response)
        except socket.error as e:
            pass
    return 0

def http_connection(conn, outgoing):
    while True:
        response = outgoing.recv(MAX_DATA_SIZE)
        if (len(response) > 0):
            conn.sendall(response)
        else:
            break
    return 0

def start():
    # Ask to block urls
    url = input("Enter a URL to block, or q to quit:\n")
    while url != "q":
        blocked_urls.append(url)
        url = input("Enter a URL to block, or q to quit:\n")
    # Print blocked urls
    print("Blocked URLS:\n")
    print(*blocked_urls, sep = "\n")
    # Create socket
    incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incoming.bind(ADDR)
    incoming.listen()
    while True:
        conn, addr = incoming.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server is starting...")
start()
