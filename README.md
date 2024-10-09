# Synthetic Eddy for Turbulent Flow Simulation

Developer Names: Phil Du (Software), Nikita Holyev (Theory)

Date of project start: 2024-01-19

This project is to generate 3D velocity fields consist of synthetic eddies, mimicking turbulent flows, and to be used as initial conditions by turbulent CFD simulations.

The folders and files for this project are as follows:

```
.
├── doc                   
│   ├── SRS        
|   ├── Design
│   |   ├── SoftArchitecture (MG)
│   │   └── SoftDetailedDes (MIS)                 
│   ├── VnVPlan 
│   └── VnVReport                
│── src     # source code         
│   ├── main.py     # main file to run the software          
|   ├── modules     # modules of the software
│   ├── profiles    # put eddy profiles here, contains examples
│   ├── queries     # put query files here, contains examples
│   ├── results     # raw results will be saved here
│   └── plots       # plots will be saved here
├── test    # test cases
│   └── system      # system test cases
│── requirements.txt    # dependencies
├── INSTALL.md
├── README.md
└── Makefile        # Quick start commands
```

## Quick Start
If you have **Make** and **Conda** installed, and just want to quickly see this program in action, you can run the following commands.  
Otherwise, see [Installation](#installation) and [Usage](#usage).
```bash
make install # create a new conda environment named "eddy" and install dependencies

make run # create a new flow field with example profile, query it and see a plot

make test # run the unit and system test cases

make clean # remove the conda environment
```


## Installation
This program requires Python 3.11 or later. The use of a virtual environment manager (such as Conda) is highly recommended. 

If such concepts are new to you, please refer to the [INSTALL.md](INSTALL.md) for detailed installation instructions.

If you are familiar with Python, you can install the dependencies of this program with:
```bash
pip install -r requirements.txt
```


## Usage
### Creating a new flow field
```bash
# view help
python ./src/main.py new -h
```
```bash
# create a new 20x20x20 (m^3) field named "test", using the provided "example" eddy profile
python ./src/main.py new -p example -n test -d 20 20 20
```
Since we did not pass average velocity (`-v`) the default value `0.0` (m/s) will be used.

The example profile can be found at **src/profiles/example.json**. It contains several variants of eddies, each with parameters for density, intensity, and length scale:
```json
{
    "settings": {},                 // not implemented yet
    "variants": [
        {
            "density": 200.0,       // the number of eddies in the a unit volume
            "intensity": 0.75,      // the intensity, magnitude of alpha (see SRS)
            "length_scale": 0.1     // the length scale, also known as sigma (see SRS)
        },
        ...
}
```

### Querying the flow field
```bash
# view help
python ./src/main.py query -h
```
```bash
# query the flow field "test" with the provided "example_meshgrid" query file
python ./src/main.py query -n test -q example_meshgrid
```
Since we did not pass shape function (`-s`) and cutoff (`-c`), the default values `gaussian` and `2.0` will be used.

The example query file can be found at **src/queries/example_meshgrid.json**. It contains the definition of a meshgrid, which is only a 2D slice to save computing time. The instruction to plot the result is also included:
```json
{
    "mode": "meshgrid",
    "params": {
        "low_bounds": [-10, -10, 0],    // the lower bounds of the meshgrid, both z = 0 for 2D
        "high_bounds": [10, 10, 0],     // the upper bounds of the meshgrid, both z = 0 for 2D
        "step_size": 0.1,               // the step size (resolution) of the meshgrid
        "chunk_size": 5,                // how many points in each direction in a chunk
        "time": 0                       // time to query
    },
    "plot": {
        "axis": "z",                // the axis perpendicular to the plot cross-section
        "index": 0,                 // the index along the axis to plot the cross-section
        "size": [1280, 960]         // save image size
    }
} 
```

After the run, you should see a plot pop-up. The raw result and the plot will be saved in **src/results** and **src/plots** respectively.

### Result file
The result is saved as a NumPy array (`.npy` file), which you can load and manipulate with your own program.

The shape of the array is `(Nx, Ny, Nz, 3)` where `N` is the number of grid points in each direction, and the last dimension represents $x$, $y$, and $z$ components of the velocity vector.

Please note that for a fine meshgrid, the file size can be large, and you may have a hard time transferring it to another machine. In such case, be prepared to consume the result in the same machine where it was generated.

For testing purposes, use a coarse meshgrid.

### Customization
`SynthEddy` allows user to define their own eddy shape function and non-uniform mean velocity profile. 

#### Non-uniform mean velocity distribution
If your flow field need a non-uniform mean velocity distribution in the $x$ direction, such as channel flow, it can be defined in [x_velocity.py](src/modules/x_velocity.py). Detailed explanation on how the velocity distribution is defined and examples are provided in the file.

This function name is then passed in command line with `-x` when creating a new field. If a velocity function is passed, the velocity argument `-v` will specify the velocity when the function outputs `1.0`:
```bash
python ./src/main.py new -p eddy_profile -n field_name -d 20 20 20 -x my_x_velocity -v 5.0
```

#### Eddy shape function
The shape function describes the velocity distribution of individual eddies. You may define yours in [shape_functions.py](src/modules/shape_function.py). Detailed explanation and example (default `gaussian`) are provided in the file.

The function name is then passed in command line with `s` when querying. Cutoff (`-c`) in multiples length scale can also be specified:
```bash
python ./src/main.py query -n field_name -q grid_name -s my_shape_function -c 2.0
```

### Running the test cases
```bash
# System and unit test cases, same ones in GitHub Actions
pytest --cov=src --cov-fail-under=95 -m "(unit or system) and not slow"
```
```bash
# Performance benchmark with 1000^3 meshgrid and 10 million eddies
pytest -s -m "performance"
```
