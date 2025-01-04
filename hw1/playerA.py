import socket

def find_waiting_players():
    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    udp_client.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_ip = '255.255.255.255'
    player_a_name = "yy"

    ports_to_search = range(10000, 13001)
    servers = []

    for port in ports_to_search:
        udp_client.sendto(player_a_name.encode('utf-8'), (broadcast_ip, port))
    
    udp_client.settimeout(2)

    try:
        while True:
            data, addr = udp_client.recvfrom(1024)
            response = data.decode()

            if "等待邀請" in response:
                servers.append(addr)
            elif "遊戲進行中" in response:
                print(f"玩家 {addr} 正在進行遊戲，跳過...")
                continue

    except socket.timeout:
        pass

    udp_client.close()
    return servers

def udp_client_invitation(tcp_port):
    servers = find_waiting_players()
    
    if not servers:
        print("沒有找到任何等待中的玩家B")
        return None, None

    print("目前等待中的玩家:")
    for i, server in enumerate(servers):
        print(f"{i+1}. Server IP: {server[0]}/Server Port: {server[1]}")

    choice = int(input("請選擇你要邀請的玩家（輸入序號）: ")) - 1
    ip, port = servers[choice]

    udp_client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    player_a_name = input("請輸入你的名字: ")
    udp_client.sendto(player_a_name.encode('utf-8'), (ip, port))

    data, addr = udp_client.recvfrom(1024)
    response = data.decode()

    if "已接受" in response:
        print("玩家B接受了邀請")
        udp_client.sendto(f"Port: {tcp_port}".encode('utf-8'), (ip, port))  # 傳送TCP端口號
        udp_client.close()
        return ip, tcp_port
    else:
        print("玩家B拒絕了邀請")
        udp_client.close()
        return None, None

def tcp_server_game(tcp_port):
    tcp_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_server.bind(('0.0.0.0', tcp_port))
    tcp_server.listen(1)
    print(f"TCP伺服器已啟動，正在監聽端口 {tcp_port}，等待玩家B通過TCP連接...")

    conn, addr = tcp_server.accept() 
    print(f"玩家B已連接: {addr}")

    data = conn.recv(1024)
    print(f"來自玩家B的消息: {data.decode()}")

    player_a_choice = input("請選擇：剪刀、石頭或布：")
    conn.send(player_a_choice.encode('utf-8'))

    result = conn.recv(1024).decode('utf-8')
    print(f"遊戲結果: {result}")

    conn.close()
    tcp_server.close()

if __name__ == '__main__':
    tcp_port = int(input("請輸入TCP伺服器要使用的端口號（例如13005）: "))
    ip, port = udp_client_invitation(tcp_port)
    if ip and port:
        tcp_server_game(port)
