import asyncio
import websockets
import threading
import testClass
import json
import pool


class SocketThread(threading.Thread):

    def __init__(self, pool):
        threading.Thread.__init__(self)
        self.pool = pool
        self.isRunning = True

    async def send(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:
                data = json.dumps({"temp1":10*self.pool.get_temp_high(),
                                   "temp2":10*self.pool.get_temp_high(),
                                   "burner_on":"false","timestamp":1516813399504})
                await websocket.send(data)
                await asyncio.sleep(5)

    async def receive(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:

                message = await websocket.recv()
                print(message)

    def run(self):
        while self.isRunning:
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