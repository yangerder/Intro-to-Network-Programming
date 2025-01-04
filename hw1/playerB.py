import socket

def udp_server_invitation():
    udp_server = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    port = int(input("請輸入要開啟的UDP伺服器Port: "))
    udp_server.bind(('0.0.0.0', port))
    print(f"伺服器已開啟在Port: {port}，等待玩家A的邀請...")

    in_game = False 

    while True:
        data, addr = udp_server.recvfrom(1024)
        player_b_name = data.decode()
        
        if in_game:
            udp_server.sendto("遊戲進行中".encode('utf-8'), addr)
            continue

        udp_server.sendto("等待邀請".encode('utf-8'), addr)
        print(f"已回應來自 {addr} 的廣播消息，等待玩家A的邀請...")

        data, addr = udp_server.recvfrom(1024)
        player_a_name = data.decode()
        print(f"{player_a_name} 想要邀請你加入遊戲，是否接受？(yes/no)")
        response = input().strip().lower()

        if response == 'yes':
            in_game = True
            udp_server.sendto("邀請已接受".encode('utf-8'), addr)
            
            data, addr = udp_server.recvfrom(1024)
            tcp_port = int(data.decode().split(":")[1].strip())

            udp_server.close()
            return tcp_port, addr
        else:
            udp_server.sendto("邀請已拒絕".encode('utf-8'), addr)
            print("拒絕了邀請")

def get_game_result(player_b_choice, player_a_choice):
    if player_b_choice == player_a_choice:
        return "平手"
    elif (player_b_choice == "剪刀" and player_a_choice == "布") or \
         (player_b_choice == "石頭" and player_a_choice == "剪刀") or \
         (player_b_choice == "布" and player_a_choice == "石頭"):
        return "玩家B勝利"
    else:
        return "玩家A勝利"

def tcp_client_game(tcp_port, addr):
    tcp_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_client.connect((addr[0], tcp_port))

    tcp_client.send("歡迎進入遊戲! 請選擇：剪刀、石頭或布".encode('utf-8'))

    player_a_choice = tcp_client.recv(1024).decode('utf-8')

    player_b_choice = input("請選擇：剪刀、石頭或布：")

    result = get_game_result(player_b_choice, player_a_choice)
    tcp_client.send(f"結果: {result}".encode('utf-8'))
    print(f"遊戲結果: {result}")

    tcp_client.close()

if __name__ == '__main__':
    port, addr = udp_server_invitation()
    if port:
        tcp_client_game(port, addr)
