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
OK = """HTTP/1.1 200 Connection established\r\n
            Proxy-agent: Proxy\r\n\r\n""".encode()

blocked_urls = []
cache = {}

# Client handler
def handle_client(conn, addr):
    # Start timer
    open_time = time.perf_counter()
    print(f"{addr} connected.")
    # Receive the request
    request = conn.recv(MAX_DATA_SIZE)
    # Convert it to a readable format
    message = request.decode(FORMAT)
    print(f"[{addr}] {message}")
    # Extract the method, url, webserver and port from the message
    method, url, webserver, port = parse_message(message)
    # Check if the URL is blocked
    if url in blocked_urls:
        print(f"{url} is blocked")
    else:
        # Create server socket and send request
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.connect((webserver, port))
        # Handle HTTPS
        if method == "CONNECT":
            https_connection(conn, server)
        else:
            # Handle HTTP
            # Check if the request is cached
            if request in cache:
                print("Cache hit!")
                for response in cache[request]:
                    conn.sendall(response)
            else:
                server.sendall(request)
                http_connection(conn, request, server)
        # Stop the timer
        close_time = time.perf_counter()
        total_time = close_time - open_time
        print(f"{addr} closed after {total_time} seconds.")
        # Close connections
        server.close()
    conn.close()

def parse_message(message):
    # Default port
    port = 80
    first_line = message.split('\n')[0]
    method = first_line.split(' ')[0]
    url = first_line.split(' ')[1]
    # Check if CONNECT method
    if method == 'CONNECT':
        # The host is on line 5
        host_line = message.split('\n')[4]
    else:
        # The host is on line 2
        host_line = message.split('\n')[1]
    host = host_line.split(' ')[1]
    # Separate host into webserver and port
    port_pos = host.find(":")
    if (port_pos != -1): 
    # Specific port
        port = int(host[(port_pos+1):])
    webserver = host[:port_pos]
    return method, url, webserver, port

def https_connection(conn, server):
    # Send HTTP 200 response
    conn.sendall(OK)
    # Unblock sockets
    conn.setblocking(0)
    server.setblocking(0)
    # Start timer
    start_time = time.perf_counter()
    # Timeout afer 2 seconds
    while (time.perf_counter() - start_time < 2):
        try:
            # Receive and send request and reset timer
            request = conn.recv(MAX_DATA_SIZE)
            start_time = time.perf_counter()
            server.sendall(request)
        except socket.error as e:
            pass
        try:
            # Receive and send response and reset timer
            response = server.recv(MAX_DATA_SIZE)
            start_time = time.perf_counter()
            conn.sendall(response)
        except socket.error as e:
            pass
    return 0

def http_connection(conn, request, server):
    # Initialise cache entry, response and number of response misses
    cache[request] = []
    response = 0
    misses = 0
    # Timeout after 100 response misses
    while misses < 100:
        while misses < 100:
            try:
                # Try to receive data
                response = server.recv(MAX_DATA_SIZE)
                server.setblocking(0)
                # On success, reset misses
                misses = 0
                break
            except socket.error as e:
                # On failure, increment misses
                misses += 1
        # Cache the response
        cache[request].append(response)
        # Send the response
        conn.sendall(response)
    return 0

# Ask to block URLs
def ask_for_blocked_urls():
    url = input("Enter a URL to block, or q to quit:\n")
    while url != "q":
        # Handle HTTPS URLs
        if url.startswith("https://"):
            url = url[8:] + ":443"
        # Add URL to list of blocked URLs
        blocked_urls.append(url)
        url = input("Enter a URL to block, or q to quit:\n")
    # Print blocked URLs
    print("Blocked URLs:\n")
    print(*blocked_urls, sep = "\n")
    
def start():
    ask_for_blocked_urls()
    # Create socket
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.bind(ADDR)
    client.listen()
    while True:
        conn, addr = client.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server is starting...")
start()
