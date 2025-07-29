function setup_labdb()
%SETUP_LABDB Setup the LabDB MATLAB interface
%   This script helps set up the LabDB MATLAB interface by:
%   1. Verifying the Python environment
%   2. Testing the Python package import
%   3. Verifying MATLAB class access

    fprintf('Setting up LabDB MATLAB interface...\n\n');
    
    % Check Python environment
    try
        py_env = pyenv;
        fprintf('Current Python environment:\n');
        fprintf('  Version: %s\n', py_env.Version);
        fprintf('  Executable: %s\n', py_env.Executable);
        fprintf('  Status: %s\n\n', py_env.Status);
    catch
        warning('Python environment not configured.');
        fprintf('Please configure Python using one of these methods:\n');
        fprintf('1. Let MATLAB choose a compatible version:\n');
        fprintf('   pyenv(''Version'', ''3.7'')\n\n');
        fprintf('2. Specify a specific Python installation:\n');
        fprintf('   pyenv(''Version'', ''/path/to/python'')\n\n');
        return;
    end
    
    % Test Python import
    try
        py.importlib.import_module('labdb');
        fprintf('Successfully imported labdb Python package\n\n');
    catch e
        warning('Failed to import labdb Python package.');
        fprintf('Error: %s\n\n', e.message);
        fprintf('Please ensure:\n');
        fprintf('1. The labdb package is installed in your Python environment:\n');
        fprintf('   pip install labdb\n\n');
        fprintf('2. You are using the correct Python environment:\n');
        fprintf('   which python  # in terminal\n');
        fprintf('   !which python  # in MATLAB\n\n');
        return;
    end
    
    % Test MATLAB classes
    try
        logger_path = which('LabDBLogger');
        query_path = which('LabDBQuery');
        
        if isempty(logger_path) || isempty(query_path)
            error('MATLAB interface classes not found in path');
        end
        
        fprintf('Found MATLAB interface classes:\n');
        fprintf('  Logger: %s\n', logger_path);
        fprintf('  Query: %s\n\n', query_path);
    catch e
        warning('Failed to find MATLAB interface classes.');
        fprintf('Error: %s\n\n', e.message);
        fprintf('Please ensure this directory is in your MATLAB path:\n');
        fprintf('  addpath(fullfile(labdb.get_package_root(), ''matlab''))\n\n');
        return;
    end
    
    fprintf('Setup complete! Try running this example:\n\n');
    fprintf('  logger = LabDBLogger();\n');
    fprintf('  path = logger.new_experiment(''test'');\n');
    fprintf('  logger.log_data(''example'', 42);\n\n');
end 