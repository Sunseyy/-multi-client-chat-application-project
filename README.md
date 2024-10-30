# Multi-Client Chat Application

This project is a multi-client chat application developed using socket programming and multithreading in Python. It demonstrates network programming, concurrent programming, and basic security concepts by enabling multiple clients to communicate with each other via a server.

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Commands](#commands)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## Features

- Handles multiple client connections simultaneously using threads
- Allows clients to send and receive messages
- Supports private chat rooms (channels)
- Implements join/leave functionality for channels
- Supports broadcasting messages to all clients
- Includes basic commands (/help, /list, /join, /leave, etc.)
- Provides user presence notifications
- Basic user authentication
- Allows users to set and change nicknames
- Displays active user list and user status (online/offline)

## Requirements

- Python 3.x

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/multi-client-chat-app.git
    cd multi-client-chat-app
    ```

2. Install the required packages (if any):
    ```sh
    pip install -r requirements.txt
    ```

## Usage

### Running the Server

1. Navigate to the project directory.
2. Run the server script:
    ```sh
    python server.py
    ```
3. The server will start and listen for client connections on `0.0.0.0:5555`.

### Running the Client

1. Navigate to the project directory.
2. Run the client script:
    ```sh
    python client.py
    ```
3. The client will connect to the server at `127.0.0.1:5555`.

### Commands

- `/create [channel_name]`: Create a new private channel.
- `/join [channel_name]`: Join an existing private channel.
- `/leave`: Leave the current channel.
- `/list`: List all available channels.
- `/help`: Show a list of available commands.
