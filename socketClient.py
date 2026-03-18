import json
import requests
import threading
import time


class SocketThread(threading.Thread):

    def __init__(self, ha_url, access_token, in_ws_q, out_ws_q):
        threading.Thread.__init__(self)
        self._in_ws_q = in_ws_q
        self._out_ws_q = out_ws_q
        self._base_url = ha_url
        self._access_token = access_token
        self._headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json"
        }
        self._isRunning = True
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

    def send_update(self, data):
        # Update self.data with the incoming data
        self.data.update(data)
        
        # Bundle all sensor data into a single JSON payload
        sensor_bundle = {}
        bundled_fields = ["temp_low", "temp_high", "temp_ambient", "warming_phase", 
                          "target", "low_limit", "estimate", "water_level", "water_level_target"]
        
        for field in bundled_fields:
            if field in data and data[field] is not None:
                sensor_bundle[field] = data[field]

        if sensor_bundle:
            url = f"{self._base_url}services/input_text/set_value"
            service_data = {
                "entity_id": "input_text.palju_sensor_data",
                "value": json.dumps(sensor_bundle)
            }
            try:
                start_time = time.time()
                response = requests.post(url, headers=self._headers, json=service_data, timeout=30)
                end_time = time.time()
                print(f"POST took {end_time - start_time:.2f} seconds")
                if response.status_code != 200:
                    print(f"Failed to send sensor data: {response.status_code} - {response.text}")
            except requests.RequestException as e:
                print(f"Error sending sensor data: {e}")

    def fetch_states(self):
        # Fetch the control data entity
        try:
            url = f"{self._base_url}states/sensor.palju_control_data"
            start_time = time.time()
            response = requests.get(url, headers=self._headers, timeout=30)
            end_time = time.time()
            print(f"GET took {end_time - start_time:.2f} seconds")
            if response.status_code == 200:
                state = response.json()["state"]
                if state and state != "unknown":
                    try:
                        control_data = json.loads(state)
                        # Extract control fields
                        if "target" in control_data and control_data["target"] is not None:
                            self.data["target"] = control_data["target"]
                        if "low_limit" in control_data and control_data["low_limit"] is not None:
                            self.data["low_limit"] = control_data["low_limit"]
                        if "heating" in control_data and control_data["heating"] is not None:
                            # Convert heating to warming_phase (handle both boolean and string)
                            heating_value = control_data["heating"]
                            if heating_value == "on" or heating_value is True:
                                self.data["warming_phase"] = "ON"
                            elif heating_value == "off" or heating_value is False:
                                self.data["warming_phase"] = "FOFF"
                    except json.JSONDecodeError:
                        print("Failed to parse palju_sensor_control_data JSON")
            else:
                print(f"Failed to fetch palju_sensor_control_data: {response.status_code}")
        except requests.RequestException as e:
            print(f"Error fetching palju_sensor_control_data: {e}")
        
        # Put a copy of current self.data to the queue
        if not self._in_ws_q.full():
            self._in_ws_q.put(self.data.copy())

    def run(self):
        while self._isRunning:
            try:
                # Fetch states periodically
                self.fetch_states()

                # Send data if any
                if not self._out_ws_q.empty():
                    msg = self._out_ws_q.get()
                    if isinstance(msg, dict):
                        self.send_update(msg)
                
                time.sleep(5)  # Poll every 5 seconds
            except Exception as e:
                print(f"Error in REST client: {e}")
                time.sleep(5)  # Wait before retrying

