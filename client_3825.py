import socket
import threading
import ssl
import sys          # Used for a similar purpose as os in server_3825.py.

HOST = '127.0.0.1'
PORT = 12345

running = True  # Controls the server thread so we can use it in shutdown.

def receive_messages(client_socket):
    global running
    while running:
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:     # For when the server closes the socket.
                print("Disconnected from the server.")
                break
            print(message)
        except Exception as e:
            if running:         # Only prints errors if the thread is supposed to be running.
                print(f"Error receiving message: {e}")
            break

def start_client():
    global running
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)   # Specifies IPv4 and TCP.

    # SSL setup.
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.check_hostname = False
    context.verify_mode = ssl.CERT_REQUIRED
    context.load_verify_locations(cafile="server.crt")
    
    ssl_socket = context.wrap_socket(client_socket, server_hostname=HOST)

    try:
        ssl_socket.connect((HOST, PORT))
        print("Connected to the server.")

        # Receive the client ID and connected clients list.
        client_id = ssl_socket.recv(1024).decode('utf-8')
        connected_clients = ssl_socket.recv(1024).decode('utf-8')
        print(client_id)
        print(connected_clients)

        # Start the receiving thread.
        receive_thread = threading.Thread(target=receive_messages, args=(ssl_socket,))
        receive_thread.start()

        while True:
            message = input()
            if message == ".exit":
                ssl_socket.send(message.encode('utf-8'))
                running = False         # Signal the receiving thread to stop.
                ssl_socket.close()      # Close the socket.
                receive_thread.join()   # Wait for the thread to finish.
                break
            else:
                recipient_id = input("Enter recipient ID: ")                    # Prompt for who the user wants to send to.
                ssl_socket.send(f"{recipient_id}:{message}".encode('utf-8'))    # Send the message.

    except Exception as e:
        print(f"Connection error: {e}")
    finally:
        running = False
        if 'ssl_socket' in locals():
            ssl_socket.close()
        sys.exit(0)

if __name__ == "__main__":
    start_client()