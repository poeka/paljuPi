import time
import socketClient

webSocket = socketClient.SocketThread()
webSocket.start()

while True:

    print("Täällä pyörii mainlooppi")

    time.sleep(3)