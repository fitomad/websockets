# WebSockets
[WebSockets](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) sobre [Tornado](http://www.tornadoweb.org/en/stable/index.html) Web Server.

## Introducción

Una prueba de concepto para probar los WebSockets presentes desde HTML5 usando el servidor Tornado de python. 

El proyecto es un chat muy básico en el que a nivel de servidor podemos indicar que usuarios van a recibir determinados mensajes.

## Requisitos

Para poder ejecutar el proyecto necesitamos tener instalado... 

* Python 2.7
* Tornado Web Server
* Un navegador con soporte para WebSocket. Safari o Google Chrome, por ejemplo

 Para comprobar si tenemos instalado Tornado en nuestro equipo ejecutamos la siguiente instrucción en la línea de comando.
```
 pip list --format=columns
```
 Si está instalado veremos que aparece en el listado junto con su número de versión. En mi caso veo esta línea:
```
 tornado    4.5.2
```
 Si no la ves es que el servidor web no está presente, así que lo instalamos mediante el comando:
```
 pip install tornado
 ```
 o si estamos en macOS es mejor usar...
 ```
 sudo pip install tornado
 ```

## Ejecutando el proyecto

Clonamos/Descargamos este repositorio y abrimos un `Terminal`. Nos situamos dentro de la carpeta **src** y ejecutamos este comando:
```
python server.py
```

Ahora el servicio está a la espera de nuevas conexiones, por lo que vamos a abrir **dos navegadores** y apuntaremos a la URL:
```
http://localhost:9090
``` 
Aparecerá la ventana de login de usuario. Es importante que elijamos *distintos* nombres de usuario pero *la misma* sala de chat para una primera prueba.  

Tras validarnos iremos al chat, y ahora escribiremos en mensajes en los dos navegadores para ver como cada uno de ellos recibe el mensaje enviado por el otro.

## Probando el envío selectivo de mensajes
Para esta prueba vamos a abrir **4 pestañas** del navegador y en la página de login vamos a poner **4 nombres de usuario diferentes** y en las salas de chat haremos que **2 de ellos** vayan a la sala de *swift-dev* y **los otros 2** a la sala *python-dev*.

Y ahora vamos a mandar mensajes con todos los usuarios, pero en este caso veremos que el servidor *sólo envía los mensajes a aquellos usuarios que comparten sala*, obviando al resto.

## Vale. Ahora vamos a verle las tripas a esto.
Tenemos que diferenciar entre el código del cliente, escrito en JavaScript, y el servidor, escrito en Python.

### El cliente
Lo que nos interesa se encuentra en el archivo `chat.js`. Aquí es donde vamos a ver todo el código necesario para conectar, enviar y recibir mensajes.

Lo primero que necesitamos es abrir una conexión con el servidor, y para ello usamos un objeto de la clase `WebSocket`
```javascript
var ws = new WebSocket("ws://localhost:9090/talking")
```
Si nos fijamos veremos que los WebSockets utilizan el protocolo `ws` en lugar de `http`. 

Una vez que hemos abierto una conexión toda la comunicación que recibamos del servidor la recogeremos en eventos que la clase `WebSocket` tiene a tal efecto.

En concreto recibiremos una evento al **conectar**
```javascript
ws.onopen = function() {
    console.log("Conectado...")
}
```
...y un evento cuando recibamos un mensaje
```javascript
ws.onmessage = function (evt) {
    console.log(evt.data)
}
```
También podemos recoger [eventos](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket) cuando se produzca un error o se cierre la conexión.

Vale, pero... ¿cómo envío un mensaje al servidor?
```javascript
ws.send("lo que quieras decir")
```
así de fácil y así de sencillo.

### El servidor
Hasta ahora hemos visto como se envía un mensaje, pero qué tenemos que hacer para que lo reciban el resto de participantes.

Lo que nos interesa saber lo encontramos en el archivo `chat.py`, en el raiz del repositorio. Este archivo contiene la clase encargada de `manejar` las conexión WebSocket y difundir los mensajes a los clientes. 

Cada uno de estos clientes se representa mediante la clase `ChatClient` que encontramos en el archivo `client.py`

Lo primero que vemos en la clase `ChatWebSocketHandler`es que hereda de [`tornado.web.WebSocketHandler`](http://www.tornadoweb.org/en/stable/websocket.html), un tipo de manejador específico que Tornado pone a nuestra disposición para manejar las conexiones WebSocket.

Al igual que en los manejadores para conexiones `HTTP`, la clase `WebSocketHandler` nos deja sobreescribir una serie de funciones en las que podemos controlar la *conexión, recepción de mensajes y cierre de comunicación* con **todos** y cada uno de los clientes que se conectan a nuestro servicio.

```python
# Se abre un canal de comunicación
def open(self):
    ...
# Recibimos un mensaje (data) de un cliente.
def on_message(self, data):
    ...
# Se ha cerrado un canal de comunicación
def on_close(self):
    ...
# Se ha recibido un PING
def on_ping(data)
    ...
```

¿Y cómo enviamos un mensaje a los clientes?

Para eso tenemos la función [`write_message(data)`](http://www.tornadoweb.org/en/stable/websocket.html#tornado.websocket.WebSocketHandler.write_message) donde data es lo que le enviamos al cliente. 

¿Y con esto respondo a **todos** los clientes?

No. Con esto **sólo** le enviamos el contenido de `data` al cliente que maneja esta WebHandlerSocket.

¿Y qué hago para responder a **todos** o a **algunos**?

Pues vamos a tener que programar un poco. Pero tranquilos que es *poco* de verdad. 

Lo primero que vamos a hacer es crearnos una clase que contenga la información relacionada con cada cliente, en nuestro caso es `ChatClient`

```python
class ChatClient:
    # WebSocket asociado
    connection = None

    #
    # Nueva Conexion
    #
    def __init__(self, nick, room, createdAt):
        self.nick = nick
        self.room = room
        self.createdAt = createdAt
```

¿Y esto se crea en la función `open()' del servidor? 

Me temo que no, vamos a tener que definir un formato de mensajes usando `json` para intercambiar mensajes con el servidor. 

En este caso he definido **3 tipos de mensajes**

* **login**: Un nuevo usuario se une al chat y a una sala en concreto
* **room**: Es un mensaje de difusión a una sala
* **private**: Un mensaje privado a un usuario.

En el servidor tenemos que diferenciar entre los mensajes de `login` y lo que son `room` o `private`. El primero no se envía a los demás usuarios, y los otros dos sólo a aquellos usuarios a los que les pueda interesar

Así que cuando un usuario hace login en la web se envía un mensaje al servidor de tipo `login` donde le dedimos el *nickname* y la *sala* a la que se conecta.

Cuando el servidor recibe el mensaje guarda esa conexión (clase ChatClient) en variable llamada `clients` donde están almacenadas **todas las conexiones** abiertas con el servicio.

Si el usuario manda un mensaje el servidor, tras comprobar que es de tipo `room` o `private`, filtra el array de clientes para recuperar sólo aquellos que están en la misma sala (si es `room`) o el cliente cuyo nick coincide con el especificado en el mensaje (si es `private`)

```python
def on_message(self, data):
    msg = json.loads(data)

    if msg["type"] == "login":
        self.manage_login(msg)
    else:
        room = msg["to"]
        self.manage_message(room, data)

def manage_login(self, message):
    client = ChatClient(message["nickname"], message["room"], message["connectedAt"])
    client.connection = self

    ChatWebSocketHandler.clients.append(client)

def manage_message(self, room, message):
    # Filtramos los clientes que esten en la misma sala
    filter_func = lambda e : e.room == room
    room_clients = filter(filter_func, ChatWebSocketHandler.clients)
    
    for client in room_clients:
        client.connection.write_message(message)        
```

Una vez el servidor tiene los clientes interesados en recibir el mensajes usa la función `write_message(message)` de **cada uno de los clientes/conexiones**

## Contacto
Cualquier duda o pregunta podéis encontrarme en twitter con el nombre de usuario [@fitomad](https://twitter.com/fitomad)
