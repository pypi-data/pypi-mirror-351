classdef LabDBLogger < handle
    %LABDBLOGGER MATLAB interface for the labdb ExperimentLogger
    %   This class provides a MATLAB interface to create and log experiments
    %   using the labdb Python package.
    
    properties (Access = private)
        py_logger  % Python ExperimentLogger instance
    end
    
    methods
        function obj = LabDBLogger(path)
            %LABDBLOGGER Constructor
            %   Creates a new LabDBLogger instance
            %   path: Optional path to work with (defaults to current path)
            
            if nargin < 1
                path = [];
            end
            
            % Import the Python module
            py.importlib.import_module('labdb');
            
            % Create Python instance
            if isempty(path)
                obj.py_logger = py.labdb.ExperimentLogger();
            else
                obj.py_logger = py.labdb.ExperimentLogger(path);
            end
        end
        
        function path = new_experiment(obj, name)
            %NEW_EXPERIMENT Create a new experiment
            %   Creates a new experiment and returns its path
            %   name: Optional name for the experiment
            
            if nargin < 2
                name = [];
            end
            
            path = char(obj.py_logger.new_experiment(name));
        end
        
        function log_data(obj, key, value)
            %LOG_DATA Log data to the current experiment
            %   key: The key to store the data under
            %   value: The value to store (can be any MATLAB type)
            
            % Convert MATLAB value to Python
            py_value = obj.matlab_to_python(value);
            obj.py_logger.log_data(key, py_value);
        end
        
        function log_note(obj, key, value)
            %LOG_NOTE Add a note to the current experiment
            %   key: The key to store the note under
            %   value: The value to store (must be JSON serializable)
            
            % Convert MATLAB value to Python
            py_value = obj.matlab_to_python(value);
            obj.py_logger.log_note(key, py_value);
        end
    end
    
    methods (Access = private)
        function py_value = matlab_to_python(obj, value)
            % Convert MATLAB value to Python
            if isempty(value)
                py_value = py.None;
            elseif isnumeric(value)
                py_value = py.numpy.array(value);
            elseif islogical(value)
                py_value = py.numpy.array(value);
            elseif ischar(value) || isstring(value)
                py_value = char(value);
            elseif isstruct(value)
                py_value = py.dict(value);
            elseif iscell(value)
                py_value = py.list(value);
            else
                error('Unsupported MATLAB type for conversion to Python');
            end
        end
    end
end 