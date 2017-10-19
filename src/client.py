
class ChatClient:
    #
    connection = None

    #
    # Nueva Conexion
    #
    def __init__(self, nick, room, createdAt):
        self.nick = nick
        self.room = room
        self.createdAt = createdAt