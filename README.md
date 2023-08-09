# crypto-data
This module is to collect public market data from crypto exchanges.


## Anaconda - Setting up a Python environment

Download and install Anaconda from https://www.anaconda.com/. Select all the checkboxes during the installation steps.

After installation, open `Anaconda Powershell Prompt` to create a Python 3.7 environment with the name `py37-crypto` by typing:
```
> conda create -n py37-crypto python=3.7
```
Multiple environments of different Python version can be created for other projects. To see the list of Anaconda environments (which include py37-smu) and the installation directory:

```
> conda info --envs
```
Each environment installation directory contains the `python.exe`, and we will need this path for configuring PyCharm later. Go to the directy to explore more.

We are going to install more libraries in `py37-crypto` environment. First activate it:

```
> conda activate py37-crypto
```
To check Python version is 3.7, enter the following:
```
> python --version
```

Next install the project's dependency with the following libraries (sometimes called packages):
```
> conda install -c anaconda requests
> conda install -c conda-forge websockets
> conda install -c conda-forge python-binance

```

To get the list of packages installed:
```
> conda list
```


## PyCharm - Integrated Development Environment (IDE)
Download and install Anaconda from https://www.anaconda.com/.
Git clone this repository, then setup PyCharm:
1. Open this project by `File` -> `Open...` -> select/navigate to folder `crypto-data`
2. Configure Python interpreter by `File` -> `Settings...` -> `Project: crypto-data` -> `Python Interpreter` -> `Add Local Interpreter` -> `Conda Environment` -> `Use Existing environment` -> `py37-smu`

