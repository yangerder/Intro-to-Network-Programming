import random
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