import socket
import getpass
import random

SERVER_HOST = '140.113.235.151'
SERVER_PORT = 10001


def start_game_server():
    game_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    game_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    port = input("Enter port number(10000~60000): ")
    game_server.bind(('140.113.235.151', int(port)))
    game_server.listen(2)
    ip, port = game_server.getsockname()
    print(f"Game server {ip}:{port}")
    return game_server, ip, port



def register():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("--- Register ---")
    username = input("Enter USERNAME: ")
    password = getpass.getpass("ENTER PASSWORD: ")

    register_data = f"register {username} {password}"
    client_socket.send(register_data.encode())

    response = client_socket.recv(1024).decode()
    if response == "OK":
        print("Account registered successfully")
    elif response == "USERNAME TAKEN":
        print("Username already exists.")
    else:
        print("Resgistration failed")

    client_socket.close()



def login():
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((SERVER_HOST, SERVER_PORT))

    print("--- Login ---")
    username = input("Enter USERNAME: ")
    login_data = f"login {username}"
    client_socket.send(login_data.encode())

    response = client_socket.recv(1024).decode()
    if response == "FOUND":
        password = getpass.getpass("ENTER PASSWORD: ")
        client_socket.send(password.encode())

        response = client_socket.recv(1024).decode()
        if response == "OK":
            print("Login successfully")

            while True:
                
                print("1. Create room.")
                print("2. Join room.")
                print("3. Logout.")
                print("4. Receive invitation.")
                print("5. List online")

                choice = input("Enter your choice: ")

                if choice == '1':
                    create_room(client_socket)
                elif choice == '2':
                    client_socket.send("join room".encode())
                    response = client_socket.recv(1024).decode()

                    if response == "No public rooms available.":
                        print(response)
                    else:
                        print(response)
                        room_choice = input("Enter room number you want to join: ")
                        client_socket.send(room_choice.encode())
                        join_response = client_socket.recv(1024).decode()
                        client_socket.send("Okay".encode())

                        if "Game_server_info:" in join_response:
                            game_type = client_socket.recv(1024).decode()
                            _, _, ip, _, port = join_response.split(" ")
                            ip, port = ip.strip(","), int(port)

                            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            game_socket.connect((ip, int(port)))
                            game_socket.send("Connected to game server".encode())
                            response = game_socket.recv(1024).decode()
                            print(f"Received: {response}")#guset1
                            if game_type == "Ultimate Number":
                                play_ultimate_number_guest(game_socket)
                            elif game_type == "Rock-Paper-Scissor":
                                play_rock_paper_scissors(game_socket)
                            client_socket.sendall("Game Over".encode())
                        else:
                            print(join_response)

                elif choice == '3':
                    client_socket.send("logout".encode())
                    response = client_socket.recv(1024).decode()
                    if response == "LOGOUT_SUCCESS":
                        print("SUCCESS Logout successful.")
                        break
                    else:
                        print("ERROR Logout failed")
                        retry = input("Retry(yes/no): ")
                        if retry.lower() == "yes":
                            break
                elif choice == '4':
                    print("\n" + "="*30)
                    print("!!! You have a new game invite !!!")
                    print("="*30)

                    private_res = client_socket.recv(1024).decode()
                    print(private_res)
                    if private_res == "invite_G1":
                        respond = input("Do you want to join? (yes/no): ")
                        client_socket.send(respond.encode())
                        res = client_socket.recv(1024).decode()
                        if res == "accept":
                            print("---------------------------")
                            print("invitee accept")
                            print("---------------------------")
                            game_server_info = client_socket.recv(1024).decode()
                            print(game_server_info)
                            _, ip, port = game_server_info.split(" ")
                            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            game_socket.connect((ip, int(port)))
                            game_socket.send("Let's play the game".encode())#guest2
                            play_ultimate_number_guest(game_socket)
                            print("Socket closed")
                            client_socket.send("Game Over".encode())
                        elif res == "reject":
                            client_socket.send("private_reject".encode())
                            print("reject the invitation")

                    elif private_res == "invite_G2":
                        respond = input("Do you want to join? (yes/no): ")
                        client_socket.send(respond.encode())
                        res = client_socket.recv(1024).decode()
                        if res == "accept":
                            print("---------------------------")
                            print("invitee accept")
                            print("---------------------------")
                            game_server_info = client_socket.recv(1024).decode()
                            print(game_server_info)
                            _, ip, port = game_server_info.split(" ")
                            game_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                            game_socket.connect((ip, int(port)))
                            game_socket.send("Let's play the game".encode())
                            play_rock_paper_scissors(game_socket)
                            print("Socket closed")
                            client_socket.send("Game Over".encode())
                        elif res == "reject":
                            client_socket.send("private_reject".encode())
                            print("reject the invitation")
                elif choice == '5':
                    client_socket.send("list game lobby info".encode())
                    response = client_socket.recv(1024).decode()
                    print(response)
                        
                else:
                    print("ERROR unvalid choice.")

                
        elif response == "Password not correct":
            print("Password not correct.")
    elif response == "EXISTED":
        print("User already log in.")
    else:
        print("User doesn't exist.")
    
    client_socket.close()

