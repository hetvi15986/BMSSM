NUM_CELLS = 4
OV_THRESHOLD = 4.2
UV_THRESHOLD = 2.5

MAX_CHARGE_TEMP = 45
MAX_CHARGE_TEMP_WARNING = 40

MIN_CHARGE_TEMP = 0
MIN_CHARGE_TEMP_WARNING = 5

MAX_DISCHARGE_TEMP = 60
MAX_DISCHARGE_TEMP_WARNING = 55

MIN_DISCHARGE_TEMP = -20
MIN_DISCHARGE_TEMP_WARNING = -15

CELL_BALANCING = False
BALANCE_THRESHOLD = 0.05 

# Main States
STATE_OFF = "OFF"
STATE_IDLE = "IDLE"
STATE_DRIVE = "DRIVE"
STATE_CHARGE = "CHARGE"
STATE_PRECHARGE = "PRECHARGE"
STATE_SLOWCHARGE = "SLOWCHARGE"
STATE_FAULT1 = "FAULT1"
STATE_FAULT2 = "FAULT2"
STATE_FAULT3 = "FAULT3"
OPEN_SHUTDOWN_CIRCUIT = "OPEN_SHUTDOWN_CIRCUIT"
RESET_MANUALLY = "RESET_MANUALLY"
OPEN_CHARGING_SHUTDOWN_CIRCUIT = "OPEN_CHARGING_SHUTDOWN_CIRCUIT"

# Transitions
TRANSITIONS = {
    STATE_OFF: {
        "power_on": STATE_IDLE,
        "fault_detected": STATE_FAULT1,
    },
    STATE_IDLE: {
        "start_drive": STATE_DRIVE,
        "start_charge": STATE_PRECHARGE,
        "fault_detected": STATE_FAULT1,
        "power_off": STATE_OFF,
    },
    STATE_DRIVE: {
        "stop_drive": STATE_IDLE,
        "fault_detected": STATE_FAULT1,
        "emergency": OPEN_SHUTDOWN_CIRCUIT,
    },
    STATE_CHARGE: {
        "stop_charge": STATE_IDLE,
        "fault_detected": STATE_FAULT1,
        "emergency": OPEN_SHUTDOWN_CIRCUIT,
    },
    STATE_PRECHARGE: {
        "stop_precharge": STATE_IDLE,
        "start_charge": STATE_CHARGE,
        "fault_detected": STATE_FAULT1,
        "emergency": OPEN_SHUTDOWN_CIRCUIT
    },
    STATE_SLOWCHARGE: {
        "stop_slowcharge": STATE_IDLE,
        "fault_detected": STATE_FAULT1,
        "emergency": OPEN_SHUTDOWN_CIRCUIT,
    },
    STATE_FAULT1: {
        "fault_confirmed": STATE_FAULT2,
        "fault_resolved_idle": STATE_IDLE,
        "fault_resolved_drive": STATE_DRIVE,
        "fault_resolved_charge": STATE_IDLE,
    },
    STATE_FAULT2: {
        "persistent_fault": STATE_FAULT3,
        "fault_resolved_idle": STATE_IDLE,
        "fault_resolved_drive": STATE_DRIVE,
        "fault_resolved_charge": STATE_IDLE,
    },
    STATE_FAULT3: {
        "reset_manual": RESET_MANUALLY,
        "fault_resolved_idle": STATE_IDLE,
        "fault_resolved_drive": STATE_DRIVE,
        "fault_resolved_charge": STATE_IDLE,
        "emergency": OPEN_SHUTDOWN_CIRCUIT,
    },
    OPEN_SHUTDOWN_CIRCUIT: {
        "confirmation, shutdown circuit": RESET_MANUALLY
    },
    OPEN_CHARGING_SHUTDOWN_CIRCUIT: {
        "confirmation, charging shutdown circuit": RESET_MANUALLY
    },
    RESET_MANUALLY: {
        "reset_done": STATE_OFF,
    },
}



class BMS:
    def __init__(self, num_cells=NUM_CELLS):
        self.num_cells = num_cells
        self.balancing = False
        self.state = STATE_OFF
        self.cells_voltage = [3.7] * num_cells
        self.cells_temp = [25] * num_cells
        self.prev_fault_state = None
    
    def broadcast(self, message):
        print(f"[BROADCAST] {message}")

    def check_sensors_and_faults(self, charging = False):
        for v in self.cells_voltage:
            if v > OV_THRESHOLD or v < UV_THRESHOLD:
                return "fault_detected"
        for t in self.cells_temp:
            if charging:
                if t > MAX_CHARGE_TEMP or t < MIN_CHARGE_TEMP:
                    self.broadcast(f"Fault detected! Temp: {t:.1f}°C")
                    return "fault_detected"
                if t > MAX_CHARGE_TEMP_WARNING:
                    self.broadcast(f"Getting hot! Temp: {t:.1f}°C")
                    return "slowcharge"
                if t < MIN_CHARGE_TEMP_WARNING:
                    self.broadcast(f"Getting cold! Temp: {t:.1f}°C")
                    return None
            else:
                if t > MAX_CHARGE_TEMP or t < MIN_CHARGE_TEMP:
                    self.broadcast(f"Too hot! Temp: {t:.1f}°C")
                    return "fault_detected"
                if t > MAX_DISCHARGE_TEMP_WARNING:
                    msg = "cell temperature: "+ t
                    self.broadcast(f"Getting hot! Temp: {t:.1f}°C")
                    return None
                if t < MIN_DISCHARGE_TEMP_WARNING:
                    self.broadcast(f"Getting cold! Temp: {t:.1f}°C")
                    return None
                
        return None


    def transition(self, update):
        if update is None:
            return
        if (self.state == STATE_CHARGE or self.state == STATE_SLOWCHARGE) and update == "slowcharge":
            self.state = TRANSITIONS[self.state][update]
            self.broadcast(f"Transition: do {update} to {self.state}")
            return
        if self.state == STATE_PRECHARGE and update == "start_charge":
            self.state = TRANSITIONS[self.state][update]
            self.broadcast(f"Precharge complete: CHARGE")
            return
        if update in TRANSITIONS[self.state]:
            self.state = TRANSITIONS[self.state][update]
            if self.state == STATE_PRECHARGE or self.state == STATE_CHARGE or self.state == STATE_SLOWCHARGE:
                self.balancing = False
            else:
                self.balancing = True
            self.broadcast(f"Transition: from {update} to {self.state}")













