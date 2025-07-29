# LabDB MATLAB Interface

This directory contains MATLAB helper scripts to interface with the LabDB Python package.

## Quick Start

1. Make sure you have MATLAB R2019b or later installed
2. Make sure you have Python 3.7 or later installed with the LabDB package
3. Add this directory to your MATLAB path:
```matlab
% Option 1: Add from your MATLAB installation of labdb
addpath(fullfile(labdb.get_package_root(), 'matlab'))

% Option 2: Add directly if you know the path
addpath('/path/to/python/site-packages/labdb/matlab')
```

4. Run the setup script:
```matlab
setup_labdb
```

## Usage Examples

### Creating and Logging Experiments

```matlab
% Create a logger instance
logger = LabDBLogger();  % Uses current path
% or
logger = LabDBLogger('/path/to/experiments');

% Create a new experiment
path = logger.new_experiment('my_experiment');

% Log data
logger.log_data('temperature', 25.5);
logger.log_data('measurements', [1, 2, 3, 4, 5]);

% Add notes
logger.log_note('description', 'Test experiment');
```

### Querying Experiments

```matlab
% Create a query instance
query = LabDBQuery();

% Get experiments at a path
exps = query.get_experiments('/path/to/experiments', 'recursive', true);

% Get a specific experiment
exp = query.get_experiment('/path/to/experiment');
```

## Troubleshooting

1. If you get a Python import error:
   - Make sure the LabDB Python package is installed in your Python environment
   - Verify the Python path in MATLAB using `pyenv`
   - Try running `which labdb` in your Python environment to find the installation path

2. If you get a path error:
   - Make sure this MATLAB interface directory is in your MATLAB path
   - Use `which LabDBLogger` to verify the class is found
   - If needed, manually add the path using:
     ```matlab
     addpath('/path/to/python/site-packages/labdb/matlab')
     ```

3. If you get a type conversion error:
   - Make sure your data types are supported (see supported types below)
   - For complex data structures, try converting to a simpler format first

## Supported Data Types

The MATLAB interface supports conversion of the following types:

- Numeric arrays (converted to NumPy arrays)
- Logical arrays (converted to NumPy arrays)
- Strings and character arrays
- Structures (converted to Python dictionaries)
- Cell arrays (converted to Python lists)

## API Reference

### LabDBLogger

- `logger = LabDBLogger(path)` - Create a new logger instance
- `path = logger.new_experiment(name)` - Create a new experiment
- `logger.log_data(key, value)` - Log data to current experiment
- `logger.log_note(key, value)` - Add a note to current experiment

### LabDBQuery

- `query = LabDBQuery()` - Create a new query instance
- `exps = query.get_experiments(path, ...)` - Get experiments at a path
- `exp = query.get_experiment(path)` - Get a specific experiment 