def create_room(client_socket):
    client_socket.send("create room".encode())
    response = client_socket.recv(1024).decode()
    if response == "OK":
        game_type = select_game_type(client_socket)
        if game_type:
            room_type = select_room_type(client_socket)
            if room_type:
                if game_type == '1':  # Ultimate Number
                    handle_ultimate_number_room(client_socket, room_type)
                elif game_type == '2':  # Rock-Paper-Scissors
                    handle_rock_paper_scissors_room(client_socket, room_type)
            else:
                print("Room creation failed")
    else:
        print("Room creation failed")

def select_game_type(client_socket):
    print("Select a game type:")
    print("1. Ultimate Number")
    print("2. Rock-Paper-Scissors")
    game_type = input("Enter your choice: ")
    client_socket.send(game_type.encode())
    response = client_socket.recv(1024).decode()
    if response == "OK":
        return game_type
    return None

def select_room_type(client_socket):
    print("Select a room type:")
    print("1. Public Room")
    print("2. Private Room")
    room_type = input("Enter your choice: ")
    client_socket.send(room_type.encode())
    response = client_socket.recv(1024).decode()
    if response == "OK":
        return room_type
    return None

def handle_ultimate_number_room(client_socket, room_type):
    if room_type == '1':  # Public Room
        print("Public Room Created, waiting for players...")
        handle_public_room(client_socket, play_ultimate_number_host)
    elif room_type == '2':  # Private Room
        print("Private Room Created")
        handle_private_room(client_socket, play_ultimate_number_host)

def handle_rock_paper_scissors_room(client_socket, room_type):
    if room_type == '1':  # Public Room
        print("Public Room Created, waiting for players...")
        handle_public_room(client_socket, play_rock_paper_scissors)
    elif room_type == '2':  # Private Room
        print("Private Room Created")
        handle_private_room(client_socket, play_rock_paper_scissors)

def handle_public_room(client_socket, game_function):
    request = client_socket.recv(1024).decode()
    if "Please provide" in request:
        game_server, ip, port = start_game_server()
        print(f"Game server IP: {ip}, Port: {port}")
        client_socket.send(f"Game_Server_IP: {ip}, Port: {port}".encode())
        game_socket, address = game_server.accept()
        print(f"Game server connected to {address}")
        data = game_socket.recv(1024).decode()
        print(f"Received: {data}")
        game_socket.send("OK".encode())
        game_function(game_socket)
        print("Socket closed")
        client_socket.send("Game Over".encode())

def handle_private_room(client_socket, game_function):
    client_socket.send("gogo".encode())
    invite_players(client_socket)
    game_server, ip, port = start_game_server()
    print(f"Game server IP: {ip}, Port: {port}")
    client_socket.send(f"{ip} {port}".encode())
    game_socket, address = game_server.accept()
    print(f"Game server connected to {address}")
    data = game_socket.recv(1024).decode()
    print(f"Received: {data}")
    game_function(game_socket)
    print("Socket closed")
    client_socket.send("Game Over".encode())

def invite_players(client_socket):
    while True:
        while True:
            choice = input("Enter the choice(1. Invite 2. List Players): ")
            if choice == '1':
                client_socket.send("INVITE".encode())
                res = client_socket.recv(1024).decode()
            
                invitee = input("Enter the player name you want to invite: ")
                client_socket.send(invitee.encode())
                break

            elif choice == '2':
                client_socket.send("LIST".encode())
                list_players = client_socket.recv(1024).decode()
                print(list_players)
            
        response = client_socket.recv(1024).decode()
        if response == "invite_receive":
            print("Received!!")


        res = client_socket.recv(1024).decode()
        if res == "accept":
            break
        elif res == "reject":
            print("---------------------------")
            print("Invitation rejected")
            print("---------------------------")
    print("---------------------------")
    print("Invitation accepted")
    print("---------------------------")


def play_rock_paper_scissors(game_socket):
    print("----------------------------")
    print("Game Started: Rock-Paper-Scissors")

    choices = {"1": "Rock", "2": "Paper", "3": "Scissors"}
    print("Choose your move:")
    print("1. Rock")
    print("""
        X   X   X  X XX
        XXXXXXXXXXXX XX
        XXXXXXXXXXXX XX
        XXXXXXXXXXXX  
    """)
    print("2. Paper")
    print("""
        X    X    X
        X    X    X
        X    X    X
    X   X    X    X
    XX X  X  X   X    XX
    XX XXXXXXXXXXXX   XX
    XXXXXXXXXXXX XX
    XXXXXXXXXXXX 
    """)
    print("3. Scissors")
    print("""
        X    X
        X    X
        X    X
        X    X
    X  X   X    
    XXXXXXXXXXXX   
    XXXXXXXXXXXX 
    XXXXXXXXXXXX     
    """)

    # 玩家選擇動作
    while True:
        player_choice = input("Enter your choice (1-3): ")
        if player_choice in choices:
            print(f"You chose: {choices[player_choice]}")
            break
        else:
            print("Invalid choice, please try again.")

    # 傳送玩家選擇給對手
    game_socket.send(player_choice.encode())

    # 接收對手的選擇
    opponent_choice = game_socket.recv(1024).decode()
    print(f"Opponent chose: {choices[opponent_choice]}")

    # 判斷遊戲結果
    if player_choice == opponent_choice:
        result = "It's a tie!"
    elif (player_choice == "1" and opponent_choice == "3") or \
         (player_choice == "2" and opponent_choice == "1") or \
         (player_choice == "3" and opponent_choice == "2"):
        result = "You win!"
    else:
        result = "You lose!"

    # 顯示結果並通知伺服器遊戲結束
    print(f"Game Over! {result}")
    game_socket.send("Game Over".encode())
    game_socket.close()
    print("----------------------------")

