import kfp.dsl as dsl
from .model_validate_dsl_component import model_validate_dsl_component
from datetime import datetime
 
# Generate a unique pipeline name using current date and time
current_datetime = datetime.now().strftime("%d%b%Y_%H%M%S")
pipeline_name = (
    f"975050071275.dkr.ecr.us-west-2.amazonaws.com/docker:Validate_Model_Pipeline_{current_datetime}"
)
 
@dsl.pipeline(
    name=pipeline_name,
    description="Kubeflow pipeline to validate a YOLO model and log metrics."
)
def validate_pipeline(
    s3_bucket_name: str,
    s3_source_folder: str,
    trained_model_path: str
):
    validate_task = model_validate_dsl_component(
        s3_bucket_name=s3_bucket_name,
        s3_source_folder=s3_source_folder,
        trained_model_path=trained_model_path
    )