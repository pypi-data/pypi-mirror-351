import kfp.dsl as dsl
from model_inference_component import model_inference_component
from kfp.dsl import OutputPath
import os

def get_variables(arg: str):
    if arg== "target_image":
        return os.environ.get("inference_target_image")
    if arg == "packages_to_install":
        package_install= os.environ.get("inference_packages_to_install")
        if package_install is not None:
            return package_install.split(",")
        else:
            pkg=[]
            return pkg



@dsl.component(
    base_image="975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:basepython16",
    target_image=get_variables("target_image"),
    #"975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:yolo_inference_pipeline_DCSF31",
    packages_to_install=get_variables("packages_to_install")
)
def model_inference_dsl_component(
     inference_results: OutputPath('InferenceResults'),  
     performance_metrics: OutputPath('PerformanceMetrics'), 
     inference_dataset: dsl.OutputPath("InferenceDataset"),
     image_size: int,  
     s3_bucket_name: str,  
     inference_source_folder: str 
):
    model_inference_component( inference_results, performance_metrics, inference_dataset, image_size, s3_bucket_name, inference_source_folder)
    