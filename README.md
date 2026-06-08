# 🚀 Phase 5: Autonomous Following & Obstacle Avoidance

## 🎯 Objective

Transform the robot from a perception-driven platform into an autonomous mobile robot capable of:

* Detecting and tracking a person
* Following the detected person while maintaining a safe distance
* Searching for a person when no target is detected
* Avoiding obstacles using LiDAR
* Making movement decisions in real time
* Safely navigating indoor environments

---

# 🏗️ What Was Implemented

### 👤 Person Detection

* YOLOv8-based person detection
* Real-time inference using TensorRT `.engine`
* Detection confidence filtering

### 🎯 Person Tracking

* Persistent target tracking
* Target position estimation
* Target loss handling

### 🚧 Obstacle Detection

* RPLIDAR C1 integration
* Front obstacle monitoring
* Left and right clearance estimation
* Emergency stop logic

### 🧠 Autonomous Decision Making

* Follow Mode
* Search Mode
* Obstacle Avoidance Mode
* Emergency Stop Mode

### ⚙️ Robot Motion Control

* Velocity command generation
* Steering decisions
* Serial communication with ESP32-C3
* Differential drive motor control

---

# 🔹 ROS2 Nodes

## 📷 Camera Node

Publishes camera frames from the IMX219 CSI camera.

### Output Topics

```text
/camera/image_raw
```

---

## 🧠 Detector Node

Runs optimized YOLOv8 TensorRT inference.

### Responsibilities

* Detect persons
* Publish detection information
* Estimate target location in image frame

---

## 🎯 Tracker Node

Tracks detected persons across frames.

### Responsibilities

* Maintain target identity
* Estimate target center
* Detect target loss

---

## 🚧 Obstacle Detection Node

Processes LiDAR scans.

### Responsibilities

* Detect nearby obstacles
* Calculate front distance
* Calculate left clearance
* Calculate right clearance

### Input Topic

```text
/scan
```

---

## 🧠 Decision Node

The brain of the robot.

Receives information from:

* Detector Node
* Tracker Node
* Obstacle Detection Node

Generates movement decisions.

### Output

```text
/cmd_vel
```

---

## ⚙️ Motor Control Node

Receives movement commands and sends them to ESP32-C3.

### Responsibilities

* Serial communication
* Motor speed control
* Robot movement execution

---

# 🔄 Robot Behaviour

## Scenario 1: Person Detected

When a person is detected:

1. Lock onto the target
2. Start tracking
3. Follow the target
4. Maintain a safe following distance

### Behaviour

```text
Person Detected
        ↓
Track Person
        ↓
Follow Person
        ↓
Maintain Distance
```

---

## Scenario 2: Person Lost

When no person is detected:

### Behaviour

```text
No Person Found
        ↓
Search Mode
        ↓
Move Through Room
        ↓
Continue Scanning
        ↓
Person Found
```

The robot continuously explores the environment while searching for a target.

---

## Scenario 3: Obstacle Detected

When an obstacle appears in front:

### Behaviour

```text
Obstacle Ahead
        ↓
Stop
        ↓
Measure Left Distance
        ↓
Measure Right Distance
        ↓
Turn Toward Clearer Side
        ↓
Continue Moving
```

---

## Scenario 4: Person Too Close

When the target enters the safety zone:

### Behaviour

```text
Person Very Close
        ↓
Stop
        ↓
Wait
        ↓
Resume Following
```

---

## Scenario 5: Obstacle Too Close

Emergency safety condition.

### Behaviour

```text
Obstacle Extremely Close
        ↓
Immediate Stop
        ↓
Evaluate Environment
        ↓
Choose Safe Direction
```

---

# 🔹 Hardware Used

## Main Computer

* Jetson Orin Nano
* JetPack 6.6
* ROS2 Humble

---

## Sensors

### Camera

* IMX219 CSI Camera

### LiDAR

* RPLIDAR C1

---

## Control

* ESP32-C3
* Motor Driver
* DC Motors

---

# 📡 Topics

```text
/camera/image_raw
/detections
/tracked_detections
/scan
/obstacle_detected
/front_distance
/free_direction
/cmd_vel
```

---

# 🚧 Challenges Faced & Solutions


🔴 Issue 1: Robot Oscillation

### Problem

Robot continuously switched between tracking and obstacle avoidance.

### Solution

Implemented behavior priority system:

```text
Emergency Stop
      ↓
Obstacle Avoidance
      ↓
Person Following
      ↓
Search Mode
```

---

## 🔴 Issue 2: Detector Latency

### Problem

Detection delays caused slow reaction times.

### Solution

* Optimized detector node
* Reduced unnecessary processing

---

## 🔴 Issue 3: Target Loss Recovery

### Problem

Robot stopped permanently after losing target.

### Solution

Implemented Search Mode.

```text
Target Lost
      ↓
Search
      ↓
Reacquire Target
```

---

# 📊 Results

### Achievements

✅ Real-time person detection

✅ Person tracking

✅ Autonomous following

✅ Dynamic obstacle avoidance

✅ Search behaviour

✅ Safe stopping mechanism

✅ Integrated perception-to-action pipeline

---

# 📚 Learnings

* LiDAR integration with ROS2
* Autonomous robot behaviour design
* State-machine based decision making
* Obstacle avoidance strategies
* Real-time robotics optimization
* Multi-node ROS2 architecture
* Sensor fusion for mobile robots

---

# 🔮 Next Phase

## Phase 6: Voice Interaction & AI Assistant

Planned Features:

* Wake word detection
* Voice commands
* Speech synthesis
* Follow-me voice mode
* Scene description
* Conversational AI integration

---

# 💡 Key Takeaway

This phase transformed the project from a perception and mobility system into an autonomous robot capable of finding, following, and navigating around people while safely avoiding obstacles in dynamic indoor environments.
