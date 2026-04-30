# Drone Detection Algorithm

This project provides the analytical overview of the data in https://huggingface.co/datasets/lll-a-p/fpv-drone-detection-dataset and provides implementation and analysis of proposed 4 algorithms: Sync Counting, FFT, Autocorrelation, Mathced Filtering. The data from dataset has to be unpacked and moved to the `./data` folder.

# The Project structure
- `python/analysis.ipynb` - Holds the dataset loader, datases analysis, methods qualitive analysis, methods implementations
- `python/benchmarks.ipynb` - Holds plotters for the benchmarks
- `python/benchmarks_runner.py` - App to collect benchmarks: connects to a board via Serial port and runs methods. Stores results in a csv file. The source passed in parameters
- `src` - Folder for Submodule with cross-platform firmware
- `imgs` - Folder with stored plots from the `.ipynb` files
- `data` - Folder for data outputs
- `data/benchmarks.csv` - combined results of `python/benchmarks_runner.py` on both ESP and STM boards.

# Use
0. Pull recursively to get the Submodule with Firmware
1. Install requirements
```
pip install -r ./python/requirements.txt
```
2. Run the `analysis.ipynb` to get the plots from the work
3. Follow run instructions in the Submodules project with platform
4. Run the `benchmarks_runner.py` to obtain benchmarks
5. Run the `benchmarks.ipynb` to plot the results

