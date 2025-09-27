
from main import BMS
from main import ( STATE_OFF, STATE_IDLE, STATE_DRIVE, 
                  STATE_CHARGE, STATE_PRECHARGE, STATE_SLOWCHARGE, 
                  STATE_FAULT1, STATE_FAULT2, STATE_FAULT3, 
                  OPEN_SHUTDOWN_CIRCUIT, RESET_MANUALLY, OPEN_CHARGING_SHUTDOWN_CIRCUIT , TRANSITIONS)
import random
import time

def simulate_cells(bms):
    s = bms.state
    for i in range(bms.num_cells):
        if bms.state == STATE_DRIVE:
            bms.cells_voltage[i] -= random.uniform(0.0, 0.1)
            bms.cells_temp[i] += random.uniform(0.0, 0.2)
        elif bms.state in [STATE_CHARGE, STATE_PRECHARGE, STATE_SLOWCHARGE]:
            bms.cells_voltage[i] += random.uniform(0, 0.1)
            bms.cells_temp[i] += random.uniform(0.0, 0.5)
        else: 
            bms.cells_temp[i] -= random.uniform(0.0, 0.1)


bms = BMS()
bms.state = STATE_IDLE
while True:
    print(f"\nState: {bms.state}")
    print(f"Voltages: {[round(v, 2) for v in bms.cells_voltage]}")
    print(f"Temps: {[round(t, 1) for t in bms.cells_temp]}")
    
    # Check for faults/warnings
    if bms.state in [STATE_CHARGE, STATE_PRECHARGE, STATE_SLOWCHARGE]:
        event = bms.check_sensors_and_faults(charging=True)
    else:
        event = bms.check_sensors_and_faults(charging=False)

    if bms.state in [STATE_FAULT1, STATE_FAULT2, STATE_FAULT3]:
        event = bms.check_sensors_and_faults(charging=True)
        if event == "fault_detected":
            possible_events = list(TRANSITIONS[bms.state].keys())
            event = possible_events[0]
    # if not fault, simulate another event
    if event != "fault_detected":
        possible_events = list(TRANSITIONS[bms.state].keys())
        if possible_events:
            event = possible_events[0]

    bms.transition(event)
    time.sleep(0.3)
    simulate_cells(bms)
    