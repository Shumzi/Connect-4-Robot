# Connect 4 Robot Project - Design & To-Do List

## Block Diagram

```
┌─────────────────────────────────────────────┐
│                PC MAIN CONTROLLER           │
│  ┌────────────┬────────────┐               │
│  │   Robot    │   Arduino  │               │
│  │ Interface  │ Interface  │               │
│  └────────────┴────────────┘               │
└─────────────┬──────┬───────────────────────┘
              │      │
        USB Serial   USB Serial
              │      │
     ┌────────▼─┐ ┌───▼─────────────┐
     │  Robot   │ │   Arduino       │
     │  Arm     │ │ - LED Strip     │
     │ (MyCobot)│ │ - Solenoids     │
     │          │ │ - Sensors       │
     └──────────┘ └────────────────┘
```

## Clean Project Structure

```
connect4-robot/
│
├── requirements.txt           # Dependencies
├── config.yaml                # Configuration file
│
├── pc_controller/
│   ├── main.py                # Orchestrator
│   ├── game.py                # Game logic (event-driven)
│   ├── core/
│   │   ├── board.py           # Board state
│   │   └── ai.py              # AI
│   ├── hardware/
│   │   ├── arduino.py         # Arduino interface
│   │   ├── robot.py           # Robot Arm interface (wraps existing)
│   │   └── mock.py            # Mocks for simulation
│   └── utils/
│       └── logger.py          # Logging
│
├── legacy/
│   └── ArmInterface.py        # Old robot interface (for re-use)
│
├── arduino_controller/
│   └── arduino_main.ino       # Arduino firmware
│
├── simulation/                # Mocks & virtual GUI for tests
│
├── docs/
│   └── architecture.md        # Design notes
```

## Risk Mitigation

**High Risk Items:**

- **Arduino firmware bugs** - Mitigated by early mock testing
- **Robot calibration drift** - Mitigated by calibration script
- **Serial communication reliability** - Mitigated by error handling
- **Hardware availability** - Mitigated by simulation layer

**Recommended approach:**

- Build simulation layer FIRST (M2) before hardware
- Test each component in isolation before integration
- Keep legacy code as fallback
- Log everything for debugging

## To-Do List

### 1. **Setup & Extraction**
- [ ] Create basic project folder structure
- [ ] Copy working ArmInterface.py to `legacy/`
- [ ] Extract board and AI logic from old repo to `core/`
- [ ] Create requirements.txt (pin pymycobot version)

### 2. **Configuration**
- [ ] Write `config.yaml` for hardware ports, AI depth, and simulation mode

### 3. **Hardware Interface**
- [ ] Wrap ArmInterface in new interface (robot.py)
- [ ] Write event-driven Arduino interface (arduino.py), including callbacks
- [ ] Implement mocks for both robot and Arduino for offline testing

### 4. **Game Logic**
- [ ] Write event-driven game loop in game.py
- [ ] Add simple `phase`/status variable for clarity

### 5. **Testing and Simulation**
- [ ] Test pure event-driven flow with mock hardware
- [ ] Test with real hardware (robot and Arduino)
- [ ] Add logging for all actions/events (for clarity)

### 6. **Documentation**
- [ ] Document all folder and file purposes in `docs/architecture.md`
- [ ] Add comments explaining the flow clearly, especially around event order

### 7. **Future/Optional**
- [ ] Add virtual GUI to simulate user/robot moves
- [ ] Upgrade to phase-based or FSM flow if requirements change

## Notes
- Pure event-driven flow is safe due to physical constraints (robot gives puck to user)
- Use phase variable just for debugging/logging clarity; FSM not required unless system becomes more complex
- Mocks will keep development smooth when hardware unavailable
