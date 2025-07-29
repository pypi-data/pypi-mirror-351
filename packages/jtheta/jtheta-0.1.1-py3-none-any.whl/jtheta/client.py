import requests

class JThetaClient:
    def __init__(self, api_key: str, base_url: str = "https://api.jtheta.ai/api"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    def validate_key(self):
        url = f"{self.base_url}/validate_key/"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def create_project(self, project_title: str, project_category: str):
        url = f"{self.base_url}/create_project/"
        payload = {
            "project_title": project_title,
            "project_category": project_category
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()

    def create_dataset(self, dataset_name: str, license: str, project_name: str, image_paths: list[str]):
        url = f"{self.base_url}/datasets/create"
        
        # Prepare form data
        data = {
            "dataset_name": dataset_name,
            "license": license,
            "project_name": project_name
        }
        
        # Prepare image files
        files = []
        for path in image_paths:
            files.append(('images', (path, open(path, 'rb'), 'image/jpeg')))
        headers_form = {
            "Authorization": f"Bearer {self.api_key}"
        }
        response = requests.post(url, headers=headers_form, data=data, files=files)
        response.raise_for_status()
        return response.json()

    def request_annotation(self, project_name: str,dataset_id: int,assigned_annotator: str, assigned_reviewer: str, labels: list,allow_class_creation: bool, auto_annotation: bool):
        url = f"{self.base_url}/annotation/request"
        payload = {
            "project_name": project_name,
            "dataset_id": dataset_id,
            "assigned_annotator": assigned_annotator,
            "assigned_reviewer": assigned_reviewer,
            "labels": labels,
            "allow_class_creation": allow_class_creation,
            "auto_annotation": auto_annotation
        }
        response = requests.post(url, headers=self.headers, json=payload)
        response.raise_for_status()
        return response.json()    
    

    def check_annotation_status(self, project_title: str) -> dict:
        """
        Get the status of a specific annotation by its ID.

        Args:
            annotation_id (str): The ID of the annotation to retrieve the status for.

        Returns:
            dict: The response from the API.
        """
        url = f"{self.base_url}/annotation/status/{project_title}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def download_dataset(self, dataset_id: str, format: str, version: str) -> str:
        """
        Download a dataset export.

        Args:
            dataset_id (str): The ID of the dataset to download.
            format (str): The format of the export (default: "csv").
            version (str): The version of the dataset (default: "1.0").
            save_path (str): Local path to save the downloaded dataset.

        Returns:
            str: Path to the saved file.
        """
        url = f"{self.base_url}/dataset/export/{dataset_id}/download/?format={format}&version={version}"
        response = requests.get(url, headers=self.headers, stream=True)
        response.raise_for_status()

        return response.json() 

    def get_annotators(self):
        url = f"{self.base_url}/get_annotators/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def get_reviewers(self):
        url = f"{self.base_url}/get_reviewers/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def upload_images(self, dataset_id: str, project_name: str, images: str):
        url = f"{self.base_url}/dataset/upload_images"

        data = {
            "dataset_id": dataset_id,
            "project_name": project_name
        }

        ext = images.split('.')[-1].lower()
        content_type = f'image/{ext if ext != "jpg" else "jpeg"}'
        with open(images, 'rb') as img_file:
            files = [('images', (images, img_file, content_type))]
            headers_form = {
                "Authorization": f"Bearer {self.api_key}"
            }
            response = requests.post(url, headers=headers_form, data=data, files=files)
            response.raise_for_status()
            return response.json()



# class _JThetaWrapper:
#     def __call__(self, api_key: str):
#         return JThetaClient(api_key)

# # This is what gets used when you `import jtheta`
# jtheta = _JThetaWrapper()