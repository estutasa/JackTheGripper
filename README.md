# JackTheGripper
NISE Project Block 2

# Bio-Inspired Stroke Rehabilitation Handle

## Project Structure
- `main_rehab.py`: The entry point. Initializes the Hardware Interface and starts the event loop
- `event_detections.py`: Neuromorphic logic to classify good vs. bad grip
- `led_feedback.py`: Controls the integrated RGB LEDs on the skin cells based on detected states (white, green, red)
- `ui_bridge.py`: Acts as a data bridge. Normalizes raw sensor values and streams to the 3D visualizer
- `visualizator_3d.py`: Graphical core. Renders the 3D handle and gives real-time feedback

## Installation & Dependencies
Run `make setup` to install all dependencies automatically.

- Python 3.12.3
- Standard libraries: `threading`, `time`, `logging`, `copy`, `sys`, `os`
- Custom libraries: `scn` (Skin Cell Network)
- External libraries: `PyQt6 pyqtgraph PyOpenGL numpy-stl numpy`

After creating a virtual environment, can be installed running `pip install -r requirements.txt`

## Usage
1. Connect to WIFI network `nise0XX` (Password: `nise2025`).
2. Run `python main_rehab.py`.
3. In CLI, type `c` (connect), then `udr 63` (start sampling), then `store offsets` (calibrate sensor), and then `start` (activate feedback loop and UI tracking).
4. Deactivate with `stop`, `d`  and then exit with `q`.
