# JackTheGripper
NISE Project 2

# Bio-Inspired Stroke Rehabilitation Handle

## Project Structure
- `main_rehab.py`: The entry point. Initializes the Hardware Interface (HWI) and starts the event loop.
- `event_detections.py`: Neuromorphic logic to classify "Controlled Grip" vs "Muscle Spasms".
- `led_feedback.py`: Controls the integrated RGB LEDs on the skin cells based on detected states.
- `ui_bridge.py`: Formats and streams tactile data to the Python/OpenGL GUI (Homunculus).

## Installation & Dependencies
- Python 3.12.3
- Standard libraries: `threading`, `time`, `logging`, `copy`
- Custom libraries: `scn` (Skin Cell Network)

## Usage
1. Connect to WIFI network `nise0XX` (Password: `nise2025`).
2. Run `python main_rehab.py`.
3. In CLI, type `c` (connect), then `udr 63` (start sampling), then `e on` (event-mode).
4. Deactivate firmware feedback with `of off`.