def play_ultimate_number_host(game_socket):
    print("----------------------------")
    print("Game Started: Ultimate Number")

    # 隨機生成目標數字
    target_number = random.randint(1, 1000)
    game_socket.send(f"Target:{target_number}".encode())

    lower_bound, upper_bound = 1, 1000  # 初始猜測範圍

    while True:
        # 顯示當前猜測範圍
        print(f"Current range: {lower_bound} - {upper_bound}")

        # 主機玩家進行猜測
        while True:
            host_guess = int(input(f"Your guess ({lower_bound}-{upper_bound}): "))
            if lower_bound <= host_guess <= upper_bound:
                break
            else:
                print("Invalid guess, please try again.")

        # 判斷是否猜中
        if host_guess == target_number:
            game_socket.send(f"{host_guess};Range update: {lower_bound}-{upper_bound}".encode())  # 傳送猜測和範圍更新
            print("Congratulations! You guessed the correct number!")
            break

        # 根據猜測更新範圍
        if host_guess < target_number:
            lower_bound = host_guess + 1
        else:
            upper_bound = host_guess - 1
        game_socket.send(f"{host_guess};Range update: {lower_bound}-{upper_bound}".encode())  # 傳送更新後的範圍

        # 等待並處理對手的猜測
        print("Waiting for the opponent's guess...")
        data = game_socket.recv(1024).decode()
        print(f"Received data from opponent: '{data}'")
        if not data:
            continue
        opponent_guess, range_update = data.split(";")
        opponent_guess = int(opponent_guess.strip())
        print(f"Opponent guessed: {opponent_guess}")

        # 判斷對手是否猜中
        if opponent_guess == target_number:
            print("Game Over! Opponent guessed the correct number. You lose!")
            break

        # 更新猜測範圍
        lower_bound, upper_bound = map(int, range_update.split(":")[1].split("-"))

    # 關閉遊戲套接字
    game_socket.close()
    print("----------------------------")

def play_ultimate_number_guest(game_socket):
    print("----------------------------")
    print("Game Started: Ultimate Number")

    # 接收主機發送的目標數字
    data = game_socket.recv(1024).decode()
    if "Target:" in data:
        target_number = int(data.split(":")[1].strip())
    else:
        print("Error: Target number not received.")
        return

    lower_bound, upper_bound = 1, 1000  # 初始猜測範圍

    while True:
        # 等待並處理主機的猜測
        print("Waiting for the host's guess...")
        data = game_socket.recv(1024).decode()
        print(f"Received data from host: '{data}'")
        
        if not data:
            continue
        host_guess, range_update = data.split(";")  # 根據分隔符拆分資料
        host_guess = int(host_guess.strip())
        print(f"Host guessed: {host_guess}")

        # 更新範圍
        print(f"Updated range: {range_update}")
        lower_bound, upper_bound = map(int, range_update.split(":")[1].split("-"))

        # 判斷主機是否猜中
        if host_guess == target_number:
            print("Game Over! Host guessed the correct number. You lose!")
            break

        # 玩家進行猜測
        while True:
            player_guess = int(input(f"Your guess ({lower_bound}-{upper_bound}): "))
            if lower_bound <= player_guess <= upper_bound:
                break
            else:
                print("Invalid guess, please try again.")

        # 判斷玩家是否猜中
        if player_guess == target_number:
            game_socket.send(f"{player_guess};Range update: {lower_bound}-{upper_bound}".encode())
            print("Congratulations! You guessed the correct number!")
            break

        # 更新範圍並傳送猜測結果給主機
        if player_guess < target_number:
            lower_bound = player_guess + 1
        else:
            upper_bound = player_guess - 1
        game_socket.send(f"{player_guess};Range update: {lower_bound}-{upper_bound}".encode())

    # 關閉遊戲套接字
    game_socket.close()
    print("----------------------------")



if __name__ == "__main__":
    port = input("Enter server port (default is 10001): ")
    port = int(port) if port else 10001
    SERVER_PORT=port
    while True:
        print("1. Resgister Account")
        print("2. Login")
        choice = input("Enter your choice: ")
        if choice == '1':
            register()
        elif choice == '2':
            login()
        else:
            print("ERROR unvalid choice.")



        