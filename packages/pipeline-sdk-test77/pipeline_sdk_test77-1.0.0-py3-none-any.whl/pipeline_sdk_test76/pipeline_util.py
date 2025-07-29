import subprocess
import os

def build_kfp_component(component_file: str):
    
    component_file_name =  component_file+"_dsl_component.py"
    
    source_path = f"/opt/conda/lib/python3.11/site-packages/pipeline_sdk_test77/{component_file_name}"
    destination_path = "."

    command_copy = ["cp", source_path, destination_path]
    result_copy = subprocess.run(command_copy, capture_output=True, text=True)
    if result_copy.returncode == 0:
        print("Command executed successfully!")
        print("Output:", result_copy.stdout)
    else:
        print("Command failed!")
        print("Errors:", result_copy.stderr)
        
    command = [
        "kfp", "component", "build", ".",
        "--component-filepattern", component_file_name,
        "--push-image"
    ]
    
    result = subprocess.run(command, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("Command executed successfully!")
        print("Output:", result.stdout)
    else:
        print("Command failed!")
        print("Errors:", result.stderr)
        
        
    command_rm = ["rm", component_file_name]    
    result_rm = subprocess.run(command_rm, capture_output=True, text=True)
    
    if result_rm.returncode == 0:
        print("Command executed successfully!")
        print("Output:", result_rm.stdout)
    else:
        print("Command failed!")
        print("Errors:", result_rm.stderr)
        
        
def populate_args(train_input: dict=None, validate_input: dict=None, inference_input: dict=None, local_directory: str=""):
    
    os.environ["local_directory"]=local_directory
    
    if train_input is not None:
        for key, value in train_input.items():
            if key == "train_target_image":
                formattedValue="975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:"+value
                os.environ[key]=formattedValue
            elif key == "train_packages_to_install":
                os.environ[key]=value
    if validate_input is not None:
            for key, value in validate_input.items():
                    if key == "validate_target_image":
                        formattedValue="975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:"+value
                        print("validate iamge")
                        print(formattedValue)
                        os.environ[key]=formattedValue
                    elif key == "validate_packages_to_install":
                        os.environ[key]=value
    if inference_input is not None:
            for key, value in inference_input.items():
                    if key == "inference_target_image":
                        formattedValue="975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:"+value
                        os.environ[key]=formattedValue
                    elif key == "inference_packages_to_install":
                        os.environ[key]=value
