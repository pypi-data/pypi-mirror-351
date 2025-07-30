# PYAWS_S3

## Description

`S3Client` is a Python class that simplifies interaction with AWS S3 for uploading, downloading, managing, and deleting files. It supports uploading images, DataFrames, PDFs, generating pre-signed URLs, downloading files, listing files, and deleting individual files.

## Installation

Make sure you have installed:

```bash
pip install pyaws_s3
```

### Env Variables

Make sure to add these environment variables:

```bash
AWS_ACCESS_KEY_ID=<Your Access Key Id>
AWS_SECRET_ACCESS_KEY=<Your Secret Access Key>
AWS_REGION=<Your Region>
AWS_BUCKET_NAME=<Your Bucket Name>
```

## Usage

### Initialization

You can initialize the class by passing AWS credentials as parameters or via environment variables:

```python
from s3_client import S3Client

s3 = S3Client(
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("AWS_REGION"),
    bucket_name=os.getenv("AWS_BUCKET_NAME")
)
```

### Main Methods

#### 1. `upload_image(fig, object_name, format_file=Literal["png", "jpeg", "svg", "html"])`

Uploads a figure (e.g., Matplotlib or Plotly) to S3 as an image (svg, png, jpeg, html).

```python
url = s3.upload_image(fig, "folder/image.svg", format_file="svg")
```

#### 2. `upload_from_dataframe(df, object_name, format_file=Literal["xlsx", "csv", "pdf"])`

Uploads a DataFrame to S3 as an Excel, CSV, or PDF file.

```python
url = s3.upload_from_dataframe(df, "folder/data", format_file="csv")
```

#### 3. `upload_to_pdf(text, object_name)`

Exports text to PDF and uploads it to S3.

```python
url = s3.upload_to_pdf("Text to export", "folder/file.pdf")
```

#### 4. `await delete_all(filter=None)`

Deletes all files from the bucket, optionally filtering by name.

```python
import asyncio
await s3.delete_all(filter="your_filter")
```

#### 5. `download(object_name, local_path=None, stream=False)`

Downloads a file from the S3 bucket.

- `object_name` (str): The name of the S3 object to download.
- `local_path` (str, optional): Local path to save the downloaded file. Required if `stream` is False.
- `stream` (bool, optional): If True, returns the file content as bytes instead of saving locally.

**Examples:**

Download and save locally:

```python
local_path = s3.download("folder/image.svg", local_path="downloads/")
```

Download as bytes (stream):

```python
file_bytes = s3.download("folder/image.svg", stream=True)
```

#### 6. `list_files(filter=None) -> list[str]`

Lists all files in the S3 bucket, optionally filtered by a substring.

- `filter` (str, optional): Only files containing this substring will be listed.

**Example:**

```python
files = s3.list_files(filter="folder/")
```

#### 7. `delete_file(object_name)`

Deletes a single file from the S3 bucket.

- `object_name` (str): The name of the S3 object to delete.

**Example:**

```python
s3.delete_file("folder/image.svg")
```

## Notes

- All upload methods return a pre-signed URL for downloading the file.
- Integrated error handling with logging.
- For uploading images and DataFrames, utility functions are required (`bytes_from_figure`, `html_from_figure`).

## Complete Example

```python
import matplotlib.pyplot as plt
import pandas as pd

fig, ax = plt.subplots()
ax.plot([1, 2, 3], [4, 5, 6])

df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})

s3 = S3Client(bucket_name="my-bucket")
img_url = s3.upload_image(fig, "test.svg")
df_url = s3.upload_from_dataframe(df, "mydata")
pdf_url = s3.upload_to_pdf("Hello PDF", "hello.pdf")

# Download a file
local_path = s3.download("test.svg", local_path="downloads/test.svg")

# List files
files = s3.list_files()

# Delete a file
s3.delete_file("test.svg")
```
