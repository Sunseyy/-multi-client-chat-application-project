# Connection Data
import socket
import sys
import threading

import re
host = '127.0.0.1'
port = 55555

# Starting Server
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((host, port))
server.listen()


# Lists For Clients and Their Nicknames
clients = []
nicknames = []
passwords=[]
status=[]

Channels={}
channel_passwords={}
max_users={}
max_users_dict = {}
# Sending Messages To All Connected Clients
def broadcast(message,channel):
    if channel == None:
        for client in clients:
            try:
                index = clients.index(client)
                if status[index] == 'offline':
                    pass  # Skip offline clients
                else:
                    client.send(message)  # Send message to online clients
            except (socket.error, ConnectionAbortedError):
                
                # You can log the error here but won't remove the client
                pass  # Continue to the next client
    else:
        for client in Channels[channel]:
            try:
                client.send(f"<{channel}>".encode('utf-8'))

                client.send(message)
            except Exception as e:
                
                Channels[channel].remove(client)
                if client in clients:
                    index = clients.index(client)
                    clients.remove(client)
                    client.close()
                    nickname = nicknames[index]
                    nicknames.remove(nickname)
                    broadcast(f'{nickname} left the chat! Bye bye'.encode('ascii'), channel)
def display_channels(channels, client):
    if not channels:
        client.send("No channels available.".encode('ascii'))
    else:
        # Prepare the response message with all channels and user counts
        message = "Available channels:\n"
        for channel, users in channels.items():
            message += f"Channel: {channel}, Users: {len(users)}\n"
        
        client.send(message.encode('ascii'))  # Send the compiled message


