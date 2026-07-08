# =============================================================================
# HomeGuard Security System - Smart Home Monitoring Simulator
# Author: Nnanyelugo Ahukannah
# Description:
#   A prototype simulator for HomeGuard's smart home monitoring system. It
#   generates readings from motion, door, temperature, and smoke sensors,
#   checks them against safety/security thresholds depending on the system
#   mode (HOME / AWAY / SLEEP), triggers the appropriate alerts, and logs
#   every event for later review.
#
#   Built for the Ironhack "Programming Foundation Exercises" lab, this file
#   demonstrates: dictionaries (data structures), if/else logic, functions,
#   and a Sensor class.
# =============================================================================

# Step 1: Import the modules we need.
#   - random   -> to generate realistic (but varied) sensor readings
#   - datetime -> to timestamp each reading and log entry
import random
import sys
from datetime import datetime, timedelta

# On Windows the console defaults to cp1252, which cannot print the emoji (🚨)
# or the degree symbol (°) used in our output. Switching stdout to UTF-8 lets
# the formatted output match the lab's sample exactly on every platform.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass  # older Python or a stream that can't be reconfigured -- safe to ignore


# -----------------------------------------------------------------------------
# CONFIGURATION / THRESHOLDS
# -----------------------------------------------------------------------------
# Keeping the "magic numbers" in named constants makes the rules easy to read
# and easy to change in one place. These come straight from the lab's
# "System Requirements" section.
TEMP_FROZEN_PIPE = 35     # Below this (°F) -> frozen pipe risk (Safety)
TEMP_EQUIPMENT   = 95     # Above this (°F) -> equipment failure / fire risk (Safety)
COMFORT_LOW      = 65     # Comfort range lower bound (°F), only relevant in HOME mode
COMFORT_HIGH     = 75     # Comfort range upper bound (°F)
DOOR_OPEN_LIMIT  = 5      # A door left open longer than this (minutes) is "unusual"


# =============================================================================
# Step 5: THE SENSOR CLASS
# -----------------------------------------------------------------------------
# A class is a blueprint. Each Sensor object bundles together its DATA
# (id, location, type, current value, how long a door has been open) with the
# ACTIONS it can perform (read a new value, decide if it's abnormal, reset).
# =============================================================================
class Sensor:
    def __init__(self, sensor_id, location, sensor_type):
        # __init__ runs automatically when we create a new Sensor(...). It sets
        # up the object's starting "properties".
        self.id = sensor_id
        self.location = location
        self.type = sensor_type            # "motion" | "door" | "temperature" | "smoke"
        self.current_value = None          # filled in the first time we read()
        self.minutes_open = 0              # only used by door sensors (tracks how long open)

    def read(self):
        """Generate a fresh, realistic reading for this sensor and store it.

        We use `random` so each run looks a little different, like real sensors
        producing live data. Returns the new value so the caller can use it.
        """
        if self.type == "motion":
            # 25% chance of detecting motion on any given minute.
            self.current_value = random.random() < 0.25

        elif self.type == "door":
            # 20% chance the door's open/closed state flips this minute.
            if random.random() < 0.20:
                self.current_value = not bool(self.current_value)
            # Track how long a door has been continuously open (for the
            # "door left open > 5 minutes" comfort/unusual-pattern rule).
            if self.current_value:
                self.minutes_open += 1
            else:
                self.minutes_open = 0

        elif self.type == "temperature":
            # Most of the time the temperature is comfortable, but ~20% of the
            # time we simulate an extreme reading (very cold or very hot).
            if random.random() < 0.20:
                self.current_value = random.choice([
                    random.randint(28, 34),    # cold snap  -> frozen pipe risk
                    random.randint(96, 104),   # overheat   -> equipment failure
                ])
            else:
                self.current_value = random.randint(60, 78)

        elif self.type == "smoke":
            # Smoke is rare: only a 10% chance on any minute.
            self.current_value = random.random() < 0.10

        return self.current_value

    def is_abnormal(self):
        """Return True if the CURRENT value is outside safe limits.

        Note: this only knows about physical thresholds (cold, hot, smoke,
        motion, open door). Whether an abnormal reading becomes an *alert*
        also depends on the system mode -- that decision lives in
        process_reading() below.
        """
        if self.type == "motion":
            return self.current_value is True            # motion present
        elif self.type == "door":
            return self.current_value is True            # door open
        elif self.type == "temperature":
            return (self.current_value < TEMP_FROZEN_PIPE
                    or self.current_value > TEMP_EQUIPMENT)
        elif self.type == "smoke":
            return self.current_value is True            # smoke present
        return False

    def reset(self):
        """Return the sensor to a safe/default state (e.g. after acknowledging)."""
        if self.type in ("motion", "smoke", "door"):
            self.current_value = False
        elif self.type == "temperature":
            self.current_value = 70                      # a comfortable default
        self.minutes_open = 0


