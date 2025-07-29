import kfp.dsl as dsl
from model_validate_component import model_validate_component
from kfp.dsl import OutputPath
import os

def get_variables(arg: str):
    if arg== "target_image":
        print( os.environ.get("validate_target_image"))
        return os.environ.get("validate_target_image")
    if arg == "packages_to_install":
        package_install= os.environ.get("validate_packages_to_install")
        if package_install is not None:
            return package_install.split(",")
        else:
            pkg=[]
            return pkg

@dsl.component(
    base_image="975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:basepython8",
    target_image= get_variables("target_image"),
    packages_to_install=get_variables("packages_to_install")
)


def model_validate_dsl_component(
    s3_bucket_name: str,
    s3_source_folder: str,
    trained_model_path:str,
    validation_results: OutputPath('ValidationResults'),

):
    model_validate_component(s3_bucket_name,s3_source_folder, trained_model_path, validation_results)