# Handling Messages From Clients
# Handling Messages From Clients
def handle(client):
    current_channel=None
    try:
        while True:
            message = client.recv(1024)  # Decode the message to a string
            
            message_decode=message.decode('utf-8') 
            if "/help" in message_decode:  # Check if /help is in the message
                
                client.send(b'\033[1;34m/help - Show this help message\n/listUsers - List all users\n/join [channel] - Join a channel\n/quit [channel] - Leave a channel\n/nickname [new_nickname] - Change your nickname\n/disconnect - Disconnect from the server\n /join <channell> \n /create <channel> \n /prv <destination> <messg> \n\033[0m')

            elif "/listUsers" in message_decode:
                
                handle_list(nicknames,status,client)
            elif "/ListChannels" in message_decode:
                display_channels(Channels,client)
            elif "/disconnect" in message_decode:
                current_nickname= message.split()[1]
                i =handle_disconnection(current_nickname,status)
                status[i]='Offline'
                client.send('DisC'.encode('ascii'))
                print(clients)

            elif "/join" in message_decode:
                parts = message_decode.split()
                if len(parts) < 2:  # Ensure the command has a channel name
                    client.send('\033[1;33mUsage: /join <channel_name>\033[0m'.encode('ascii'))  # Yellow for usage
                    return

                channel_name = parts[2]  # Get the channel name
                if channel_name not in Channels:  # Check if the channel exists
                    client.send(f'\033[1;31mChannel {channel_name} does not exist.\033[0m'.encode('ascii'))  # Red for error
                else:
                    # Check if the channel is at maximum capacity
                    if len(Channels[channel_name]) >= max_users_dict[channel_name]:
                        client.send(f'\033[1;31mChannel {channel_name} is full. Max number of users is {max_users_dict[channel_name]}.\033[0m'.encode('ascii'))  # Red for full channel
                    else:
                        if channel_name in channel_passwords:
                            # Request password input from the user
                            client.send('\033[1;33mThis channel requires a password. Please enter the password.\033[0m'.encode('ascii'))  # Yellow for password prompt
                            # Wait for the user to send the password
                            password_message = client.recv(1024).decode('utf-8')
                            entered_password = password_message.split(':', 1)[1].strip()  # Extract and trim the password
                            print(entered_password)
                            if entered_password == channel_passwords[channel_name]:
                                Channels[channel_name].append(client)
                                current_channel = channel_name
                                client.send(f'\033[1;32mSuccessfully joined channel {channel_name}.\033[0m'.encode('ascii'))  # Green for success

                                # Notify other clients in the channel about the new member
                                broadcast(f'{nicknames[clients.index(client)]} has joined {channel_name}.'.encode('ascii'), channel_name)
                            else:
                                # Incorrect password
                                client.send('\033[1;31mIncorrect password. Please try again.\033[0m'.encode('ascii'))  # Red for incorrect password
                        else:
                            # No password required, just add the client to the channel
                            Channels[channel_name].append(client)
                            current_channel = channel_name
                            client.send(f'\033[1;32mSuccessfully joined channel {channel_name}.\033[0m'.encode('ascii'))  # Green for success

                            # Notify other clients in the channel about the new member
                            broadcast(f'{nicknames[clients.index(client)]} has joined {channel_name}.'.encode('ascii'), channel_name)

            elif "/create" in message_decode:
                parts = message_decode.split()

                if len(parts) < 2:  # Ensure the command has a channel name
                    client.send('\033[1;33mUsage: /create <channel_name>\033[0m'.encode('ascii'))  # Yellow for usage
                    return

                channel_name = parts[2]
                if channel_name in Channels:
                    client.send('\033[1;31mThis channel already exists. If you want to join it, please use /join.\033[0m'.encode('ascii'))  # Red for error
                else:
                    if current_channel is not None:
                        Channels[current_channel].remove(client)

                    client.send(f'\033[1;34mChannel {channel_name} created. Now, please specify the max number of users (between 2 and 100).\033[0m'.encode('utf-8'))  # Blue for channel creation

                    message = client.recv(1024).decode('utf-8').split()

                    Channels[channel_name] = []
                    max_users = int(message[1])
                    if 2 <= max_users <= 100:
                        # Save the max users for the channel
                        max_users_dict[channel_name] = max_users
                        print(max_users_dict[channel_name])
                        client.send(f'\033[1;34mMax users for {channel_name} set to {max_users}. Now, please enter a password for the channel.\033[0m'.encode('ascii'))  # Blue for password request

                        # Wait for the user to enter a password
                        password_message = client.recv(1024).decode('utf-8').split(':', 1)[1].strip()
                        channel_passwords[channel_name] = password_message
                        client.send(f'\033[1;32mPassword for {channel_name} set. You can now join the channel.\033[0m'.encode('ascii'))  # Green for success

                        # Add the client to the channel
                        Channels[channel_name].append(client)
                        current_channel = channel_name
                        # Broadcast the channel creation to other clients
                        broadcast(f'{nicknames[clients.index(client)]} created and joined {channel_name}.'.encode('ascii'), channel_name)
                    else:
                        client.send(f'\033[1;31mInvalid number of users. Please specify a number between 2 and 100.\033[0m'.encode('ascii'))  # Red for invalid input

            elif "/quit" in message_decode:
                if current_channel is None:
                    client.send('\033[1;33mYou are not currently in any channel.\033[0m'.encode('ascii'))  # Yellow for not in any channel
                else:
                    # Remove the client from the channel's list
                    Channels[current_channel].remove(client)

                    # Notify the channel about the user leaving
                    nickname = nicknames[clients.index(client)]
                    broadcast(f"\033[1;33m{nickname} has left the channel {current_channel}.\033[0m".encode('ascii'), current_channel)

                    client.send(f'\033[1;32mYou have left the channel {current_channel}.\033[0m'.encode('ascii'))  # Green for success
                    # Set current_channel to None to indicate that the user is no longer in a channel
                    current_channel = None

            elif "/nickname" in message_decode:
                change_nickname(client, message_decode, current_channel)

            elif "/prv" in message_decode:
                _, prv, target_nickname, *msg = message.split()

                # Decode the target_nickname and msg from bytes to string
                target_nickname = target_nickname.decode('utf-8')  # Decode target_nickname to string
                msg = [part.decode('utf-8') for part in msg]  # Decode each byte in the msg list
                msg = ' '.join(msg)  # Now you can safely join the decoded strings

                if target_nickname in nicknames:
                    target_index = nicknames.index(target_nickname)
                    target_client = clients[target_index]

                    # Send the private message to the target user
                    target_client.send(f'\033[1;35mPrivate message from {nicknames[clients.index(client)]}: {msg}\033[0m'.encode('ascii'))  # Magenta for private message

                    # Notify the client that the message was sent
                    client.send(f'\033[1;35mPrivate message to {target_nickname}: {msg}\033[0m'.encode('ascii'))  # Magenta for success
                else:
                    client.send(f'\033[1;31mUser {target_nickname} not found.\033[0m'.encode('ascii'))  # Red for error

            else:
                if current_channel is not None:
                    broadcast(message, current_channel)
                else:
                    broadcast(message, None)

    except (OSError, ConnectionAbortedError) as e:
        # Catch errors when trying to communicate with a disconnected client
        pass
