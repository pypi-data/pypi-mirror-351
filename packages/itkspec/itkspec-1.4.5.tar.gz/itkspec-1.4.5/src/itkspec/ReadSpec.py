### imports
import os.path
import os
import pandas as pd
from ast import literal_eval


### template info. for user input
infoDict_template={'project':None, 'componentType':None, 'testType':None, 'stage':None, 'parameter':None}
## copy function - for use in functions
def copyTemplate():
    return infoDict_template.copy()


### Function for returning a single spec from a unique parameter
def getSpec(**kwargs):
    inCheck = True
    core_keys = ['project', 'componentType', 'testType', 'stage', 'parameter']

    # Check for missing core labels
    if any(kwargs.get(label) is None for label in core_keys):
        print(" there's a core label missing. Please check inputs.")
        inCheck = False

    # Determine the file name
    fileName = "_".join([kwargs['project'], kwargs['componentType']]) + ".csv"

    # Check if the file exists
    if fileName is not None:
        # Get root directory
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the spec_files directory
        spec_files_directory = os.path.join(current_directory, "spec_files")
        print(f"  csv files directory: {spec_files_directory}")

        # Construct the full path to the file
        file_path = os.path.join(spec_files_directory, fileName)
        try:
            os.path.isfile(file_path)
            print(f"  file path: {file_path}\n")
        except FileNotFoundError:
            print("Error: This specification file does not exist yet or inputs are incorrect.")
            inCheck = False

    if not inCheck:
        print("returning nothing :(")
        return pd.DataFrame()

    # Open the file and get spec data
    print("# getting spec from csv #\n")
    df_csv = pd.read_csv(file_path, converters={"spec": literal_eval})

    queryStr=f'project==\"{kwargs["project"]}\" & componentType==\"{kwargs["componentType"]}\" & parameter==\"{kwargs["parameter"]}\"'
    print(f"query spec using: \n{queryStr}\n")

    df_spec=df_csv.query(queryStr)

    if df_spec.empty:
        print(" - empty spec csv :(.")
        return pd.DataFrame()
    else:
        spec_dict = df_spec.to_dict()
        out_dict = {
            'parameter': spec_dict['parameter'][0],
            'spec': spec_dict['spec'][0]
        }
        print(df_spec.to_markdown())
    return out_dict


### Function for returning multiple specs from various parameters
def getSpecList(**kwargs):
    inCheck = True
    core_keys = ['project', 'componentType', 'testType', 'stage']

    # Check for missing core labels
    if any(kwargs.get(label) is None for label in core_keys):
        print(" there's a core label missing. Please check inputs.")
        inCheck = False

    # Determine the file name
    fileName = "_".join([kwargs['project'], kwargs['componentType']]) + ".csv"

    # Check if the file exists
    if fileName is not None:
        # Get the main directory
        current_directory = os.path.dirname(os.path.abspath(__file__))

        # Construct the full path to the spec_files directory
        spec_files_directory = os.path.join(current_directory, "spec_files")
        print(f"  csv files directory: {spec_files_directory}")

        # Construct the full path to the file
        file_path = os.path.join(spec_files_directory, fileName)
        try:
            os.path.isfile(file_path)
            print(f"  file path: {file_path}")
        except FileNotFoundError:
            print("Error: This specification file does not exist yet or inputs are incorrect.")
            inCheck = False

    if not inCheck:
        print("returning nothing :(")
        return pd.DataFrame()

    # Open the file and get spec data
    print("# getting spec from csv #\n")
    df_csv = pd.read_csv(file_path, converters={"spec": literal_eval})

    queryStr=f'project==\"{kwargs["project"]}\" & componentType==\"{kwargs["componentType"]}\"'
    print(f"query spec using: \n{queryStr}\n")
    
    df_spec=df_csv.query(queryStr)

    if df_spec.empty:
        print(" - empty spec csv :(.")
        return pd.DataFrame()
    else:
        spec_dict = df_spec.to_dict()
        out_dict = {
            'parameter': list(spec_dict['parameter'].values()),
            'spec': list(spec_dict['spec'].values())
        }
        print(df_spec.to_markdown())
        print(out_dict)
    return out_dict


def listSpecFiles():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    spec_files_directory = os.path.join(current_directory, "spec_files")
    
    ## get list of (csv) files in directory
    csv_list=os.listdir(spec_files_directory)
    ## filter csv files
    csv_list=[x for x in csv_list if ".csv" in x]
    
    print(f"csv files in directory: {csv_list}")
    return csv_list