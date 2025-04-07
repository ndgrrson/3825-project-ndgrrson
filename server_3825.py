import socket       # Imports low-level TCP/UDP communication.
import threading    # Allows for running multiple threads concurrently.
import ssl          # Allows for SSL/TLS encryption.
import os           # Allows for OS interaction so users can be returned to their CLIs when the server closes.

# Server configuration.
HOST = '127.0.0.1'  # Localhost.
PORT = 12345        # Server's port.

# Global variables
clients = {}            # Stores {client_id: socket} for active connections.
server_running = True   # To be used later when the server is closing.

def broadcast_to_all(message):  # For printing to users any server-wide messages.
    dead_clients = []
    for client_id, sock in list(clients.items()):
        try:
            sock.send(message.encode('utf-8'))      # Attempt to send the message.
        except:
            dead_clients.append(client_id)          # Label any "dead" clients.
    for client_id in dead_clients:
        del clients[client_id]                      # Remove "dead" clients.

def handle_client(sock, client_id):
    try:
        while True:
            sock.send(f"CLIENT_LIST:{','.join(clients.keys())}".encode())   # Send the current list of clients.
            
            msg = sock.recv(1024).decode('utf-8')   # Wait for a message.
            if not msg or msg == ".exit":
                break
                
            recipient_id, message = msg.split(":", 1)
            
            if recipient_id in clients: # Route the message to the other user.
                try:
                    clients[recipient_id].send(f"{client_id}: {message}".encode())  # Takes the client ID to be sent to from the client's file.
                    sock.send(f"Message delivered to {recipient_id}".encode())      # Confirmation message.
                except:
                    sock.send(f"ERROR: Failed to send to {recipient_id}".encode())  # Failure message.
            else:
                sock.send(f"ERROR: Client {recipient_id} not found".encode())       # For when the user we're sending to isn't found.
                
    except ConnectionResetError:
        print(f"Client {client_id} disconnected abruptly.")
    finally:
        sock.close()                                                # Closes the socket to the specific client.
        del clients[client_id]                                      # Removes the client from the client list.
        print(f"Client {client_id} removed")                        # Prints that the client was removed.
        broadcast_to_all(f"CLIENT_LIST:{','.join(clients.keys())}") # Updates the remaining clients regarding the change.

def start_server():                                                     # The main function for the server.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Specifies IPv4 and TCP so we can bind to an IP/port and listen for connections.
    server_socket.bind((HOST, PORT))                                    # Binds to the port.
    server_socket.listen(5)                                             # Queues up to 5 connections.
    print(f"Server running on {HOST}:{PORT}. Type '.shutdown' to kill.")

    # SSL setup.
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)           # Create an SSL with default settings.
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")    # Load certificates.
    ssl_socket = context.wrap_socket(server_socket, server_side=True)       # Encryption.

    # Function to listen for the .shutdown command.
    def shutdown_listener():
        while True:
            if input() == ".shutdown":
                shutdown_server()

    threading.Thread(target=shutdown_listener, daemon=True).start()  # Allows shutdown without waiting for shutdown_listener.

    while True: # Accept new clients.
        try:
            client_sock, addr = ssl_socket.accept()                                         # Accept the connection.
            client_id = f"Client-{len(clients)+1}"                                          # Generate the unique ID.
            clients[client_id] = client_sock                                                # Track the client.
            client_sock.send(f"Your ID: {client_id}".encode())                              # Send the client's ID.
            threading.Thread(target=handle_client, args=(client_sock, client_id)).start()   # Handle the client.
        except:
            if not server_running:
                break

def shutdown_server():                              # Shuts the server down when prompted in the server terminal.
    global server_running
    print("\nShutting down server...")
    broadcast_to_all("[SERVER] !!! SHUTDOWN !!!")   # Notify all connected clients that the server's shutting down.
    
    # Close all client sockets.
    for client_id, sock in list(clients.items()):
        sock.close()
        del clients[client_id]
    
    os._exit(0)  # Return to the CLI.

if __name__ == "__main__":
    start_server()