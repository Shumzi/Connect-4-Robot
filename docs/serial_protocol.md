# Serial Protocol Documentation

This document describes the serial protocol used for communication between the Connect 4 hardware (Arduino) and the host computer.

## Overview

The protocol is ASCII-based, with each command sent as a line terminated by `\n`. Responses from the Arduino are also line-based.

## Arduino -> PC

### 1. Update puck dropped

**Format:**  
`DROP <column>`

- `<column>`: Integer (0-based index) specifying the column in which puck was dropped.

**Example:**  
`DROP 3`

### 2. Update Player Pressed Start
**Format:**  
`START`

- indicates beginning of new game. todo: figure out what the game loop is (should it reset and start a new game or only after a while or what?)

## PC->Arduino

### Reset Board Command
**Format:**  
`RESET`

Resets the game board. Arduino should open all the solenoids to make all the pucks fall.

**Response:**  
- `OK` if reset was successful.


# error codes non existent for now.