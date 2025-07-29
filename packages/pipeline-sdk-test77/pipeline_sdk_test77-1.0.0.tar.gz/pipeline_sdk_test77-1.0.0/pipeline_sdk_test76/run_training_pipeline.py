import kfp
from kfp.compiler import Compiler
from .train_pipeline import train_pipeline
from .auth_service import get_auth_token
from typing import List
from datetime import datetime
import logging
from config import Config
from typing import Callable, Optional


def run_pipeline(
    s3_bucket_name: str,
    s3_source_folder: str
):
    """
    Runs the Train pipeline using Kubeflow Pipelines.
    """
    KFP_HOST = Config.KFP_HOST
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
 
    token = get_auth_token()
    SESSION_COOKIE = f"authservice_session={token}"
    print(f"SESSION_COOKIE: {SESSION_COOKIE}")
 
    client = kfp.Client(host=KFP_HOST, cookies=SESSION_COOKIE)
 
    experiment_name = "yolo_experiment"
 
    experiment = client.get_experiment(experiment_name=experiment_name)
    if experiment is None:
        experiment = client.create_experiment(name=experiment_name)
 
    run_name = f"yolo_train_pipeline_{timestamp}"
    NAMESPACE = "kubeflow-user-example-com"
 
    # Submit pipeline run
    clientResults = client.create_run_from_pipeline_func(
        train_pipeline,
        arguments={
            "s3_bucket_name": s3_bucket_name,
            "s3_source_folder": s3_source_folder
        },
        experiment_name=experiment_name,
        run_name=run_name,
        namespace=NAMESPACE
    )
 
if __name__ == "__main__":
    run_pipeline(
        "yolo-new-bucket",
        "yolo_datasets/"
    )