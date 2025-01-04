import socket
import threading
import time
import os

USER_DATA_FILE = "users.txt"

HOST = '140.113.235.151'
PORT = 10001

CHAT_PORT = 10003  # 聊天伺服器的埠號
chat_clients = []  # 所有連接到聊天伺服器的客戶端

pause_event = threading.Event()
SERVER_GAME_FOLDER = "my_games"
if not os.path.exists(SERVER_GAME_FOLDER):
    os.makedirs(SERVER_GAME_FOLDER)


class Player:
    def __init__(self, username, status="idle", client_socket=None):
        self.username = username
        self.status = status
        self.client_socket = client_socket
        self.invitations = []

class Public_Room:
    def __init__(self, creator, game_type, status):
        self.creator = creator
        self.game_type = game_type
        self.status = status
        self.creator_socket = None
        self.num_players = 1

class Private_Room:
    def __init__(self, creator, game_type, status):
        self.creator = creator
        self.game_type = game_type
        self.creator_socket = None
        self.invited_players = []



registered_users = {}
online_users = []
clients = []
public_rooms = []
private_rooms = []


# 確保伺服器有一個遊戲資料夾
LOBBY_GAME_FOLDER = "games"
if not os.path.exists(LOBBY_GAME_FOLDER):
    os.makedirs(LOBBY_GAME_FOLDER)
GAME_INFO_FILE = os.path.join(LOBBY_GAME_FOLDER, "game_info.txt")

# 確保遊戲資訊檔案存在
if not os.path.exists(GAME_INFO_FILE):
    open(GAME_INFO_FILE, "w").close()

def broadcast_message(message):
    """向所有聊天室用戶廣播訊息"""
    for client in chat_clients:
        try:
            client.send(message.encode())
        except:
            chat_clients.remove(client)

def handle_chat_client(client_socket, address):
    """處理聊天室用戶的訊息"""
    chat_clients.append(client_socket)
    broadcast_message(f"🎉 A user joined the chat room from {address}! 🎉")

    while True:
        try:
            data = client_socket.recv(1024).decode()
            if not data or data.lower() == "/leave":
                broadcast_message(f"🚪 A user left the chat room from {address}.")
                chat_clients.remove(client_socket)
                break
            broadcast_message(data)
        except:
            chat_clients.remove(client_socket)
            break
    client_socket.close()

def accept_chat_clients():
    """接受聊天室用戶的連接"""
    while True:
        client_socket, address = chat_server.accept()
        threading.Thread(target=handle_chat_client, args=(client_socket, address)).start()


def load_users():
    """從文件中讀取用戶數據"""
    if not os.path.exists(USER_DATA_FILE):
        return {}

    users = {}
    with open(USER_DATA_FILE, "r") as file:
        for line in file:
            username, password = line.strip().split(",")
            users[username] = password
    return users

def save_user(username, password):
    """將新用戶追加寫入文件"""
    with open(USER_DATA_FILE, "a") as file:
        file.write(f"{username},{password}\n")

def send_invitation_notification(username, message):
    """
    向聊天室內的特定玩家發送邀請通知。
    :param username: 被邀請玩家的用戶名
    :param message: 要發送的通知訊息
    """
    for client in chat_clients:
        try:
            if client.username == username:  # 假設 client 有 username 屬性
                client.socket.send(f"INVITATION: {message}".encode())
                print(f"Invitation notification sent to {username}")
                break
        except Exception as e:
            print(f"Error sending notification to {username}: {e}")


def GET_lobby_status():
    lobby_status = "✧･ﾟ: *✧･ﾟ:*  🎮 Game Lobby 🎮  *:･ﾟ✧*:･ﾟ✧\n\n"

    if online_users:
        lobby_status += "💻 Online Users 💻\n"
        for player in online_users:
            lobby_status += f"• {player.username} | Status: {player.status} ✨\n"
    else:
        lobby_status += "😔 No players are online at the moment.\n"

    lobby_status += "\n"

    if public_rooms:
        lobby_status += "🚪 Available Public Rooms 🚪\n"
        for idx, room in enumerate(public_rooms, start=1):
            lobby_status += f"{idx}. 🌟 Room by {room.creator} | Game: {room.game_type} | Status: {room.status} 🎲\n"
    else:
        lobby_status += "🚫 No public rooms available right now. Try creating one! 🎉\n"

    lobby_status += "\n✧･ﾟ: *✧･ﾟ:* ✨ End of Lobby ✨ *:･ﾟ✧*:･ﾟ✧\n"

    return lobby_status


