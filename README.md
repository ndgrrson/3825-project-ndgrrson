# 3825-project-ndgrrson

Nikolas Garrison
04/06/2025
COMP 3825 - Network/Info Assurance
Final Project

This program is a client/server chat application using Python. It includes encrypted messaging, confirms to the user when their message has been sent, and allows multiple users to connect.

To begin using it:
1. Generate an SSL certificate with the command below.
    openssl req -newkey rsa:2048 -nodes -keyout server.key -x509 -days 365 -out server.crt -subj "/CN=localhost"

2. Open at least 2 separate terminals where the client Python files will be ran.

3. Enter messages from either terminal and which connected client the message should be sent to.

4. The chat can be exited if the user types ".exit" or if .shutdown is ran in the server terminal.