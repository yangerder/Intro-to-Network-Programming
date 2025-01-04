def play_rock_paper_scissors_host(game_socket):
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
    print("----------------------------")

def play_rock_paper_scissors_guest(game_socket):
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