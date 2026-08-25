# 🪟 Smart Curtain Automation

A locally controlled IoT curtain automation system built with a **Raspberry Pi 5, MQTT, Python, and a 28BYJ-48 stepper motor**. The system supports real-time commands, recurring schedules, and schedule cancellation without relying on cloud services.

## 🎥 Demo

**[Watch the Demo](https://www.youtube.com/shorts/DGhA2qYbo9Y)**

## 📸 Hardware

<img width="360" height="480" alt="IMG_6943" src="https://github.com/user-attachments/assets/7d2d8759-137a-4c6b-a62c-f5f52b58a5c9" />

**Hardware:**

* Raspberry Pi 5
* 28BYJ-48 stepper motor
* ULN2003 motor driver
* Curtain belt and pulley mechanism

## ✨ Features

* **MQTT control:** Open and close curtains through MQTT commands.
* **Recurring schedules:** Schedule actions for multiple days, such as `Monday & Friday at 7:00 AM`.
* **Schedule cancellation:** Cancel scheduled actions before they execute.
* **Local operation:** Communication runs entirely over the local network.
* **Duplicate protection:** Prevents scheduled events from executing more than once.
* **GPIO motor control:** Controls the stepper motor through Raspberry Pi GPIO.

## 🏗️ Architecture

```text
Phone
  │
  │ MQTT
  ▼
MQTT Broker
  │
  ▼
Raspberry Pi 5
  │
  │ GPIO
  ▼
ULN2003 Driver
  │
  ▼
28BYJ-48 Motor
  │
  ▼
Curtains
```

## ⏰ Scheduling

Schedules support multiple days and specific times:

```text
Monday  07:00 → OPEN
Friday  07:00 → OPEN
```

The scheduler continuously checks for matching events, executes the motor command, and uses execution tracking to prevent duplicate runs.

Schedules can also be cancelled through MQTT before execution.

## 🛠️ Tech Stack

**Python · MQTT · Mosquitto · Raspberry Pi · Stepper Motors**

## 📸 More Photos

<img width="360" height="480" alt="IMG_6938" src="https://github.com/user-attachments/assets/7be1d09a-ed67-447c-a3f5-79b563541c0e" />
<img width="360" height="480" alt="IMG_6940" src="https://github.com/user-attachments/assets/a60d700b-293f-4111-8409-02ef4b38a280" />
<img width="480" height="360" alt="IMG_6944" src="https://github.com/user-attachments/assets/0c48e3fa-ffab-4855-a12a-dba48eed8557" />
