classdef LabDBQuery < handle
    %LABDBQUERY MATLAB interface for the labdb ExperimentQuery
    %   This class provides a MATLAB interface to query experiments
    %   using the labdb Python package.
    
    properties (Access = private)
        py_query  % Python ExperimentQuery instance
    end
    
    methods
        function obj = LabDBQuery()
            %LABDBQUERY Constructor
            %   Creates a new LabDBQuery instance
            
            % Import the Python module
            py.importlib.import_module('labdb');
            
            % Create Python instance
            obj.py_query = py.labdb.ExperimentQuery();
        end
        
        function exps = get_experiments(obj, path, varargin)
            %GET_EXPERIMENTS Get experiments at a path
            %   path: Path to get experiments from
            %   Optional arguments:
            %   - recursive: If true, include experiments in subdirectories
            %   - query: Additional query conditions
            %   - projection: Fields to include in results
            %   - sort: Sort specification
            %   - limit: Maximum number of results
            
            % Parse optional arguments
            p = inputParser;
            addParameter(p, 'recursive', false);
            addParameter(p, 'query', []);
            addParameter(p, 'projection', []);
            addParameter(p, 'sort', []);
            addParameter(p, 'limit', []);
            parse(p, varargin{:});
            
            % Convert MATLAB values to Python
            py_query = obj.matlab_to_python(p.Results.query);
            py_projection = obj.matlab_to_python(p.Results.projection);
            py_sort = obj.matlab_to_python(p.Results.sort);
            
            % Get experiments
            py_exps = obj.py_query.get_experiments(path, ...
                'recursive', p.Results.recursive, ...
                'query', py_query, ...
                'projection', py_projection, ...
                'sort', py_sort, ...
                'limit', p.Results.limit);
            
            % Convert Python results to MATLAB
            exps = obj.python_to_matlab(py_exps);
        end
        
        function exp = get_experiment(obj, path)
            %GET_EXPERIMENT Get data for a specific experiment
            %   path: Full path to the experiment
            
            py_exp = obj.py_query.get_experiment(path);
            exp = obj.python_to_matlab(py_exp);
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
        
        function mat_value = python_to_matlab(obj, py_value)
            % Convert Python value to MATLAB
            if isa(py_value, 'py.NoneType')
                mat_value = [];
            elseif isa(py_value, 'py.numpy.ndarray')
                mat_value = double(py_value);
            elseif isa(py_value, 'py.str')
                mat_value = char(py_value);
            elseif isa(py_value, 'py.dict')
                mat_value = struct(py_value);
            elseif isa(py_value, 'py.list')
                mat_value = cell(py_value);
            else
                error('Unsupported Python type for conversion to MATLAB');
            end
        end
    end
end 