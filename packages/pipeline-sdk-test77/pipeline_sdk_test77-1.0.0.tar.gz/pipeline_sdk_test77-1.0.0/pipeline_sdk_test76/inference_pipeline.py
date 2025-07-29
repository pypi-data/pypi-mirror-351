import kfp.dsl as dsl
from .model_inference_dsl_component import model_inference_dsl_component
from datetime import datetime
 
# Generate dynamic image name with date and time
current_datetime = datetime.now().strftime("%d%b%Y_%H%M%S")
pipeline_name = f"975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:YOLO_Inference_Pipeline_{current_datetime}"
 
# Define pipeline
@dsl.pipeline(
    name=pipeline_name,
    description="Runs YOLO inference on images stored in S3."
)
def inference_pipeline(
    s3_bucket_name: str,
    inference_source_folder: str,  
    image_size: int = 640
):
    """Pipeline for YOLO inference"""
    inference_task = model_inference_dsl_component(
        image_size=image_size,
        s3_bucket_name=s3_bucket_name,
        inference_source_folder=inference_source_folder
    )