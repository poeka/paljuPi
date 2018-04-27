import asyncio
import json
import threading
import time
import websockets
import pool


class SocketThread(threading.Thread):

    def __init__(self, pool, path):
        threading.Thread.__init__(self)
        self.pool = pool
        self.isRunning = True
        self.data_array = []
        self.log_file = open(path, 'w')

    def message_handler(self, message):

        # TODO: can this throw?
        data = json.loads(message)

        if self.pool.get_state() == "FOFF":
            if data["warming_phase"] == "ON":
                self.pool.set_state("ON")

        elif data["warming_phase"] == "FOFF":
            self.pool.set_state("FOFF")

        self.pool.set_target(data["target"])
        self.pool.set_lower_limit(data["low_limit"])
        # self.pool.set_estimate(data["estimation"])

    async def send(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:
                while len(self.data_array) > 0:
                    await websocket.send(self.data_array.pop)

    async def receive(self):
        async with websockets.connect('ws://89.106.38.236:3000') as websocket:
            while True:
                self.message_handler(await websocket.recv())

    async def get_data(self):
        data = json.dumps({
            "temp_low": self.pool.get_temp_low(),
            "temp_high": self.pool.get_temp_high(),
            "temp_ambient": self.pool.get_temp_ambient(),
            "warming_phase": self.pool.get_state(),
            "target": self.pool.get_target(),
            "low_limit": self.pool.get_lower_limit()
        })
        # Append the data to an array, websocket sends data from this array
        self.data_array.append(data)
        self.log_file.write(data + '\n')  # Write the data also to a file
        await asyncio.sleep(30)

    def run(self):
        while self.isRunning:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(asyncio.gather(
                    self.send(),
                    self.receive(),
                    self.get_data(),
                ))
                loop.close()

            except:
                continue