def display_lobby_status():
    print("✧･ﾟ: *✧･ﾟ:* 🎮 Welcome to the Game Lobby 🎮 *:･ﾟ✧*:･ﾟ✧\n")

    if online_users:
        print("💻 Online Users 💻")
        for player in online_users:
            print(f"• {player.username} | Status: {player.status} ✨")
    else:
        print("😔 No players are online at the moment.")
    print()

    if public_rooms:
        print("🚪 Available Public Rooms 🚪")
        for idx, room in enumerate(public_rooms, start=1):
            print(f"{idx}. 🌟 Room by {room.creator} | Game: {room.game_type} | Status: {room.status} 🎲")
    else:
        print("🚫 No public rooms available right now. Try creating one! 🎉")
    
    print("\n✧･ﾟ: *✧･ﾟ:* ✨ End of Lobby ✨ *:･ﾟ✧*:･ﾟ✧\n")



def handle_registration(client_socket, data):
    try:
        _, username, password = data.split()

        if username in registered_users:
            client_socket.send("USERNAME TAKEN".encode())
        else:
            registered_users[username] = password
            save_user(username, password)  # 新增：保存用戶到文件
            client_socket.send("OK".encode())
    except Exception as e:
        client_socket.send("ERROR".encode())
        print(f"Registration failed: {e}")


def send_invitation(inviter, invitee):
    invitee_player = next((player for player in online_users if player.username == invitee), None)
    
    if invitee_player is not None:
        if invitee_player.status == "idle":
            invitee_player.client_socket.send(f"INVITATION {inviter}".encode())
            return True
        else:
            print(f"⚠️ {invitee} is currently busy.")
    else:
        print(f"🚫 {invitee} is not online.")
    
    return False



