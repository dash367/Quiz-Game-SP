import socket
import random
import time

PORT = 5689                                        # The port number that will be used according to the project specifications.
SERVER = socket.gethostbyname(socket.gethostname())# The IP of the host that is using the server. 
ADDR = (SERVER, PORT)                              # The data that will be written on the packet to route it correctly(IP, and Port used).
FORMAT = "utf-8"                                   # Encoding format since the messages will be sent in binary format.
DIS_MESSAGE = "."                                  # The sent message in case of disconnecting from the server.
BUFFER_SIZE = 1024                                 # Maximum message size. 

server_connect = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Creates a new socket object with an IPv4 address and a data gram socket type for UDP.
server_connect.bind(ADDR)                          # Associates the socket with the specified address (IP and port).

clients = {}                                       # Initialize a dictionary for clients, IP and name.
scores = {}                                        # Initialize a dictionary for the scores of each connected client IP and score.
connections = 0                                    # The number of currently connected clients.


def handle_client():
    print(f"[LISTENING] Server is listening on {SERVER}")           # Start the server
    global connections

    while True:
        msg, address = server_connect.recvfrom(BUFFER_SIZE)         # Recieve messeges from clients
        msg = msg.decode(FORMAT)            

        if address not in clients:
            clients[address] = msg                                  # Define a client by his name
            scores[address] = 0                                     # Set his score to zero
            print(f"[NEW CONNECTION] {address} is known as '{msg}'")

            for client in clients:
                server_connect.sendto(f"{msg} joined the game".encode(FORMAT), client) # Notify all clients for a new connection

            connections += 1
            if connections < 2:
                server_connect.sendto("wait".encode(FORMAT), address) # Notify all clients to wait until there is players enough
            else:
                time.sleep(3)
                print(f"[PREPARING] The game should start soon!")
                for client in clients:
                    server_connect.sendto("start".encode(FORMAT), client) # Notify all clients that the game started
                time.sleep(3)
                print(f"[START] The game started!")
                start_game() # Start game
            continue

        username = clients[address]
        print(f"[{username} - {address}] {msg}")

        if msg == DIS_MESSAGE:                                             # If the client send the disconnection messege
            print(f"[DISCONNECTION] {username} at {address} disconnected.")
            del clients[address]
            del scores[address]
            connections -= 1
            continue

        server_msg = "Message received".encode(FORMAT)
        server_connect.sendto(server_msg, address)


def start_game():
    for round_num in range(1, 4):   # Randomly choose number of rounds
        print(f"[ROUND {round_num}] Starting round {round_num}...") 
        for client in clients:
            server_connect.sendto(f"[ROUND {round_num}] Get ready!".encode(FORMAT), client) # Notify all clients the round number

        num_questions = random.randint(2, 4)    # Randomly choose the number of questions for the current round
        for _ in range(num_questions):
            send_question_to_all_clients()      # Send the Question to all clients

        print(f"[ROUND {round_num}] Round {round_num} completed!")

    end_game() # End the game after rounds finishes


def send_question_to_all_clients():
    question = game_questions()
    question_msg = question["question"]
    for client in clients:
        server_connect.sendto(f"[QUESTION] {question_msg}".encode(FORMAT), client) # Notify all clients the new question and wait for their answers
    print("[QUESTION] sent to all players:", question_msg)
    collect_answers(question)


def collect_answers(question):
    start_time = time.time()
    received_answers = {}

    while time.time() - start_time < 15: # Set timer of 15s for each round
        try:
            server_connect.settimeout(15 - (time.time() - start_time))
            answer_msg, client = server_connect.recvfrom(BUFFER_SIZE)   # Collect answers from clients
            answer_msg = answer_msg.decode(FORMAT)

            if client not in clients:
                continue

            if client not in received_answers:
                received_answers[client] = answer_msg
        except socket.timeout:
            break

    for client, answer in received_answers.items():
        if answer.lower() == question["answer"].lower(): # If answer is correct
            scores[client] += 1
            print(f"[CORRECT ANSWER] {clients[client]} answered correctly! New score: {scores[client]}")
            server_connect.sendto(f"You answered correctly! Your score now is: {scores[client]}".encode(FORMAT), client)
        else:                                            # If answer is wrong
            print(f"[WRONG ANSWER] {clients[client]} answered incorrectly.")
            server_connect.sendto(f"You answered wrong! Your score still: {scores[client]}".encode(FORMAT), client)

    send_scoreboard() # Broadcast a scoreboard each question


def send_scoreboard():
    scoreboard = "[SCOREBOARD]\n" + "\n".join([f"{clients[client]}: {scores[client]}" for client in clients])
    print(scoreboard)
    for client in clients:
        server_connect.sendto(scoreboard.encode(FORMAT), client)


def end_game():
    print("[GAME OVER] Ending the game.")
    for client in clients:
        server_connect.sendto("game over".encode(FORMAT), client)
    print("[FINAL SCORES]")
    for client, score in scores.items():
        print(f"{clients[client]}: {score}")


def game_questions(): # Random questions database
    questions = [
        {"question": "What is the first animal to go to space?", "answer": "dog"},
        {"question": "Who is the author of '1984' novel?", "answer": "george orwell"},
        {"question": "What is the largest planet in our solar system?", "answer": "jupiter"},
        {"question": "Who painted the Mona Lisa?", "answer": "da vinci"},
        {"question": "Who was the responsible of the Holocaust?", "answer": "hitler"}
    ]
    return random.choice(questions)


print(f"[STARTING] server is starting...")
handle_client()
