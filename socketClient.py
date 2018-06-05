import asyncio
import json
import threading
import time
import websockets
import pool


class SocketThread(threading.Thread):

    def __init__(self, pool, path, url):
        threading.Thread.__init__(self)
        self.pool = pool
        self.isRunning = True
        #self.log_file = open(path, 'w')
        self.url = url

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
        async with websockets.connect('ws://' + self.url) as websocket:
            while True:
                data = json.dumps({
                    "temp_low": self.pool.get_temp_low(),
                    "temp_high": self.pool.get_temp_high(),
                    "temp_ambient": self.pool.get_temp_ambient(),
                    "warming_phase": self.pool.get_state(),
                    "target": self.pool.get_target(),
                    "low_limit": self.pool.get_lower_limit()
                })

                # Write the data also to a file
                #self.log_file.write(data + '\n')
                # self.log_file.flush()
                print(data)
                await websocket.send(data)
                await asyncio.sleep(10)

    async def receive(self):
        async with websockets.connect('ws://' + self.url) as websocket:
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