# =============================================================================
# Step 2: DATA STRUCTURES  (dictionaries + a list of sensors)
# -----------------------------------------------------------------------------
# The lab asks us to represent sensors, alerts, and system state as data.
# We use a class for sensors (Step 5) and plain dictionaries for alerts and the
# overall system state.
# =============================================================================
def initialize_sensors():
    """Create and return the list of Sensor objects for the Peterson home."""
    return [
        Sensor("S1", "Living Room", "motion"),
        Sensor("S2", "Front Door", "door"),
        Sensor("S3", "Kitchen", "temperature"),
        Sensor("S4", "Bedroom", "smoke"),
    ]


def make_alert(severity, category, message):
    """Build one alert as a dictionary (key/value pairs)."""
    return {
        "severity": severity,     # "HIGH" | "MEDIUM" | "LOW"
        "category": category,     # "SECURITY" | "SAFETY" | "COMFORT"
        "message": message,       # human-readable description
    }


# A simple mapping from severity -> icon, used when we print alerts.
SEVERITY_ICON = {"HIGH": "🚨", "MEDIUM": "⚠️", "LOW": "ℹ️"}


# =============================================================================
# Step 4: FUNCTIONS  (generate, process, trigger, log)
# =============================================================================

def format_reading(sensor):
    """Return the human-readable '[READING] ...' line for one sensor."""
    if sensor.type == "motion":
        state = "MOTION DETECTED" if sensor.current_value else "No activity"
        return f"[READING] {sensor.location} Motion: {state}"

    elif sensor.type == "door":
        state = "OPENED" if sensor.current_value else "CLOSED"
        return f"[READING] {sensor.location}: {state}"

    elif sensor.type == "temperature":
        temp = sensor.current_value
        if temp < TEMP_FROZEN_PIPE:
            label = "LOW"
        elif temp > TEMP_EQUIPMENT:
            label = "HIGH"
        elif COMFORT_LOW <= temp <= COMFORT_HIGH:
            label = "Normal"
        else:
            label = "Mild"
        return f"[READING] {sensor.location} Temperature: {temp}°F ({label})"

    elif sensor.type == "smoke":
        state = "SMOKE DETECTED" if sensor.current_value else "CLEAR"
        return f"[READING] {sensor.location} Smoke: {state}"

    return f"[READING] {sensor.location}: {sensor.current_value}"