def handle_client(client_socket, address):
    global joiner
    global Game_room
    global tmp
    global tmp2
    clients.append(client_socket)
    current_player = None
    current_room = None
    
    while True:
        try:
            data = client_socket.recv(1024).decode()
            print(data)
            if not data:
                break
            
            if data.startswith("register"):
                handle_registration(client_socket, data)

            elif data.startswith("login"):
                _, username = data.split()
                response = "FOUND" if username in registered_users else "NOT FOUND"
                if any(player.username == username for player in online_users):
                    response="EXISTED"
                client_socket.send(response.encode())

                if response == "FOUND":
                    password = client_socket.recv(1024).decode()
                    if password == registered_users.get(username):
                        broadcast_message(f"🟢 {username} logged in.")
                        current_player = Player(username, "idle", client_socket)
                        online_users.append(current_player)
                        client_socket.send("OK".encode())
                    else:
                        client_socket.send("Password not correct".encode())
            elif data.startswith("private_room"):
                if private_rooms:
                    client_socket.send("Yes".encode())
                else:
                    client_socket.send("No".encode())
            elif data.startswith("LIST_GAMES"):
                # 列出伺服器中的遊戲
                if os.path.getsize(GAME_INFO_FILE) == 0:
                    client_socket.send("No games available.".encode())
                else:
                    with open(GAME_INFO_FILE, "r") as info_file:
                        games = info_file.readlines()
                    formatted_games = "Name / Author / Description\n"
                    formatted_games += "\n".join(game.strip().replace(";", " / ") for game in games)
                    client_socket.send(formatted_games.encode())

            elif data.startswith("UPLOAD_GAME"):
                _, game_name, description, uploader = data.split(";", 3)
                if not game_name.endswith(".py"):
                    client_socket.send("Only .py files are allowed.".encode())
                else:    
                    file_path = os.path.join(LOBBY_GAME_FOLDER, game_name)
                    with open(file_path, "wb") as f:
                        while True:
                            print("recive chunk")
                            data_file = client_socket.recv(1024)
                            if data_file == b"EOF":
                                print("recive EOF")
                                break
                            f.write(data_file)
                    time.sleep(3)
                    print("file success")
                    # 儲存遊戲資訊到 game_info.txt
                    with open(GAME_INFO_FILE, "a") as info_file:
                        info_file.write(f"{game_name};{uploader};{description}\n")
                    print("game info sucsess")
                print("uploaded successfully.")
                client_socket.send(f"{game_name} uploaded successfully.".encode())

            
            elif data.startswith("GAMEEEEE"):
                _, game_name = data.split()
                file_path = os.path.join(LOBBY_GAME_FOLDER, game_name)
                if os.path.exists(file_path):
                    with open(file_path, "rb") as f:
                        while chunk := f.read(1024):
                            client_socket.send(chunk)
                    print("send EOF.")
                    time.sleep(1)
                    client_socket.send(b"EOF")
                else:
                    client_socket.send(f"{game_name} does not exist.".encode())


            elif data.startswith("DOWNLOAD_GAME"):
                _, game_name = data.split()
                if not game_name.endswith(".py"):
                    client_socket.send("Only .py files are allowed.".encode())
                else:
                    file_path = os.path.join(LOBBY_GAME_FOLDER, game_name)
                    if os.path.exists(file_path):
                        with open(file_path, "rb") as f:
                            while chunk := f.read(1024):
                                client_socket.send(chunk)
                        client_socket.send(b"EOF")
                    else:
                        client_socket.send(f"{game_name} does not exist.".encode())

            elif data.startswith("logout"):
                if current_player:
                    try:
                        broadcast_message(f"🔴 {current_player.username} logged out.")
                        online_users.remove(current_player)
                        clients.remove(client_socket)
                        client_socket.send("LOGOUT_SUCCESS".encode())
                        display_lobby_status() 
                        break
                    except Exception as e:
                        print(f"Error: {e}")
                        client_socket.send("LOGOUT_FAILED".encode())
            elif data.startswith("create"):
                if current_player.status == "idle":
                    current_player.status = "In Room"
                    client_socket.send("OK".encode())
                    game_type = client_socket.recv(1024).decode()
                    client_socket.send("OK".encode())
                    ensure = client_socket.recv(1024).decode()
                    print(ensure)
                    if not ensure:
                        break
                    elif ensure.startswith("GAMEEEEE"):
                        _, game_name = ensure.split()
                        file_path = os.path.join(LOBBY_GAME_FOLDER, game_name)
                        if os.path.exists(file_path):
                            with open(file_path, "rb") as f:
                                while chunk := f.read(1024):
                                    client_socket.send(chunk)
                            print("send EOF.")
                            time.sleep(1)
                            client_socket.send(b"EOF")
                        else:
                            client_socket.send(f"{game_name} does not exist.".encode())
                            
                    if game_type == "1":  # todo Ultimate Number
                        room_type = client_socket.recv(1024).decode()
                        if room_type == "1": # Public Room
                            broadcast_message(f"🎲 {current_player.username} created a public room.")
                            current_room = Public_Room(current_player.username, "Ultimate Number", "Waiting")
                            current_room.creator_socket = client_socket
                            public_rooms.append(current_room)
                            client_socket.send("OK".encode())

                        elif room_type == "2": # Private Room
                            current_room = Private_Room(current_player.username, "Ultimate Number", "Waiting")
                            current_room.creator_socket = client_socket
                            private_rooms.append(current_room)
                            client_socket.send("OK".encode())
                            res = client_socket.recv(1024).decode()

                            tmp, tmp2 = 1, 1

                            if res == "gogo":
                                while True:
                                    res = client_socket.recv(1024).decode()
                                    player_idle_list = " ".join(player.username for player in online_users if player.status == "idle")

                                    if res == "INVITE" and player_idle_list:
                                        client_socket.send(player_idle_list.encode())
                                        invite_phase = True
                                    elif res == "LIST":
                                        client_socket.send(f"Available_Player: {player_idle_list}".encode() if player_idle_list else "NO_IDLE_PLAYERS".encode())
                                        invite_phase = False
                                    
                                    if invite_phase:
                                        invitee = client_socket.recv(1024).decode()
                                        # 發送邀請通知給聊天室內的被邀請玩家
                                        notification_message = f"{current_player.username} invited you to join a game!"
                                        send_invitation_notification(invitee, notification_message)
                                        print(f"==============\nInviter chosen: {invitee}\n==============")
                                        client_socket.send("invite_receive".encode())

                                        invitee_socket = next((player.client_socket for player in online_users if player.username == invitee), None)
                                        print(f"==============\nInvitee socket: {invitee_socket}\n==============")

                                        invitee_socket.send("invite_G1".encode())
                                        time.sleep(10)

                                        if tmp == 2:
                                            invitee_socket.send("accept".encode())
                                            client_socket.send("accept".encode())
                                            game_server_info = client_socket.recv(1024).decode()
                                            print(f"Game server info: {game_server_info}")
                                            invitee_socket.send(f"Game_server_info: {game_server_info}".encode())

                                            for player in online_users:
                                                if player.username == invitee:
                                                    player.status = "In Game"
                                                    break

                                            current_player.status = "In Game"
                                            joiner = Player(invitee, "In Game", invitee_socket)
                                            break
                                        elif tmp == 1:
                                            invitee_socket.send("reject".encode())
                                            time.sleep(5)
                                            if tmp2 == 2:
                                                client_socket.send("reject".encode())

                    elif game_type == "2":
                        room_type = client_socket.recv(1024).decode()
                        if room_type == "1":
                            broadcast_message(f"🎲 {current_player.username} created a public room.")
                            current_room = Public_Room(current_player.username, "Rock-Paper-Scissor", "Waiting")
                            current_room.creator_socket = client_socket
                            public_rooms.append(current_room)
                            client_socket.send("OK".encode())

                        elif room_type == "2":
                            current_room = Private_Room(current_player.username, "Rock-Paper-Scissor", "Waiting")
                            current_room.creator_socket = client_socket
                            private_rooms.append(current_room)
                            client_socket.send("OK".encode())
                            res = client_socket.recv(1024).decode()

                            tmp = 1
                            tmp2 = 1

                            if res == "gogo":
                                while True:
                                    res = client_socket.recv(1024).decode()
                                    player_idle_list = " ".join(player.username for player in online_users if player.status == "idle")

                                    if res == "INVITE" and player_idle_list:
                                        client_socket.send(player_idle_list.encode())
                                        invite_phase = True
                                    elif res == "LIST":
                                        client_socket.send(f"Available_Player: {player_idle_list}".encode() if player_idle_list else "NO_IDLE_PLAYERS".encode())
                                        invite_phase = False

                                    if invite_phase:
                                        invitee = client_socket.recv(1024).decode()
                                        # 發送邀請通知給聊天室內的被邀請玩家
                                        notification_message = f"{current_player.username} invited you to join a game!"
                                        send_invitation_notification(invitee, notification_message)
                                        print(f"==============\nInviter chosen: {invitee}\n==============")
                                        client_socket.send("invite_receive".encode())

                                        invitee_socket = next((player.client_socket for player in online_users if player.username == invitee), None)
                                        print(f"==============\nInvitee socket: {invitee_socket}\n==============")

                                        invitee_socket.send("invite_G2".encode())
                                        time.sleep(10)

                                        if tmp == 2:
                                            invitee_socket.send("accept".encode())
                                            client_socket.send("accept".encode())
                                            game_server_info = client_socket.recv(1024).decode()
                                            print(f"Game server info: {game_server_info}")
                                            invitee_socket.send(f"Game_server_info: {game_server_info}".encode())

                                            for player in online_users:
                                                if player.username == invitee:
                                                    player.status = "In Game"
                                                    break

                                            current_player.status = "In Game"
                                            joiner = Player(invitee, "In Game", invitee_socket)
                                            break
                                        elif tmp == 1:
                                            invitee_socket.send("reject".encode())
                                            time.sleep(5)
                                            if tmp2 == 2:
                                                client_socket.send("reject".encode())
                    else:  
                        room_type = client_socket.recv(1024).decode()
                        if room_type == "1": # Public Room
                            broadcast_message(f"🎲 {current_player.username} created a public room.")
                            current_room = Public_Room(current_player.username, game_type, "Waiting")
                            current_room.creator_socket = client_socket
                            public_rooms.append(current_room)
                            client_socket.send("OK".encode())

                        elif room_type == "2": # Private Room
                            current_room = Private_Room(current_player.username, game_type, "Waiting")
                            current_room.creator_socket = client_socket
                            private_rooms.append(current_room)
                            client_socket.send("OK".encode())
                            res = client_socket.recv(1024).decode()

                            tmp, tmp2 = 1, 1

                            if res == "gogo":
                                while True:
                                    res = client_socket.recv(1024).decode()
                                    player_idle_list = " ".join(player.username for player in online_users if player.status == "idle")

                                    if res == "INVITE" and player_idle_list:
                                        client_socket.send(player_idle_list.encode())
                                        invite_phase = True
                                    elif res == "LIST":
                                        client_socket.send(f"Available_Player: {player_idle_list}".encode() if player_idle_list else "NO_IDLE_PLAYERS".encode())
                                        invite_phase = False
                                    
                                    if invite_phase:
                                        invitee = client_socket.recv(1024).decode()
                                        # 發送邀請通知給聊天室內的被邀請玩家
                                        notification_message = f"{current_player.username} invited you to join a game!"
                                        send_invitation_notification(invitee, notification_message)
                                        print(f"==============\nInviter chosen: {invitee}\n==============")
                                        client_socket.send("invite_receive".encode())

                                        invitee_socket = next((player.client_socket for player in online_users if player.username == invitee), None)
                                        print(f"==============\nInvitee socket: {invitee_socket}\n==============")

                                        invitee_socket.send(game_type.encode())
                                        time.sleep(10)

                                        if tmp == 2:
                                            invitee_socket.send("accept".encode())
                                            client_socket.send("accept".encode())
                                            game_server_info = client_socket.recv(1024).decode()
                                            print(f"Game server info: {game_server_info}")
                                            invitee_socket.send(f"Game_server_info: {game_server_info}".encode())

                                            for player in online_users:
                                                if player.username == invitee:
                                                    player.status = "In Game"
                                                    break

                                            current_player.status = "In Game"
                                            joiner = Player(invitee, "In Game", invitee_socket)
                                            break
                                        elif tmp == 1:
                                            invitee_socket.send("reject".encode())
                                            time.sleep(5)
                                            if tmp2 == 2:
                                                client_socket.send("reject".encode())
                            

            elif data.startswith("join"):
                if public_rooms:
                    rooms_info = "\n".join(f"{idx + 1}. {room.creator} ({room.game_type})" for idx, room in enumerate(public_rooms))
                    client_socket.send(rooms_info.encode())

                    joiner = current_player

                    try:
                        room_choice = int(client_socket.recv(1024).decode()) - 1
                        if 0 <= room_choice < len(public_rooms):
                            chosen_room = public_rooms[room_choice]

                            if chosen_room.num_players < 2:
                                chosen_room.status = "In Game"
                                chosen_room.num_players += 1
                                Game_room = chosen_room

                                creator_socket = chosen_room.creator_socket
                                creator_socket.send("Please provide your game server's IP and port.".encode())
                            else:
                                client_socket.send("Room is full.".encode())
                        else:
                            client_socket.send("Invalid room choice.".encode())

                    except (ValueError, IndexError):
                        client_socket.send("Invalid input".encode())

                else:
                    client_socket.send("No public rooms available.".encode())

            elif data.startswith("Game Over"):
                current_player.status = "idle"
                joiner.status = "idle"
                if current_room:
                    if current_player.username == current_room.creator:
                        time.sleep(3)
                        if current_room in public_rooms:
                            public_rooms.remove(current_room)
                        elif current_room in private_rooms:
                            private_rooms.remove(current_room)
                        current_room = None    
                        display_lobby_status()
            

            elif data.startswith("Game_Server_IP"):
                print(data)
                joiner.client_socket.send(f"Game_server_info: {data}".encode())
                res = joiner.client_socket.recv(1024).decode()
                if res == "Okay":
                    joiner.client_socket.send(Game_room.game_type.encode())
                for player in online_users:
                    if player.username == Game_room.creator:
                        player.status = "In Game"
                        break
                joiner.status = "In Game"
                display_lobby_status()

            elif data.startswith("yes"):
                print("-----------------------------------")
                print(f"Invitee respond: {data}")
                print("-----------------------------------")
                tmp = 2

            elif data.startswith("no"):
                print("-----------------------------------")
                print(f"Invitee respond: {data}")
                print("-----------------------------------")
                tmp = 1

            elif data.startswith("private_reject"):
                tmp2 = 2
                print(f"Invitee_res: {data}")

            elif data.startswith("list game lobby info"):
                status_message = GET_lobby_status()
                client_socket.send(status_message.encode())
                


            if data != "Game Over" and not data.startswith("Game_Server_IP"):
                print("----------------------")
                print(f"Received: {data}")
                print("----------------------")
                display_lobby_status()

        except Exception as e:
            print(f"Error: {e}")
            break        
    client_socket.close()



def accept_clients():
    while True:
        client_socket, address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, address)).start()

if __name__ == "__main__":
    try:
        # 初始化時從文件加載用戶數據
        registered_users = load_users()
        
        port = int(input("Enter the chat port (e.g., 10001): "))
        CHAT_PORT=port
        chat_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        chat_server.bind((HOST, CHAT_PORT))
        chat_server.listen(5)
        # 啟動聊天伺服器
        threading.Thread(target=accept_chat_clients, daemon=True).start()

        port = int(input("Enter the server port (e.g., 10001): "))
        PORT=port
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((HOST, PORT))
        server.listen(5)
        print("The game lobby server is running, allowing new players to register...")
        accept_clients()
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        # 關閉聊天伺服器和遊戲伺服器
        if 'chat_server' in locals():
            chat_server.close()
            print(f"Chat server on port {CHAT_PORT} closed.")
        if 'server' in locals():
            server.close()
            print(f"Game lobby server on port {PORT} closed.")
        print("Servers shut down successfully. Goodbye!")