def handle_list(nicknames,status,client):
    for i in range(len(nicknames)):
        client.send(f'{nicknames[i]} : {status[i]}\n'.encode('utf-8'))
        
# Mark client as offline when they disconnect
def handle_disconnection(currentNickname, status):
    
    for i in range(len(nicknames)):
        if nicknames[i] == currentNickname:
           break  # Mark the client as offline
    return i

def change_nickname(client, message_decode,current_channel):
    # Split the message into command and nickname
    parts = message_decode.split()
    
    if len(parts) < 2:
        # If the message doesn't contain a new nickname
        client.send("Usage: /nickname <new_nickname>".encode('ascii'))
        return
    
    new_nickname = parts[2]  # Get the new nickname from the message
    
    
    
    # Get the current nickname index
    current_index = clients.index(client)
    
    # Change the nickname
    old_nickname = nicknames[current_index]
    nicknames[current_index] = new_nickname
    
    # Notify the client about the change
    client.send(f"Your nickname has been changed to {new_nickname}".encode('ascii'))
    
    # Optionally, broadcast to other clients in the same channel about the nickname change
    # Broadcast can be done here if you want to notify others about the nickname change
    broadcast(f"{old_nickname} is now known as {new_nickname}.".encode('ascii'), current_channel)


def shutdown_server():
    print("Server is shutting down...")
    for client in clients:
        client.close()  # Close all client connections
    server.close()  # Close the server socket
    sys.exit()  # Exit the program


def listen_for_shutdown():
    while True:
        # Wait for user input from the server console
        command = input()
        if command == '/shutdown':
            print("Shutdown command received from server console.")
            shutdown_server()
            break  # Exit the loop and shut down the server



# Receiving / Listening Function
# Receiving / Listening Function
def receive():
    try:
        while True:
            print("Server is running...")  # Server running message
            # Accept Connection
            client, address = server.accept()
            print("Connected with {}".format(str(address)))

            # Request And Store Nickname
            client.send('username'.encode('ascii'))
            nickname = client.recv(1024).decode('ascii')

            client.send('password'.encode('ascii'))
            passwordC=client.recv(1024).decode('ascii')
            

            # Check if the nickname is already in use
            if nickname in nicknames and status[nicknames.index(nickname)] == 'Offline':
               
                
                index = nicknames.index(nickname)
                if passwordC == passwords[index]:
                    
                    clients[index] = client
                    status[index] = 'Online'  # Set status to online
                    client.send(f"Welcome back, {nickname}!".encode('ascii'))
                else:
                    
                    client.send("DisC".encode('ascii'))

                    
            elif nickname in nicknames  and status[nicknames.index(nickname)] == 'Online':
                
                client.send("DisC".encode('ascii'))
               
                    
            if nickname not in nicknames:
                
                nicknames.append(nickname)
                passwords.append(passwordC)
                
                status.append('Online')
                clients.append(client)

            # Print and Broadcast Nickname
            print("Nickname is {}".format(nickname))
            broadcast("{} joined!".format(nickname).encode('ascii'),None)
            client.send('Connected to server!'.encode('ascii'))


            # Start Handling Thread For Client
            thread = threading.Thread(target=handle, args=(client,))
            thread.start()

    except (OSError, ConnectionAbortedError) as e:
        # Catch errors when trying to communicate with a disconnected client
        print(f"Error with client {client} disconnected unexpctedly !")
        
def send_private_message(sender, recipient, message):
    if recipient in nicknames:
        # Find the index of the recipient client
        recipient_index = nicknames.index(recipient)
        recipient_client = clients[recipient_index]
        
        # Send the private message to the recipient
        recipient_client.send(f"Private message from {sender}: {message}".encode('utf-8'))
        sender_client = clients[nicknames.index(sender)]
        
        # Acknowledge to the sender that the message was sent
        sender_client.send(f"Private message sent to {recipient}: {message}".encode('utf-8'))
    else:
        # If the recipient is not found
        sender_client = clients[nicknames.index(sender)]
        sender_client.send(f"Error: User {recipient} not found.".encode('utf-8'))


command_thread = threading.Thread(target=listen_for_shutdown)
command_thread.start()
receive()