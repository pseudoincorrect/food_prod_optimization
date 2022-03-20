
## Requirements
- A Windows 10 (or so) computer
- IMPL installed on your computer
- "model.torch" file in ".\food_prod_optimization\vision_model\"
- A Drobot robot !

</br>

---

</br>

## Python install 

Install python (version 3.7)
https://www.python.org/downloads/

Install conda (version 4.10.1)
https://docs.conda.io/projects/conda/en/latest/user-guide/install/windows.html

Update python path by adding to path environment variable :
- %USERPROFILE%\AppData\Local\Programs\Python\Python37\Scripts
- %USERPROFILE%\AppData\Local\Programs\Python\Python37
- %USERPROFILE%\Anaconda3\Scripts

Remove windows alias with setting : "Manage app execution aliases" in windows settings

Create a virtual environment with virtualenv
``` console
$ virtualenv -p %AppData%\Local\Programs\Python\Python37\python.exe main_env  
```

For Windows venv activation error:
``` console
$ Set-ExecutionPolicy Unrestricted -Scope Process
```

Activate the virtual environment (in "vision_optimization" folder)
``` console
$ .\virtualenvs\main_env\Scripts\activate
```

Run the main Scripts
``` console
$ python .\src\main.py
```

Installing package with pip (in virtualenv)
``` console
$ python -m pip install scipy
```

Increase python stack size
- Open a command prompt with administrator right
- Navigate to your python install folder %AppData%\Local\Programs\Python\Python37
``` console
$ editbin /stack:5000000,5000000 excel.exe
```

</br>

---

</br>

## Run the vision program
Open an Anaconda terminal
``` console
$ cd food_prod_optimization\vision
$ conda activate vision_ai 
$ python vision.py
``` 

## Run the optimization program
Open a powershell terminal
``` console
$ cd food_prod_optimization\optimization
$ python optimization.py
``` 

## Run the robot control program
Open a powershell terminal
``` console
$ cd food_prod_optimization\robot
$ python robot_control.py
``` 
