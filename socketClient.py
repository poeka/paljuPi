import asyncio
import json
import threading
import time
import websockets


class SocketThread(threading.Thread):

    def __init__(self, url, in_ws_q, out_ws_q):
        threading.Thread.__init__(self)
        self._in_ws_q = in_ws_q
        self._out_ws_q = out_ws_q
        self._url = url
        self._isRunning = True

    async def send(self):
        async with websockets.connect('ws://' + self._url) as websocket:
            while True:
                if not self._out_ws_q.empty():
                    data = json.dumps(self._out_ws_q.get())
                    await websocket.send(data)

                await asyncio.sleep(10)

    async def receive(self):
        async with websockets.connect('ws://' + self._url) as websocket:
            while True:
                message = await websocket.recv()
                if not self._out_ws_q.empty():
                    # No clear() method available...
                    tmp = self._out_ws_q.get()

                if not self._in_ws_q.full():
                    self._in_ws_q.put(json.loads(message))

    def run(self):
        #logger = logging.getLogger('websockets')
        # logger.setLevel(logging.ERROR)  # ERROR, INFO, DEBUG
        # logger.addHandler(logging.StreamHandler())

        while self._isRunning:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(asyncio.gather(
                    self.send(),
                    self.receive(),
                ))
                loop.close()

            except:
                continue
