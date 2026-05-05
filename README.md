# Bike Plotting Tools

This project provides tools for bike enthusiasts that should help with purchasing decisions and comparing different bikes.

## Features
For now, it only includes a gear ratio plotting tool that, given comfortable RPMs and relevant bike specs, plots the speeds that can be achieved at those RPMs for all gear combinations. The plot is designed to be easily comparable between different bikes, so you can quickly see which bike has more or less overlap in gear ratios, which one has more low or high gears, etc.

### Other tools that may be added in the future:
* bike geometry comparison tool  
  an interactive visualisation of bike geometry. A solver auomatically calculates missing values in real-time as new values are entered.

## Usage
The gear ratio plotting tool can be used by running `gear_plotting.py`. You can edit the bike specs and comfortable RPMs at the top of the file and specify bikes to compare at the bottom. By default, the plot will be saved as `gear_ratios.png` in the current directory.
Once all configurations are set, run the script (e.g. via `python gear_plotting.py` in a terminal) and the plot will be generated and saved.