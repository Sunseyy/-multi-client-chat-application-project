import re
import socket
import threading

def validate_username(nickname):
    return bool(re.match("^[a-zA-Z0-9_.-]{3,}$", nickname))

nickname = input("Choose your nickname: ")
while not validate_username(nickname):
    nickname = input("Choose another username this one is not valid !: ")

password = input("Choose your password: ")

# Connecting To Server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(('127.0.0.1', 55555))

# Initialize opt to True
opt = True


# Listening to Server and Sending Nickname
def receive():
    global nickname
    global opt
    while True:
        try:
            # Receive Message From Server
            # If 'NICK' Send Nickname
            message = client.recv(1024).decode('ascii')
            if message == 'username':
                client.send(nickname.encode('ascii'))
            if message =='password':
                
                client.send(password.encode('ascii'))
            elif message == 'DisC':
                opt = False
                print("You are now disconnected.")
                client.close()
                break
            elif message == 'The nickname is already in use. Please choose a new one.':
                # Prompt the user to input a new nickname
                
                nickname = input("Choose a new username: ")
                print ('this is the nickname ',nickname)
                client.send(nickname.encode('ascii')) # Send the new nickname to the server

            elif "Your nickname has been changed to" in message:
                nickname = message.split()[-1]  # Extract the new nickname
                print(f"Your nickname is now: {nickname}")
        # Optionally, update the client's display here
            else:
                print(message)
        except socket.error:
            # Handle socket errors (e.g., connection issues)
            print("Connection lost!")
            opt = False
            client.close()
            break

# Sending Messages To Server
def write():
    global opt
    global nickname
    while opt:
        try:
            message = '{}: {}'.format(nickname, input(''))
            if client.fileno() == -1:  # Check if the socket is closed
                print("Socket is closed, cannot send message.")
                break
            client.send(message.encode('ascii'))
        except socket.error:
            print("Error: Could not send message.")
            break
        

# Starting Threads For Listening And Writing
receive_thread = threading.Thread(target=receive)
receive_thread.start()

write_thread = threading.Thread(target=write)
write_thread.start()
