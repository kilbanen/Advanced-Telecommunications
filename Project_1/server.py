# Import libraries
import socket
import threading

# Define constants
MAX_DATA_SIZE = 8192
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'ISO-8859-1'

# Client handler
def handle_client(conn, addr):
    print(f"[NEW CONNECTION] {addr} connected.")

    connected = True
    while connected:
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
        print(f"Sending {method} request to {webserver} {port}")
        if(method == "CONNECT"):
            response = "HTTP/1.1 200 Connection established\r\nProxy-agent: Proxy\r\n\r\n".encode()
            print("Initiating connection...")
            conn.sendall(response)
            conn.setblocking(0)
            outgoing.setblocking(0)
            while True:
                try:
                    request = conn.recv(MAX_DATA_SIZE)
                    outgoing.sendall(request)
                except socket.error as e:
                    pass
                try:
                    response = outgoing.recv(MAX_DATA_SIZE)
                    conn.sendall(response)
                except socket.error as e:
                    pass
            connected = False
        else:
            outgoing.sendall(request)
            while connected:
                response = outgoing.recv(MAX_DATA_SIZE)
                print(f"Received response {response}")
                if (len(response) > 0):
                    print("Sending response to client")
                    conn.send(response)
                else:
                    connected = False
    outgoing.close()
    conn.close()

def parse_message(message):
    # Default port
    port = 80
    first_line = message.split('\n')[0]
    method = first_line.split(' ')[0]
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

def start():
    # Create socket
    incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    incoming.bind(ADDR)
    incoming.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = incoming.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server is starting...")
start()
