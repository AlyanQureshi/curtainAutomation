from gpiozero import OutputDevice
from time import sleep
from datetime import datetime, timedelta
import threading
import json
import os
import paho.mqtt.client as mqtt

# Config
BROKER = "localhost"
PORT = 1883
TOPIC = "curtains/command"
STATE_FILE = "/home/alyan-pi1/personalProjects/curtain_schedule.json"
# 20 Motor Rotations
MOTOR_STEPS_WHILE_OPENING = 10240
# 17.25 Motor Rotations
MOTOR_STEPS_WHILE_CLOSING = 9728

# Day codes, in Python's weekday() order (Monday = 0 ... Sunday = 6)
WEEKDAY_CODES = ["Mo", "Tu", "We", "Th", "Fr", "Sa", "Su"]

# GPIO / motor
IN1 = OutputDevice(17)  # Yellow
IN2 = OutputDevice(18)  # Green
IN3 = OutputDevice(27)  # Blue
IN4 = OutputDevice(22)  # Black

pins = [IN1, IN2, IN3, IN4]

sequence = [
    [1, 0, 0, 0],
    [1, 1, 0, 0],
    [0, 1, 0, 0],
    [0, 1, 1, 0],
    [0, 0, 1, 0],
    [0, 0, 1, 1],
    [0, 0, 0, 1],
    [1, 0, 0, 1]
]

# Reverse the sequence for closing
reverse_sequence = sequence[::-1]

# Only used to keep the MQTT thread and scheduler thread from
# reading/writing the file at the exact same instant.
file_lock = threading.Lock()


def run_motor(motor_sequence, steps):
    for _ in range(steps):
        for step in motor_sequence:
            for pin, value in zip(pins, step):
                pin.value = value
            sleep(0.002)

    for pin in pins:
        pin.off()


def open_curtains():
    print("Opening curtains...")
    run_motor(sequence, MOTOR_STEPS_WHILE_OPENING)
    print("Curtains opened.")


def close_curtains():
    print("Closing curtains...")
    run_motor(reverse_sequence, MOTOR_STEPS_WHILE_CLOSING)
    print("Curtains closed.")


def save_schedule(days, time_str):
    """Writes (and overwrites) the weekly schedule file."""
    data = {
        "days": days,
        "time": time_str
    }

    with file_lock:
        with open(STATE_FILE, "w") as file:
            json.dump(data, file, indent=4)

    print(f"Weekly schedule saved -> {','.join(days)} at {time_str}")


def load_schedule():
    """
    Returns (days, time_str) for the current weekly schedule, or None
    if no schedule file exists (or it's unreadable/corrupt). This is
    the only place that knows whether a schedule currently exists.
    """
    with file_lock:
        if not os.path.exists(STATE_FILE):
            return None

        try:
            with open(STATE_FILE, "r") as file:
                data = json.load(file)
            return data["days"], data["time"]
        except Exception as e:
            print("Could not read schedule file:", e)
            return None


def clear_schedule():
    """Deletes the schedule file entirely (used only for 'cancel')."""
    with file_lock:
        if os.path.exists(STATE_FILE):
            os.remove(STATE_FILE)
    print("Schedule cleared.")


# MQTT connection
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT broker.")
        client.subscribe(TOPIC)
        print(f"Listening on topic: {TOPIC}")
    else:
        print(f"MQTT connection failed. Error code: {rc}")


# Handle messages received from the phone
# Expected format: "<days> <time>", e.g. "Mo 6:00" or "Mo,Fr,Sa 8:00"
# (days comma-separated, then a space, then HH:MM)
def on_message(client, userdata, msg):
    message = msg.payload.decode().strip()
    print(f"Received MQTT message: {message}")

    if message.lower() == "cancel":
        clear_schedule()
        return

    try:
        days_part, time_part = message.split(" ", 1)
        days = [d.strip().capitalize() for d in days_part.split(",")]

        if not days or not all(d in WEEKDAY_CODES for d in days):
            raise ValueError("invalid day code")

        # Parse and re-format the time so "6:00" and "06:00" both
        # end up stored the same way, matching now.strftime("%H:%M")
        parsed_time = datetime.strptime(time_part.strip(), "%H:%M").time()
        time_str = parsed_time.strftime("%H:%M")

    except ValueError:
        print(
            f"Invalid command '{message}'. Use e.g. 'Mo 6:00' "
            f"or 'Mo,Fr,Sa 8:00' (days: {', '.join(WEEKDAY_CODES)})."
        )
        return

    save_schedule(days, time_str)


# Check whether it is time to run the curtains
def scheduler():
    # Purely local - no other thread needs to know this, so no
    # global/lock required for it.
    pending = False

    while True:
        schedule = load_schedule()

        if schedule is not None and not pending:
            days, time_str = schedule
            now = datetime.now()
            today_code = WEEKDAY_CODES[now.weekday()]

            if today_code in days and now.strftime("%H:%M") == time_str:
                print(f"Scheduled time reached! ({today_code} {time_str})")

                pending = True
                open_curtains()
                print("Waiting 1 second...")
                sleep(1)
                close_curtains()
                pending = False

        sleep(1)


# Start the program
client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

try:
    print("Starting curtain controller...")

    scheduler_thread = threading.Thread(target=scheduler, daemon=True)
    scheduler_thread.start()

    client.connect(BROKER, PORT)
    client.loop_forever()

finally:
    for pin in pins:
        pin.off()
