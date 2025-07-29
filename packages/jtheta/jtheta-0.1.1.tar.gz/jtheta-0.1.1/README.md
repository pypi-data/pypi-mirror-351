<!-- # jtheta

SDK for accessing the jtheta.ai API.

## Installation

```bash
pip install jtheta -->
## SDK for accessing the jtheta.ai API.






# 🧠 jtheta

SDK for accessing the [jtheta.ai](https://jtheta.ai) API — making it easy to manage datasets, request annotations, and automate your AI pipeline.

[![PyPI version](https://img.shields.io/pypi/v/jtheta.svg)](https://pypi.org/project/jtheta/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python Versions](https://img.shields.io/pypi/pyversions/jtheta.svg)](https://pypi.org/project/jtheta/)

## 📆 Installation

Install the SDK with pip:

```bash
pip install jtheta
```

---
## 🚀 Getting Started
```bash
Step 1: Login into https://app.jtheta.ai/ & Create the workspace.

Step 2: On Workspace dashboard click the Crete API key option in left sidebar.

Step 3: Copy the api key 
```


```python
import jtheta

# Initialize with your API key
jtheta.init("your_api_key_here")

# Validate your API key
print(jtheta.validate_key())

# Create a new project
#jtheta.create_project("project_title","project_category")
project = jtheta.create_project("My Project", "image")

# Upload images and create a dataset
#jtheta.create_dataset("dataset_name","license","project_name","image_paths"=["image path"])
dataset = jtheta.create_dataset("MyDataset", "MIT", "My Project", ["image1.jpg", "image2.jpg"])

#Upload more images
#jtheta.upload_images("dataset_id","project_name","images"="image1.jpg")
upload_image = jtheta.upload_images(231,"My Project","image1.jpg")

# Get list of Annotators
jtheta.get_annotators()

# Get list of Reviewers
jtheta.get_reviewers()

# Request annotation
#jtheta.request_annotation("dataset_id","project_name","assigned_annotator","assigned_reviewer","labels"=[{"label": class_label, "type": "Bounding Boxes"},{"label": class_label, "type": "Polygons"},{"label": class_label, "type": "Instance Segmentation"},{"label": class_label, "type": "Semantic Segmentation"}],allow_class_creation=True,auto_annotation=True)

jtheta.request_annotation("My Project", dataset["id"], "annotator@example.com", "reviewer@example.com", [{"label": "car", "type": "Bounding Boxes"},{"label": "truck", "type": "Polygons"}], True, False)

# Download dataset
jtheta.download_dataset(dataset["id"], format="csv", version="1.0", save_path="annotations.csv")
```

---

## 📚 Features

* ✅ Project and dataset creation
* 📄 Image upload
* 🔍 Annotation request and monitoring
* ⬇️ Dataset export
* 🢑 Retrieve annotators and reviewers

---

<!-- ## 🛠️ Developer Guide

If you're contributing to this SDK, clone and install locally:

```bash
git clone https://github.com/yourusername/jtheta-sdk.git
cd jtheta-sdk
pip install -e .
``` -->

<!-- --- -->

## 📬 Support & Feedback

Have questions or feature requests? Reach out!

📧 Email: [contact@jtheta.ai](mailto:contact@jtheta.ai)
🌐 Website: [jtheta.ai](https://jtheta.ai)

---

## 🌐 Connect with us

[![Website](https://img.shields.io/badge/Website-jtheta.ai-4E73DF?logo=google-chrome\&logoColor=white)](https://jtheta.ai)
[![YouTube](https://img.shields.io/badge/YouTube-Channel-red?logo=youtube)](https://www.youtube.com/@JThetaAi)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Follow-blue?logo=linkedin)](https://www.linkedin.com/company/jtheta-ai/)
[![Facebook](https://img.shields.io/badge/Facebook-Page-3b5998?logo=facebook\&logoColor=white)](https://facebook.com/jthetaAI)

<!-- ---
## 🌐 Connect with us

[![Website](https://img.shields.io/badge/-4E73DF?logo=google-chrome&logoColor=white&label=jtheta.ai)](https://jtheta.ai)
[![YouTube](https://img.shields.io/badge/-red?logo=youtube&logoColor=white&label=)](https://www.youtube.com/@JThetaAi))
[![LinkedIn](https://img.shields.io/badge/-blue?logo=linkedin&logoColor=white&label=)](https://linkedin.com/company/jtheta)
[![Facebook](https://img.shields.io/badge/-3b5998?logo=facebook&logoColor=white&label=)](https://facebook.com/jthetaAI) -->

## 📝 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
