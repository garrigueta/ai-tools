import threading
import time
import json
from SimConnect import SimConnect, AircraftRequests, AircraftEvents


class MSFSWrapper:
    """ Wrapper class for Microsoft Flight Simulator (MSFS) SimConnect API. """
    def __init__(self):
        self.simconnect = SimConnect()
        self.requests = AircraftRequests(self.simconnect, _time=0)
        self.events = AircraftEvents(self.simconnect)
        self.running = False
        self.data = {}
        self.data_lock = threading.Lock()

    def fetch_flight_data(self):
        """Fetches flight data from MSFS."""
        with self.data_lock:
            try:
                self.data = {
                    "latitud actual": self.requests.get("PLANE_LATITUDE"),
                    "longitud actual": self.requests.get("PLANE_LONGITUDE"),
                    "altitud de vuelo": self.requests.get("PLANE_ALTITUDE"),
                    "airspeed(velocidad)": self.requests.get("AIRSPEED_INDICATED"),
                    "ground speed(velocidad sobre el suelo)": self.requests.get("GROUND_VELOCITY"),
                    "dirección(HDG)": self.requests.get("PLANE_HEADING_DEGREES_TRUE"),
                    "velocidad vertical": self.requests.get("VERTICAL_SPEED"),
                    "en tierra": self.requests.get("SIM_ON_GROUND"),
                    "ángulo de los flaps": self.requests.get("TRAILING_EDGE_FLAPS_LEFT_PERCENT"),
                    "gear": self.requests.get("GEAR_POSITION"),
                    "freno de estancionamiento": self.requests.get("BRAKE_PARKING"),
                    "motor encendido": self.requests.get("GENERAL_ENG_MASTER_ALTERNATOR"),
                    "vueltas motor(RPM)": self.requests.get("GENERAL_ENG_RPM"),
                    "Cantidad de combustible": self.requests.get("FUEL_TOTAL_QUANTITY"),
                    "flujo de combustible": self.requests.get("ENG_FUEL_FLOW_GPH:1"),
                    "temperatura del aceite": self.requests.get("ENG_OIL_TEMPERATURE:1"),
                    "temperatura de la cámara de explosión": self.requests.get("ENG_CYL_HEAD_TEMP:1"),
                    "pressión del combustible": self.requests.get("ENG_FUEL_PRESSURE:1"),
                    "bomba de combustible encendida": self.requests.get("FUEL_PUMP_ON:1"),
                    "piloto automático": self.requests.get("AUTOPILOT_MASTER"),
                    "retención de altitud": self.requests.get("AUTOPILOT_ALTITUDE_LOCK_VAR"),
                    "retención de rumbo": self.requests.get("AUTOPILOT_HEADING_LOCK_DIR"),
                    "frequencia activa de radio nav1": self.requests.get("NAV_ACTIVE_FREQUENCY:1"),
                    "frequencia activa de radio nav2": self.requests.get("NAV_ACTIVE_FREQUENCY:2"),
                    "frequencia activa de radio com1": self.requests.get("COM_ACTIVE_FREQUENCY:1"),
                    "frequencia activa de radio com2": self.requests.get("COM_ACTIVE_FREQUENCY:2"),
                    "código del transponder": self.requests.get("TRANSPONDER_CODE_SET"),
                    # Warnings
                    "alerta de stall": self.requests.get("STALL_WARNING"),
                    "alerta de overspeed": self.requests.get("OVERSPEED_WARNING"),
                    "alerta de motor": self.requests.get("ENGINE"),
                    "alerta de fuel": self.requests.get("FUEL"),
                    "alerta de apu": self.requests.get("APU"),
                    "alerta de aviónica": self.requests.get("AVIONICS"),
                    "alerta de eléctrico": self.requests.get("ELECTRICAL"),
                    "alerta de pitot": self.requests.get("PITOT"),
                    "alerta de vacío": self.requests.get("VACUUM"),
                    "alerta de hidráulico": self.requests.get("HYDRAULIC"),
                    "alerta de oxígeno": self.requests.get("OXYGEN"),
                }
            except Exception as e:
                print(f"Error fetching data: {e}")

    def start_data_loop(self, interval=1):
        """Starts a loop to fetch data at regular intervals."""
        self.running = True
        thread = threading.Thread(target=self._data_loop, args=(interval,), daemon=True)
        thread.start()

    def _data_loop(self, interval):
        """Thread function to fetch data in a loop."""
        while self.running:
            self.fetch_flight_data()
            time.sleep(interval)

    def get_flight_data(self):
        """Safely retrieves the latest flight data."""
        with self.data_lock:
            return json.dumps(self.data.copy())

    def stop_data_loop(self):
        """Stops the data-fetching loop."""
        self.running = False

    def trigger_event(self, event_name):
        """Triggers an MSFS event."""
        try:
            event = self.events.find(event_name)
            event()
            print(f"Triggered event: {event_name}")
        except Exception as e:
            print(f"Error triggering event: {e}")
