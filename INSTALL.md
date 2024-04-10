## Python Installation
This program requires Python 3.11 or later. Using a virtual environment manager (such as conda) is highly recommended. The following instructions are for people new to Python or VS Code. If you already know how to handle Python versions and environments, please skip to [Installing Dependencies](#installing-dependencies).
### Installing Conda
> **What is conda?**  
> Each python project you may want to run on your computer can have its specific python version and library dependency requirements (look at the first sentence in the paragraph above!). If you try to cram everything into one python installation, you will soon run into conflicts.  
> Conda is a package manager that allows you to create isolated environments for each project. You only install the required version of python and libraries for that project and nothing more, keeping everything lean and clean!


Download the latest version of Miniconda from its [official website](https://docs.anaconda.com/free/miniconda/index.html#latest-miniconda-installer-links) for your operating system.

**If you are on Windows, and want to use VS Code with Conda**  
In Start Menu, search "Anaconda Powershell Prompt". Then run the following commands:

Initialize conda for powershell command line
```powershell
conda init powershell
```

Set conda to manual activation (recommended but optional)
```powershell
conda config --set auto_activate_base false
```

Allow the startup script to run when you open the VS Code terminal
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```
You will likely see some red warnings at this point, but as long as it starts with 
`Set-ExecutionPolicy : Windows PowerShell updated your execution policy successfully`, you are good to go.

**If you are on Linux**  
You can initialize conda with
```bash
conda init bash  # or zsh if you are into that
conda config --set auto_activate_base False # Set to manual activation
```
Please refer to [official documentation for Linux](https://docs.anaconda.com/anaconda/install/linux/).

**If you are on MacOS**  
Then you are a lot richer than me, and I have no idea how conda works on your fancy machine.  
Please refer to [official documentation for MacOS](https://docs.anaconda.com/anaconda/install/mac-os/).

### Creating a New Conda Environment
Assuming you are using VS Code and you have done the steps above correctly...

Open the project folder in VS Code. Press `Ctrl` + `` ` `` to bring up the terminal.  
Run the following commands to create a new conda environment called "eddy".
```powershell
conda create -n eddy python=3.11 -y
```
Then switch to the new environment with
```powershell
conda activate eddy
```
You should now see `(eddy)` at the beginning of the command line if it is successfully activated.

> Note: VS Code will try to automatically activate the "eddy" environment when you open the project folder in the future. However, sometimes it fails to do so. You can always manually activate it with the command above.

### VS Code Python Extension
On the Extensions tab on the left, search for "Python" and install the one by Microsoft.

Now, open any Python file in the project folder. If you try to click the "Run" button on the top right, a pop-up will appear, asking you for a Python interpreter. Select the one with "eddy" in its name. You can also do this from the bottom right corner of the VS Code window. *If nothing is listed, restart VS Code so it can detect the new conda changes*.

> Note: Selecting Python interpreter here and activating conda environment in the terminal are two independent actions. You should make sure both are set correctly.  
> ***Hopefully***, they will both be set automatically from now on. But please double-check each time you reopen VS Code.

### Installing Dependencies
Currently, this program only requires `numpy`, `matplotlib` and `tqdm` to use.  
If you want to run the test cases, you will also need `pytest` and `pytest-cov`.

If you have opened the project folder in VS Code, you can install them all with
```bash
pip install -r requirements.txt
```

or you can install them selectively with
```bash
pip install numpy matplotlib tqdm  # Required for the program itself
pip install pytest pytest-cov      # Required for running tests
```
