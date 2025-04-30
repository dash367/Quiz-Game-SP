import socket

PORT = 5689
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DIS_MESSAGE = "."
BUFFER_SIZE = 1024

client_connect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

def send(msg):
    try:
        if msg == DIS_MESSAGE:
            print("Disconnecting from server...")
            client_connect.sendto(DIS_MESSAGE.encode(FORMAT), ADDR)
            client_connect.close()
            return False
        else:
            message = msg.encode(FORMAT)
            client_connect.sendto(message, ADDR)
            server_msg, _ = client_connect.recvfrom(BUFFER_SIZE)
            print(f"[SERVER]: {server_msg.decode(FORMAT)}")
            return True
    except socket.timeout:
        print("[ERROR]: No response from server, disconnecting...")
        return False

def server_connection():
    client_name = input("Please enter your username: ")
    client_connect.sendto(client_name.encode(FORMAT), ADDR)
    print("Connected to the server.")
    
    while True:
        server_msg, _ = client_connect.recvfrom(BUFFER_SIZE)
        message = server_msg.decode(FORMAT)
        
        if message == "start":
            print("The game will start soon, be prepared!")
            break
        elif "joined the game" in message:
            print(f"[INFO]: {message}")
        elif message == "wait":
            print("Please wait for other players to join...")
            
    return True

def main():
    if server_connection():
        while True:
            try:
                server_msg, _ = client_connect.recvfrom(BUFFER_SIZE)
                message = server_msg.decode(FORMAT)

                if message == "game over":
                    print("The game has ended. Thank you for playing!")
                    break
                elif "[QUESTION]" in message:
                    print(f"{message}")
                    answer = input("Your answer: ")
                    if not send(answer):
                        break
                elif "[SCOREBOARD]" in message:
                    print(f"{message}")
                else:
                    print(f"[INFO]: {message}")
            except socket.timeout:
                print("[ERROR]: Server response timeout. Exiting game.")
                break

if __name__ == "__main__":
    client_connect.settimeout(15)
    main()
