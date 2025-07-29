import kfp.dsl as dsl
from .model_train_dsl_component import model_train_dsl_component
from datetime import datetime
from typing import Callable
from kfp.dsl import component, pipeline


 
# Generate a unique pipeline name using current date and time
current_datetime = datetime.now().strftime("%d%b%Y_%H%M%S")
pipeline_name = (
    f"975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:Train_Model_Pipeline_{current_datetime}"
)
 
@dsl.pipeline(
    name=pipeline_name,
    description="Kubeflow pipeline to train a YOLO model and log metrics."
)
def train_pipeline(
    s3_bucket_name: str,
    s3_source_folder: str,
    epochs: int = 1,
    imgsz: int = 640
):
    
    train_task = model_train_dsl_component(
        epochs=epochs,
        imgsz=imgsz,
        s3_bucket_name=s3_bucket_name,
        s3_source_folder=s3_source_folder
    )