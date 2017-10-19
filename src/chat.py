import json
import tornado.websocket

from client import ChatClient

class ChatWebSocketHandler(tornado.websocket.WebSocketHandler):
    #
    clients = []

    #
    #
    #
    def open(self):
        print("Nuevo canal de comunicacion...")

    #
    #
    #
    def on_message(self, data):
        msg = json.loads(data)

        if msg["type"] == "login":
            self.manage_login(msg)
        else:
            room = msg["to"]
            self.manage_message(room, data)

    #
    # 
    #   
    def on_close(self):
        print("canal cerrado...")

    #
    #
    #
    def on_ping(self, data):
        print("Ping received. {0}".format(data))

    #
    #
    #
    def manage_login(self, message):
        client = ChatClient(message["nickname"], message["room"], message["connectedAt"])
        client.connection = self

        ChatWebSocketHandler.clients.append(client)
    #
    #
    #
    def manage_message(self, room, message):
        # Filtramos los clientes que esten en la misma sala
        filter_func = lambda e : e.room == room
        room_clients = filter(filter_func, ChatWebSocketHandler.clients)
        
        for client in room_clients:
            client.connection.write_message(message)