# Import libraries
import socket
import threading

# Define constants
MAX_DATA_SIZE = 8192
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'

# Create socket
incoming = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
incoming.bind(ADDR)

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
        webserver, port = get_host(msg)
        # Create outgoing socket and send request
        print(f"Sending request to {webserver} {port}")
        outgoing = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        outgoing.connect((webserver, port))
        outgoing.sendall(request)
        while connected:
            response = outgoing.recv(MAX_DATA_SIZE)
            #msg = response.decode(FORMAT)
            print(f"Received response {response}")
            if (len(response) > 0):
                print("Sending response to client")
                conn.send(response)
            else:
                connected = False
    outgoing.close()
    conn.close()

def get_host(message):
    # Default port
    port = 80
    first_line = message.split('\n')[0]
    message_type = first_line.split(' ')[0]
    if message_type == 'CONNECT':
        host_line = message.split('\n')[4]
    else:
        host_line = message.split('\n')[1]
    host = host_line.split(' ')[1]
    port_pos = host.find(":")
    if (port_pos != -1): 
    # Specific port
        port = int(host[(port_pos+1):])
    webserver = host[:port_pos]
    return webserver, port

def start():
    incoming.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = incoming.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server is starting...")
start()
