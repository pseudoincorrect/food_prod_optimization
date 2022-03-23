# REQUIREMENTS

- A Windows 10 (or so) computer
- IMPL installed on your computer
- "model.torch" file in ".\food_prod_optimization\vision_model\"
- A Drobot robot !

</br>

---

</br>

# INSTALLATION


## Installing Python, Virtualenv and Conda

Install python (version 3.7)
https://www.python.org/downloads/

Install conda (version 4.10.1)
https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html

Update python path by adding to path environment variable :
- %USERPROFILE%\AppData\Local\Programs\Python\Python37\Scripts
- %USERPROFILE%\AppData\Local\Programs\Python\Python37
- %USERPROFILE%\Anaconda3\Scripts

Remove windows alias with setting : "Manage app execution aliases" in windows settings

Installing virtualenv with pip 
``` console
$ pip install virtualenv
```

</br>

## Installing the vision program

Create a conda environment
``` console
$ cd food_prod_optimization\food_prod_optimization\vision
$ conda env create -f vision_conda_environment.yaml
```

</br>

## Installing the optimization program

Create a virtual environment with virtualenv
``` console
# Use absolute path, not %LocalAppData%
$ virtualenv -p %LocalAppData%\Programs\Python\Python37\python.exe env  
```

Activate the virtual environment
and set execution policy (Windows venv activation error)
``` console
$ cd food_prod_optimization\food_prod_optimization\optimization
$ Set-ExecutionPolicy Unrestricted -Scope Process
$ .\env\Scripts\activate
```

Install necessary packages
``` console
$ python -m pip install zmq
```

Increase python stack size
- Open a command prompt with administrator right
- Navigate to your python install folder %LocalAppData%\Local\Programs\Python\Python37
``` console
$ editbin /stack:5000000,5000000 excel.exe
```

</br>

## Installing the robot arm program

Create a virtual environment with virtualenv
``` console
# Use absolute path, not %LocalAppData%
$ virtualenv -p %LocalAppData%\Programs\Python\Python37\python.exe env  
```

Activate the virtual environment
and set execution policy (Windows venv activation error)
``` console
$ cd food_prod_optimization\food_prod_optimization\robot
$ Set-ExecutionPolicy Unrestricted -Scope Process
$ .\env\Scripts\activate
```

install necessary packages (local and online ones)
``` console
# move to the repo folder
$ cd food_prod_optimization\food_prod_optimization\robot
# unzip packages
$ cd vendor
$ Expand-Archive vendor.zip -DestinationPath .
# move to the first local package and install it 
$ cd cri
$ pip install -e .
# move to the second local package and install it
$ cd ../cri_dobot
$ pip install -e .
# install ZeroMQ and Keyboard packages
$ pip install zmq keyboard
```

</br>

---

</br>

# USAGE 

</br>

## Running the vision program
Open an Anaconda terminal
``` console
$ cd food_prod_optimization\vision
$ conda activate vision_ai 
$ python vision.py
``` 

</br>

## Running the optimization program
Open a powershell terminal
``` console
$ cd food_prod_optimization\optimization
$ Set-ExecutionPolicy Unrestricted -Scope Process
$ .\env\Scripts\activate
$ python optimization.py
``` 

</br>

## Running the robot control program
Open a powershell terminal
``` console
$ cd food_prod_optimization\robot\robot
$ Set-ExecutionPolicy Unrestricted -Scope Process
$ .\env\Scripts\activate
$ python robot_control.py --home 
``` 
