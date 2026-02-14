import json
import multiprocessing
import pandas as pd
import sys
import time
from utility_dataframes import read_file_into_dataframe, write_dataframe_to_file
from utility_functions import get_all_files_in_path
from utility_gcam import modify_crop_names

def compile_ehc_scalars(inputs):
    """ 
    Processes and compiles the scalars files generated at run time by the E3SM human component (EHC) and subsequently gets passed into GCAM. 
    The files are located in multiple directories into a single output file that gets written to a .dat or .csv file.

    Parameters:
        inputs: Dictionary with user-specified inputs for the directory paths, the name of the output file, whether we want to standardize the
                crop names, and a list of scenario names, with each scenario in the list corresponding to one directory.

    Returns:
        N/A.
    """
    start_time = time.time()
    input_directories = inputs['input_directories']
    output_file = inputs['output_file']
    call_modify_crop_names = inputs.get('call_modify_crop_names', False)
    scenarios = inputs['scenarios']
    dataframes_for_all_scenarios = []
    for index, scenario in enumerate(scenarios):
        input_directory = input_directories[index]
        files = get_all_files_in_path(input_directory)
        dataframes_for_all_files_for_this_scenario = [read_file_into_dataframe(file) for file in files]
        df = pd.concat(dataframes_for_all_files_for_this_scenario, ignore_index=True)
        # Convert all column names to lowercase.
        df.columns = df.columns.str.lower()
        df = df.sort_values(by='year')
        # Split the landtype_basin column into 'landtype' and 'basin' columns. Delete the original 'landtype_basin' column.
        df[['landtype', 'basin']] = df['landtype_basin'].str.split('_', expand=True)   
        df.drop('landtype_basin', axis=1, inplace=True) 
        df['scenario'] = scenario
        dataframes_for_all_scenarios.append(df)
        
    df = pd.concat(dataframes_for_all_scenarios, ignore_index=True)
    key_columns = ['scenario', 'region', 'basin', 'landtype', 'year']
    df = df.sort_values(by=key_columns)
    df = df[key_columns + ['vegetation', 'soil']]

    # Update original crop names to a common, standardized set of names. 
    if call_modify_crop_names:
        df = modify_crop_names(df, key_columns)

    write_dataframe_to_file(df, output_file)
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time processing/compiling the data for {output_file}: {elapsed_time:.2f} seconds")


###---------------Begin execution---------------###
if __name__ == '__main__':

    # Run this script together with the input JSON file(s) on the command line.
    start_time = time.time()
    if len(sys.argv) < 2:
        print('Usage: python gcam_compile_ehc_scalars.py `path/to/json/input/file(s)\'')
        sys.exit()

    # Read and load the JSON file(s) into a list of dictionaries.
    list_of_inputs = []
    for i in range(1, len(sys.argv)):
        input_file = sys.argv[i]
        with open(input_file) as f:
            list_of_inputs.extend(json.load(f))

    # Produce data for each file in parallel.
    # Limit processes to reduce memory pressure - use at most 16 processes or half of available CPUs.
    max_processes = min(16, multiprocessing.cpu_count() // 2) 
    with multiprocessing.Pool(processes=max_processes) as pool:
        pool.map(compile_ehc_scalars, list_of_inputs)
    
    # Print the total execution time needed to process/compile the scalars for all files.
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Elapsed time processing/compiling the data for all files: {elapsed_time:.2f} seconds")