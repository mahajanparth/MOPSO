
# A Particle Swarm Optimization-Based Cooperation Method for Multiple-Target Search by Swarm UAVs in Unknown Environments

## Overview
This repository contains a swarm UAV coordination system designed for multi-target search, optimized payload drops, and inter-UAV collision avoidance. The system is based on a **Multi-Target Particle Swarm Optimization (MTPSO)** approach, inspired by Particle Swarm Optimization (PSO), to enable decentralized cooperative UAV control.

The swarm UAVs utilize onboard sensors and real-time data sharing to dynamically adjust flight paths, detect targets, and deploy payloads efficiently in unknown environments.

## Key Features
- **Decentralized Swarm Coordination**: UAVs operate in a networked environment, sharing limited data to improve efficiency.
- **Multi-Target Search Optimization**: Implements an adaptive PSO variant (MTPSO) for improved search performance.
- **Inter-UAV Collision Avoidance**: Ensures safe flight paths using dynamic trajectory adjustments.
- **Optimized Payload Delivery**: UAVs determine the best drop points in real-time.
- **Simulation Integration**: Uses Ardupilot’s Simulation in the Loop (SITL) for realistic testing.
- **Human Detection**: Vision-based processing using Deep Learning models for identifying targets.
- **Ground Control Station (GCS) Interface**: A control interface to manage UAVs and monitor their status.

---

## Directory Structure
The repository consists of the following major components:

### `gcs_client4/`
Contains scripts related to the **Ground Control Station (GCS)**, which communicates with UAVs.
- `gcs_client4.py` - Manages communication between the GCS and UAV swarm.

### `new_on_uav/`
Core UAV control scripts, including swarm behavior, emergency handling, and network management.
#### Key Scripts:
- `Swarm2.py` - Implements swarm behavior and MOPSO-based navigation.
- `SwarmBot.py` - Defines individual UAV control, including navigation and state tracking.
- `Uav_to_GCS.py` - Manages data exchange between UAVs and the GCS.
- `helper.py` - Contains utility functions for waypoint calculations, distance measurement, and velocity adjustments.
- `emergency_landing.py` - Handles emergency UAV landings.
- `back_to_adhoc.py` - Ensures UAVs remain connected in Ad-Hoc networking mode.
- `modified_server8.py` - Alternative UAV server implementation.

#### Supporting Files:
- `wp_list`, `number_of_UAVs`, `weight_matrix` - Configuration files for swarm parameters and navigation.
- `mav.tlog`, `eeprom.bin` - Log files for debugging and data recording.

### `VISION/`
Includes scripts and data for human detection and vision-based navigation.
#### Key Scripts:
- `human_detection.py` - Uses deep learning to identify humans in UAV camera feeds.
- `VideoGrabber.py` - Handles real-time video streaming from UAV cameras.
- `LocalPlanner.py` - Computes local navigation paths based on detected objects.
- `calc_gps.py`, `gps_correction.py` - GPS processing utilities.

#### Deep Learning Model Files:
- `darknet/files/human_detection.cfg`, `human.names`, `tiny_human_detection.cfg` - Configuration for object detection models.

### `GUI/`
The Ground Control Station graphical interface.
#### Key Scripts:
- `GUI.py` - Main GUI application for monitoring and controlling UAVs.
- `working_gui.py`, `new_gui.py`, `tested_gui.py` - Various versions of the control interface.
- `connectiontouavs.py` - Manages network connectivity between the GUI and UAVs.
- `LAND_ALL_UAVS.py` - Emergency landing control for all UAVs.

---

## Installation and Setup
### Prerequisites
Ensure you have the required dependencies installed:
```bash
pip install dronekit pymavlink numpy scipy shapely
```

### Running the System
1. **Start the GCS Interface:**
   ```bash
   python3 CORE_GUI_CODE/GUI.py
   ```
2. **Launch Swarm Control:**
   ```bash
   python3 CORE_UAV_CODE/Swarm2.py
   ```
3. **Monitor Video Feeds:**
   ```bash
   python3 CORE_UAV_CODE/VISION/VideoGrabber.py
   ```
4. **Emergency Landing (if required):**
   ```bash
   python3 CORE_UAV_CODDE/emergency_landing.py
   ```

---

## Algorithmic Approach
### **Multi-Target Particle Swarm Optimization (MTPSO)**
The UAV swarm utilizes a modified PSO-based control mechanism:
- Each UAV adjusts its position based on **personal best**, **global best**, and **inter-UAV collision avoidance** factors.
- UAVs dynamically share target data to optimize the search process.
- Payload drops are assigned based on proximity and availability.
- The system integrates various **inertial functions** to balance exploration and exploitation.

### Collision Avoidance
- Ensures UAVs maintain safe distances using consensus-based adjustments.
- The `Dsafe` parameter prevents UAV clustering and reduces congestion.

### Simulation and Testing
- The system is tested using **Ardupilot SITL**.
- Multiple **hyperparameters** such as FOV, velocity, and swarm size are optimized to achieve efficient results.

---

## Future Improvements
- **Adaptive UAV Formation**: Dynamic restructuring of UAVs based on detected targets.
- **Enhanced Target Prediction**: Using reinforcement learning for improved target identification.
- **Energy-Aware Navigation**: Optimizing routes to extend UAV battery life.

---

## Contributors
- **Parth Mahajan**
- **Aniket Gupta** 
- **Aman Virmani**


For further details, refer to the **A Particle Swarm Optimization-Based Cooperation Method for Multiple-Target Search by Swarm UAVs in Unknown Environments** paper.

---

## License
This project is open-source and available under the MIT License.


