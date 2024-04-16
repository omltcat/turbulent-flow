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
│   ├── qeuries     # put query files here, contains examples
│   ├── results     # raw results will be saved here
│   └── plots       # plots will be saved here
├── test    # test cases
│   └── system      # system test cases
│── requirements.txt    # dependencies
├── INSTALL.md
└── README.md
```

## Installation
Please refer to the [INSTALL.md](INSTALL.md) for detailed installation instructions.

Makefile WIP for people with make and conda installed:


## Usage
First, enter the source code directory:
```bash
cd src
```
### Creating a new flow field
```bash
# view help
python main.py new -h

# create a new 20x20x20 field named "test", using the provided "example" eddy profile
python main.py new -p example -n test -d 20 20 20
```
Since we did not pass average velocity (-v) the default value 0.0 will be used.

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
python main.py query -h

# query the flow field "test" with the provided "example_meshgrid" query file
python main.py query -n test -q example_meshgrid
```
Since we did not pass shape function (-s) and cutoff (-c), the default values "gaussian" and 2.0 will be used.

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