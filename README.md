# JackTheGripper
NISE Project 2

# Bio-Inspired Stroke Rehabilitation Handle

## Project Structure
- `main_rehab.py`: The entry point. Initializes the Hardware Interface (HWI) and starts the event loop.
- `event_detections.py`: Neuromorphic logic to classify "Controlled Grip" vs "Muscle Spasms".
- `led_feedback.py`: Controls the integrated RGB LEDs on the skin cells based on detected states.
- `ui_bridge.py`: Acts as a data bridge. Normalizes raw sensor values and strems to the 3D visualizer.
- `visualizator_3d.py`: Graphical core. Render the 3D handle and gives real-time feedback. 

## Installation & Dependencies
- Python 3.12.3
- Standard libraries: `threading`, `time`, `logging`, `copy`, `sys`, `os`
- Custom libraries: `scn` (Skin Cell Network)
- External libraries: `pip install PyQt6 pyqtgraph PyOpenGL numpy-stl numpy`

## Usage
1. Connect to WIFI network `nise0XX` (Password: `nise2025`).
2. Run `python main_rehab.py`.
3. In CLI, type `c` (connect), then `udr 63` (start sampling), then `store offsets` (calibrate sensor), and then `tut on` (activate feedback loop and UI tracking).
4. Deactivate with `d`  and then exit with `q`.