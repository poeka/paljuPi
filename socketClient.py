import asyncio
import json
import threading
import time
import websockets


class SocketThread(threading.Thread):

    def __init__(self, ha_url, access_token, in_ws_q, out_ws_q):
        threading.Thread.__init__(self)
        self._in_ws_q = in_ws_q
        self._out_ws_q = out_ws_q
        self._ha_url = ha_url
        self._access_token = access_token
        self._isRunning = True
        self.ws = None
        self.msg_id = 1
        self.data = {
            "temp_low": None,
            "temp_high": None,
            "temp_ambient": None,
            "warming_phase": None,
            "target": None,
            "low_limit": None,
            "estimate": None,
            "water_level": None,
            "water_level_target": None,
            "heating": None
        }

    async def connect(self):
        self.ws = await websockets.connect(self._ha_url)
        # HA sends auth_required
        msg = json.loads(await self.ws.recv())
        print("HA:", msg)
        if msg["type"] != "auth_required":
            raise Exception("Unexpected auth step")
        # Send token
        await self.ws.send(json.dumps({
            "type": "auth",
            "access_token": self._access_token
        }))
        msg = json.loads(await self.ws.recv())
        print("Auth result:", msg)
        if msg["type"] != "auth_ok":
            raise Exception("Authentication failed")
        print("Connected to Home Assistant")

    async def subscribe(self):
        payload = {
            "id": self.msg_id,
            "type": "subscribe_trigger",
            "trigger": {
                "platform": "state",
                "entity_id": [
                    "input_text.palju_status",
                    "input_number.palju_current_temp",
                    "input_number.palju_target_temp",
                    "input_number.palju_low_temp_limit",
                    "input_boolean.palju_heating"
                ]
            }
        }
        self.msg_id += 1
        await self.ws.send(json.dumps(payload))

    async def send_loop(self):
        while self._isRunning:
            if not self._out_ws_q.empty():
                msg = self._out_ws_q.get()

                # Otherwise, assume this is the full data dict and translate it into HA service calls
                if isinstance(msg, dict):
                    # Update self.data with the incoming data
                    self.data.update(msg)
                    
                    mapping = {
                        "temp_high": ("input_number", "palju_current_temp"),
                        "target": ("input_number", "palju_target_temp"),
                        "low_limit": ("input_number", "palju_low_temp_limit"),
                        "warming_phase": ("input_text", "palju_status"),
                    }

                    for key, (domain, entity) in mapping.items():
                        if key not in msg:
                            continue
                        value = msg[key]
                        if value is None:
                            continue

                        if domain == "input_boolean":
                            state = "on" if value else "off"
                        else:
                            # Home Assistant expects strings for input_number/text
                            state = str(value)

                        await self.send_command({
                            "type": "set_state",
                            "domain": domain,
                            "entity": entity,
                            "state": state,
                        })

            await asyncio.sleep(0.1)

    async def receive_loop(self):
        async for msg in self.ws:
            data = json.loads(msg)
            if data.get("type") == "event":
                self.handle_event(data["event"])

    def handle_event(self, event):
        trigger = event["variables"]["trigger"]
        entity_id = trigger["entity_id"]
        new_state = trigger["to_state"]["state"]
        # Update self.data
        if entity_id == "input_number.palju_current_temp":
            self.data["temp_high"] = float(new_state) if new_state else None
        elif entity_id == "input_number.palju_target_temp":
            self.data["target"] = float(new_state) if new_state else None
        elif entity_id == "input_number.palju_low_temp_limit":
            self.data["low_limit"] = float(new_state) if new_state else None
        elif entity_id == "input_text.palju_status":
            self.data["warming_phase"] = new_state
        elif entity_id == "input_boolean.palju_heating":
            self.data["warming_phase"] = "ON" if new_state == "on" else "OFF"
        # Put updated data into queue
        if not self._in_ws_q.full():
            self._in_ws_q.put(self.data.copy())

    async def send_command(self, cmd):
        if cmd["type"] == "set_state":
            domain = cmd["domain"]
            entity = cmd["entity"]
            state = cmd["state"]
            service = "set_value"
            if domain == "input_boolean":
                service = "turn_on" if state == "on" else "turn_off"
            service_data = {"entity_id": f"{domain}.{entity}"}
            if domain != "input_boolean":
                service_data["value"] = state
            payload = {
                "id": self.msg_id,
                "type": "call_service",
                "domain": domain,
                "service": service,
                "service_data": service_data
            }
            self.msg_id += 1
            await self.ws.send(json.dumps(payload))
        # Add other command types if needed

    async def connect_and_run(self):
        await self.connect()
        await self.subscribe()
        send_task = asyncio.create_task(self.send_loop())
        receive_task = asyncio.create_task(self.receive_loop())
        await asyncio.gather(send_task, receive_task)

    def run(self):
        while self._isRunning:
            try:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                loop.run_until_complete(self.connect_and_run())
                loop.close()
            except Exception as e:
                print(f"Error: {e}")
                time.sleep(5)  # Wait before retrying