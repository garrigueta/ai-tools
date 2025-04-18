""" Microsoft Flight Simulator interface module """
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

    def get_flight_data(self):
        """
        Returns the current flight data as a JSON string.
        
        Returns:
            str: JSON string of flight data
        """
        with self.data_lock:
            return json.dumps(self.data.copy())

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

    def get_game_data(self):
        """Safely retrieves the latest game data.
        
        This uses get_flight_data to ensure consistency with tests.
        """
        return self.get_flight_data()

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
            
    def get_active_warnings(self):
        """Check for and return any active warnings.
        
        Returns:
            dict: Dictionary of active warnings with warning name as key and value as 1 (active) or 0 (inactive)
        """
        active_warnings = {}
        with self.data_lock:
            # Check all warning fields
            warning_fields = [
                "alerta de stall", "alerta de overspeed", "alerta de motor",
                "alerta de fuel", "alerta de apu", "alerta de aviónica", 
                "alerta de eléctrico", "alerta de pitot", "alerta de vacío", 
                "alerta de hidráulico", "alerta de oxígeno"
            ]
            
            for field in warning_fields:
                if field in self.data and self.data[field] == 1:
                    active_warnings[field] = self.data[field]
        
        return active_warnings
        
    def get_warning_message(self, warning_name):
        """Get a detailed message for a specific warning.
        
        Args:
            warning_name (str): The name of the warning
            
        Returns:
            str: A helpful message describing the warning and recommended actions
        """
        warnings_info = {
            "alerta de stall": "¡Alerta de pérdida! Aumente la velocidad inmediatamente bajando el morro del avión.",
            "alerta de overspeed": "¡Alerta de exceso de velocidad! Reduzca potencia y levante el morro del avión.",
            "alerta de motor": "¡Alerta de motor! Verifique los indicadores del motor inmediatamente.",
            "alerta de fuel": "¡Alerta de combustible bajo! Verifique los niveles de combustible y busque un lugar para aterrizar.",
            "alerta de apu": "Alerta de la unidad auxiliar de potencia (APU). Verifique los sistemas auxiliares.",
            "alerta de aviónica": "Alerta de sistemas de aviónica. Posible fallo en instrumentos de navegación.",
            "alerta de eléctrico": "Alerta del sistema eléctrico. Verifique los sistemas eléctricos y considere apagar equipos no esenciales.",
            "alerta de pitot": "Alerta del sistema pitot. Los datos de velocidad pueden ser incorrectos.",
            "alerta de vacío": "Alerta del sistema de vacío. Los instrumentos giroscópicos pueden ser poco fiables.",
            "alerta de hidráulico": "Alerta del sistema hidráulico. El control de la aeronave puede ser afectado.",
            "alerta de oxígeno": "Alerta del sistema de oxígeno. Verifique el suministro de oxígeno y considere descender."
        }
        
        return warnings_info.get(warning_name, f"Advertencia activa: {warning_name}")
        
    def get_warning_priority(self, warning_name):
        """Get the priority level for a specific warning.
        
        Args:
            warning_name (str): The name of the warning
            
        Returns:
            int: Priority level (1-3, where 3 is highest priority)
        """
        high_priority = ["alerta de stall", "alerta de overspeed", "alerta de motor", "alerta de fuel"]
        medium_priority = ["alerta de eléctrico", "alerta de hidráulico", "alerta de pitot"]
        
        if warning_name in high_priority:
            return 3
        elif warning_name in medium_priority:
            return 2
        else:
            return 1

    def get_assistant_context(self):
        """Provides specialized context for the flight simulator assistant."""
        return """
You are a virtual co-pilot and flight assistant for Microsoft Flight Simulator.
You have expertise in flight operations, navigation, and aircraft systems.

Key flight parameters to monitor:
- Normal airspeed range is typically between 80-250 knots depending on aircraft and phase of flight
- Normal rate of climb/descent is typically between -2000 and +2000 feet per minute
- Normal engine temperature ranges are 100-240°C for oil and 300-500°C for cylinder head
- Stall warnings indicate dangerously low airspeed; immediate action required
- Overspeed warnings indicate excessive speed; reduce throttle immediately

When reporting flight data:
- Altitude should be reported in feet MSL (Mean Sea Level)
- Airspeed should be reported in knots
- Heading should be reported in degrees (0-359)
- Vertical speed should be reported in feet per minute

Key terminology:
- HDG: Heading
- ALT: Altitude
- SPD/IAS: Indicated Airspeed
- VS: Vertical Speed
- NAV1/NAV2: Navigation Radios
- COM1/COM2: Communication Radios
- XPDR: Transponder

When warning alerts are active, prioritize them in your responses and recommend appropriate actions.
For altitude and heading, round to the nearest whole number for clarity.
For airspeed and vertical speed, round to one decimal place.

If asked about ATC communications or flight planning, explain that you can report current radio settings but cannot communicate with ATC directly.
"""