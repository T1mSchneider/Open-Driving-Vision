# 🚗 Open Driving Vision

An open-source driving vision simulator designed for experimentation and research in autonomous driving perception.

### 🚀 Getting Started

Clone the repository:
```
git clone https://github.com/ben-gunnels/Open-Driving-Vision.git
cd Open-Driving-Vision
```
### 🛠 Configuration

Customize the simulator settings:

Edit the configuration in src/constants/constants.py

Modify the simulator behavior in src/app.py

### ▶️ Run the Simulator

Launch the application from the root directory:
```
python -m src.app
```
### 👀🔭🥽 View the Outputs
Output images are generated in src/outputs/images.
Labels are generated in src/outputs/labels.
Videos are generated in src/outputs/videos. 

### 🎯 Features

### ✔️ Easily configurable driving vision system✔️ Modular & extensible architecture✔️ Open-source and community-driven

### 🚀 Start experimenting today!

### Interacting with this Application
The StreamSimulator class simulates a continuous drive by streaming objects from the horizon to the front of the frame. This can be used to test a model on a continuous driving experience.
The RandomSimulator class creates screens with random objects in random locations. This can be used for getting a diverse set of training and testing data. 
