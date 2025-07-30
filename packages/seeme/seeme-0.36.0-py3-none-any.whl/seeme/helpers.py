import os
import zipfile
import pathlib
import pickle
import json
from typing import Union, List

class OptionalDependencyError(Exception):
        pass

def package_version(package_name, include_name=True):
    package = __import__(package_name)
    try:
        package_version = package.__version__
    except:
        from importlib.metadata import version  
        package_version = version(package_name)

    if include_name:
        return f"{package_name}: {package_version}" 
    
    return package_version

def compress_files(path:str=".", files:List=[], compression:int=zipfile.ZIP_DEFLATED, zip_filename:str="my.zip"):
    with zipfile.ZipFile(zip_filename, mode="w") as zf:
        try:
            for filename in files:
                file_to_zip = f"{path}/{filename}"
                zf.write(file_to_zip, compress_type=compression)
        except FileNotFoundError:
            print("FileNotFoundError:")
            print(file_to_zip)
        finally:
            zf.close()

def compress_folder(path:str=".", compression:int=zipfile.ZIP_DEFLATED, zip_filename:str="my.zip"):
    path = pathlib.Path(path)

    with zipfile.ZipFile(zip_filename, mode="w") as archive:
        for file_path in path.iterdir():
            archive.write(file_path, arcname=file_path.name, compress_type=compression)

def save_pkl(data_folder, filename, contents, mode="wb", extension=".pkl"):
    os.makedirs(data_folder, exist_ok=True)
    filename = add_missing_extension(filename, extension)
    full_filename = f"{data_folder}/{filename}"
    pickle.dump(contents, open(full_filename, mode))

def load_pkl(data_folder, filename, mode="rb", extension=".pkl"):
    filename = add_missing_extension(filename, extension)
    full_filename = f"{data_folder}/{filename}"
    return pickle.load(open(full_filename, mode))

def save_dill(folder, filename, contents, mode="wb", extension=".pkl"):
    filename = add_missing_extension(filename, extension)
    required_package = "dill"
    try:
        package = __import__(required_package)
    except ImportError:

        raise OptionalDependencyError(f"Optional dependency '{required_package}' is not installed.")
    full_filename = f"{folder}/{filename}"
    
    with open(full_filename, mode) as f:
        package.dump(contents, f)

def load_dill(folder, filename, mode="rb", extension=".pkl"):
    filename = add_missing_extension(filename, extension)
    required_package = "dill"
    try:
        package = __import__(required_package)
    except ImportError:

        raise OptionalDependencyError(f"Optional dependency '{required_package}' is not installed.")

    full_filename = f"{folder}/{filename}"
    
    with open(full_filename, mode) as f:
    # Load the object from the file using dill.load()
        return  package.load(f)

def save_anything(data_folder, filename, contents, mode="wb", protocol:Union["pkl", "dill"]="pkl", extension=".pkl"):
    if protocol == "pkl":
        save_pkl(data_folder, filename, contents, mode=mode, extension=extension)
        
    elif protocol == "dill":
        save_dill(data_folder, filename, contents, mode=mode, extension=extension)
    
    else:
        raise ValueError(f"Protocol: {protocol} not supported")

def load_anything(data_folder, filename, mode="rb",protocol:Union["pkl", "dill"]="pkl", extension=".pkl"):
    if protocol == "pkl":
        return load_pkl(data_folder, filename, mode=mode, extension=extension)
        
    elif protocol == "dill":
        return load_dill(data_folder, filename, mode=mode, extension=extension)
    else:
        raise ValueError(f"Protocol: {protocol} not supported") 

def save_json(data_folder, filename, contents, mode="w", options={"indent": 4}, extension=".json", force_folder=True):
    """
    Saves a dictionary as a JSON file.
    
    :param data: Dictionary to be saved.
    :param filename: Name of the output file.
    """
    filename = add_missing_extension(filename, extension)
    os.makedirs(data_folder, exist_ok=force_folder)
    full_filename = f"{data_folder}/{filename}"
    with open(full_filename, mode) as f:
        json.dump(contents, f, **options)

def load_json(data_folder, filename, mode='r', options={}, extension=".json"):
    """
    Loads a JSON file into a dictionary.
    
    :param filename: Name of the input file.
    :return: Dictionary loaded from the JSON file.
    """
    filename = add_missing_extension(filename, extension)
    try:
        full_filename = f"{data_folder}/{filename}"
        with open(full_filename, mode) as f:
            return json.load(f, **options)
    except FileNotFoundError:
        print(f"File {filename} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Failed to parse JSON in {filename}.")
        return None

def save_jsonl(data_folder, filename, data_list:List=[], extension:str=".jsonl"):
    """
    Saves a list of dictionaries as a JSONL file.
    
    :param data_list: List of dictionaries to be saved.
    :param filename: Name of the output file.
    """
    filename = add_missing_extension(filename, extension)
    full_filename = f"{data_folder}/{filename}"
    with open(full_filename, 'w') as f:
        for data in data_list:
            json.dump(data, f)
            f.write('\n')

def load_jsonl(data_folder, filename, extension=".jsonl"):
    """
    Loads a JSONL file into a list of dictionaries.
    
    :param filename: Name of the input file.
    :return: List of dictionaries loaded from the JSONL file.
    """
    filename = add_missing_extension(filename, extension)
    full_filename = f"{data_folder}/{filename}"
    data_list = []
    try:
        with open(full_filename, 'r') as f:
            for line in f:
                if line.strip():  # Ignore empty lines
                    data_list.append(json.loads(line))
    except FileNotFoundError:
        print(f"File {filename} not found.")
    except json.JSONDecodeError as e:
        print(f"Failed to parse a line in {filename}: {e}")
    return data_list

def add_missing_extension(filename, ext = ".pkl"):
    if not filename.endswith(ext):
        return f"{filename}{ext}"

    return filename