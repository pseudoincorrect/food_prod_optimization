# Food Production Chain Optimization (Industry 4.0)

Optimization of the flow in a robotized food production chain.

System regrouping machine vision, optimization and robot control to optimizing the flow of items on a conveyor belt.

<br/>

---

<br/>

<br/>

<p align="center"><img width=75% src="support/images/robot_arm.jpg"></p>
<p align="center"> <i> Robot arm with vision system </i> </p>

<br/>


## 3 Parts System

### 1) Vision
- Image acquisition of 3 food/ingredients container.

- Processing of ingredients level (in pixels) within the 3 containers.

- Data communication server (socket) to exchange data between processes

### 2) Optimization
- Optimization of the robot positioning depending (not only) of containers level and ingredients flow

- Timing of the command to be sent to the robot, provided by the optimization algorithm

- Data reception for vision and Serving to Robot control

### 3) Robot Control

- Robot control depending of the optimization commands

- Data reception process

<br/>

<p align="center"><img width=75% src="support/images/robot_arm_diagram.jpg"></p>
<p align="center"> <i> System architecture </i> </p>

<br/>

<br/>

---

<br/>

## Authors (alphabetical order)
- Ashhadul Islam (Ph.D Student)
- Brenno Castrillon Menezes (Assistant Professor)
- Maxime Clement (Software Engineer)
- Mohammad Yaqot (Ph.D Student)
- Robert Eduard Franzoi Junior (PostDoc)
- Shaymaa Fawzi M. Khalifa (Software Engineer)

## Notable technologies used here
- OpenCV
- IMPL
- ZeroMQ
- FCN model
- Python