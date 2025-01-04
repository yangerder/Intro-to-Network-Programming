README for Network Programming Homework
HW1: Two-Player Online Game Part 1
Objective: Develop a two-player online game where players can send game invitations and play interactively.
Features:
Game invitation using UDP protocol (client-side).
Game logic and interaction using TCP protocol (server-side).
Support for observation mode, allowing players to view all available game servers.
Technology:
UDP for sending and receiving game invitations.
TCP for transmitting game data.
Architecture: Players can act as either the Server or Client, enabling peer-to-peer game connections.
HW2: Two-Player Online Game Part 2
Objective: Extend HW1 by introducing a game lobby server and improving game workflows.
Features:
Lobby Features: Players can register, log in, log out, and view online players and game rooms.
Game Rooms: Support creating private or public rooms.
Advanced Features:
Player status updates.
Players can accept or reject game invitations.
Support multi-player connections and interactions.
Technology:
Game Lobby Server to manage player logins, room creation, and invitations.
Communication using TCP/UDP protocols.
Challenges:
Enhance user experience with player list broadcasting.
Implement error handling (e.g., server crashes or disconnections).
HW3: Two-Player Online Game Part 3
Objective: Build upon HW2 with additional lobby features and improved user interaction.
Features:
Game Management:
Allow players to upload and download game resources.
Provide a game management interface for organizing games.
Multi-User Chat Room: Enable real-time communication among players.
Invitation Management: Players can invite others to games and accept/reject invitations.
Advanced Challenges:
Add a game-switching feature.
Include a game rating and feedback system.
Technology:
Integration with external storage (e.g., CSV or database) for saving player data.
Broadcasting changes to all players in the lobby.
