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
        # Extract the url from the HTTP message
        first_line = msg.split('\n')[0]
        url = first_line.split(' ')[1]
        # Extract the webserver and port from the url
        # Found between "://" and first "/"
        http_pos = url.find("://")
        # If there is no "://" then the webserver starts at the start of the url
        if (http_pos==-1):
            temp = url
        # If there is a "://" then the webserver starts directly after it
        else:
            temp = url[(http_pos+3):]
        # Find the port position if it exists
        port_pos = temp.find(":")
        webserver_pos = temp.find("/")
        if webserver_pos == -1:
            webserver_pos = len(temp)
        webserver = ""
        port = -1
        # Default port
        if (port_pos==-1 or webserver_pos < port_pos): 
            port = 80 
            webserver = temp[:webserver_pos]
        # Specific port
        else:
            port = int((temp[(port_pos+1):])[:webserver_pos-port_pos-1])
            webserver = temp[:port_pos]
        # Create outgoing socket and send request
        outgoing = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        outgoing.connect((webserver, port))
        outgoing.sendall(request)
        print(f"Sending request to {webserver} {port}")
        while connected:
            data = outgoing.recv(MAX_DATA_SIZE)
            if (len(data) > 0):
                conn.send(data)
            else:
                connected = false
                outgoing.close()
    conn.close()

def start():
    incoming.listen()
    print(f"[LISTENING] Server is listening on {SERVER}")
    while True:
        conn, addr = incoming.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

print("[STARTING] Server is starting...")
start()