# Step 3: IF/ELSE LOGIC -- decide whether a reading should raise an alert.
def process_reading(sensor, system_mode):
    """Look at one sensor + the system mode and return an alert dict, or None.

    This is where the mode matters: e.g. motion is perfectly normal in HOME
    mode, but a security alert in AWAY mode.
    """
    # ----- SAFETY rules: these apply in EVERY mode -----------------------
    if sensor.type == "temperature":
        if sensor.current_value < TEMP_FROZEN_PIPE:
            return make_alert("HIGH", "SAFETY",
                              f"{sensor.location} temperature {sensor.current_value}°F "
                              f"- frozen pipe risk!")
        elif sensor.current_value > TEMP_EQUIPMENT:
            return make_alert("HIGH", "SAFETY",
                              f"{sensor.location} temperature {sensor.current_value}°F "
                              f"- equipment failure risk!")
        # COMFORT rule: only nag about mild discomfort when someone is HOME.
        elif system_mode == "HOME" and not (COMFORT_LOW <= sensor.current_value <= COMFORT_HIGH):
            return make_alert("LOW", "COMFORT",
                              f"{sensor.location} temperature {sensor.current_value}°F "
                              f"is outside the comfort range ({COMFORT_LOW}-{COMFORT_HIGH}°F).")

    elif sensor.type == "smoke":
        if sensor.current_value:                         # smoke is always critical
            return make_alert("HIGH", "SAFETY",
                              f"{sensor.location} smoke detected - fire risk!")

    # ----- SECURITY rules: only matter when nobody should be moving ------
    elif sensor.type == "motion":
        if sensor.current_value and system_mode in ("AWAY", "SLEEP"):
            return make_alert("HIGH", "SECURITY",
                              f"Motion detected in {sensor.location} while in {system_mode} mode!")

    elif sensor.type == "door":
        if sensor.current_value and system_mode in ("AWAY", "SLEEP"):
            return make_alert("HIGH", "SECURITY",
                              f"{sensor.location} opened while in {system_mode} mode!")
        # COMFORT / unusual pattern: a door left open too long (any mode).
        elif sensor.current_value and sensor.minutes_open > DOOR_OPEN_LIMIT:
            return make_alert("MEDIUM", "COMFORT",
                              f"{sensor.location} has been open for {sensor.minutes_open} minutes.")

    return None  # nothing wrong with this reading


def trigger_alert(alert):
    """Print an alert in the '[ALERT!] icon SEVERITY: CATEGORY: message' format."""
    icon = SEVERITY_ICON.get(alert["severity"], "")
    print(f"[ALERT!] {icon} {alert['severity']}: {alert['category']}: {alert['message']}")


def log_event(log, timestamp, message):
    """Append an event to the log list AND print a '[LOG]' line."""
    entry = f"[{timestamp}] {message}"
    log.append(entry)
    print(f"[LOG] {entry}")


# =============================================================================
# Step 6: INTEGRATION -- the main simulation loop
# =============================================================================
def run_simulation(system_mode="AWAY", iterations=5, seed=42):
    """Run the full simulator for a number of one-minute time steps.

    system_mode: "HOME" | "AWAY" | "SLEEP"
    iterations:  how many minutes to simulate
    seed:        fixing the random seed makes the output reproducible, which is
                 handy for verifying the program and writing up the proof.
    """
    if seed is not None:
        random.seed(seed)

    sensors = initialize_sensors()          # Step 2: build our sensor list
    event_log = []                          # collects every logged event
    clock = datetime.strptime("14:30:00", "%H:%M:%S")  # start time

    # ----- Header -----
    print("=== HomeGuard Security System ===")
    print(f"Mode: {system_mode}")

    for minute in range(iterations):
        current_time = clock.strftime("%H:%M:%S")
        print(f"\nTime: {current_time}")

        alerts_this_tick = []               # used to detect "multiple sensors at once"

        # 1) Read + display every sensor, and collect any alerts.
        for sensor in sensors:
            sensor.read()                              # Step 4: generate reading
            print(format_reading(sensor))              # show the reading
            alert = process_reading(sensor, system_mode)  # Step 3: decide
            if alert:
                alerts_this_tick.append(alert)

        # 2) Special SECURITY rule: several sensors abnormal in the same minute
        #    while AWAY strongly suggests a break-in.
        security_hits = [a for a in alerts_this_tick if a["category"] == "SECURITY"]
        if system_mode == "AWAY" and len(security_hits) >= 2:
            alerts_this_tick.append(make_alert(
                "HIGH", "SECURITY",
                "Multiple sensors triggered at once - possible break-in!"))

        # 3) Trigger (print) each alert and log it.
        for alert in alerts_this_tick:
            trigger_alert(alert)
            log_event(event_log, current_time,
                      f"{alert['category']} alert sent to homeowner...")

        clock += timedelta(minutes=1)       # advance one minute

    # ----- Summary -----
    print(f"\n=== Simulation complete: {len(event_log)} event(s) logged ===")
    return event_log


# =============================================================================
# Step 7: TESTING -- run the simulator when this file is executed directly.
# =============================================================================
if __name__ == "__main__":
    # Security + Safety test: AWAY mode should surface security/safety alerts.
    run_simulation(system_mode="AWAY", iterations=5, seed=42)
