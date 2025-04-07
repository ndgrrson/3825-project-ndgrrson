import socket
import threading
import ssl
import os

# Server configuration.
HOST = '127.0.0.1'  # Localhost.
PORT = 12345        # Server's port.

# Global variables
clients = {}            # Stores {client_id: socket} for active connections.
server_running = True   # To be used later when the server is closing.

def broadcast_to_all(message):  # For printing to users any server-wide messages.

def handle_client(sock, client_id):

def start_server():                                                     # The main function for the server.

def shutdown_server():                              # Shuts the server down when prompted in the server terminal.

if __name__ == "__main__":
    start_server()