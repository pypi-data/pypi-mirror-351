# jtheta/__init__.py

# from .client import JThetaClient as Client


############################################################
from .client import JThetaClient

__version__ = "0.1.1.dev1"

_client = None  # global variable

def init(api_key: str):
    """
    Initialize the SDK with the provided API key.
    """
    global _client
    _client = JThetaClient(api_key=api_key)
    return _client

def _require_client():
    if _client is None:
        raise RuntimeError("SDK not initialized. Call `jtheta.init(api_key)` first.")
    return _client

def validate_key():
    return _require_client().validate_key()

def create_project(project_title: str, project_category: str):
    return _require_client().create_project(project_title, project_category)

def create_dataset(dataset_name: str, license: str, project_name: str, image_paths: list[str]):
    return _require_client().create_dataset(dataset_name, license, project_name, image_paths)

def request_annotation(project_name: str, dataset_id: int, assigned_annotator: str, assigned_reviewer: str, labels: list, allow_class_creation: bool, auto_annotation: bool):
    return _require_client().request_annotation(
        project_name, dataset_id, assigned_annotator, assigned_reviewer, labels, allow_class_creation, auto_annotation
    )

def check_annotation_status(project_title: str):
    return _require_client().check_annotation_status(project_title)

def download_dataset(dataset_id: str, format: str = "csv", version: str = "1.0", save_path: str = "dataset.csv"):
    return _require_client().download_dataset(dataset_id, format, version, save_path)

def get_annotators():
    return _require_client().get_annotators()

def get_reviewers():
    return _require_client().get_reviewers()

def upload_images(dataset_id: str, project_name: str, images: str):
    return _require_client().upload_images(dataset_id, project_name, images)


