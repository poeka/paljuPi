import asyncio
import json
import threading
import time
import websockets


class SocketThread(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.isRunning = True
        print("haloo")

    def message_handler(self, message):

        # TODO: can this throw?
        #data = json.loads(message)
        print(message)
        print("message received")

    async def send(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:

                data = json.dumps({
                    "temp_low": 1,
                    "temp_high": 2,
                    "temp_ambient": 1.5,
                    "warming_phase": "ON",
                    "target": 38,
                    "low_limit": 36
                })

                await websocket.send(data)
                print("message sent")
                await asyncio.sleep(10)

    async def receive(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:
                self.message_handler(await websocket.recv())

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
