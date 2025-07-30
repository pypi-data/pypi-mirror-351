import logging
import os
import boto3
import aioboto3
import pandas as pd
import io
import matplotlib.pyplot as plt
from plotly.graph_objs import Figure
from pandas.plotting import table
from typing import Any, Literal
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from io import BytesIO

logger = logging.getLogger(__name__)

FormatFile = Literal["png", "jpeg", "svg", "html", "xlsx", "csv", "pdf"]

class S3Client:
    """
    A class to interact with AWS S3 for uploading and managing files.
    """
    
    aws_access_key_id : str
    aws_secret_access_key : str
    region_name : str
    bucket_name : str

    def __init__(self, **kwargs: Any) -> None:
        """
        Initialize the S3Client with AWS credentials and region.

        Args:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str): AWS region name.
        """
        # aws_access_key_id: str, aws_secret_access_key: str, region_name: str
        self.aws_access_key_id = kwargs.get("aws_access_key_id", os.getenv("AWS_ACCESS_KEY_ID"))
        self.aws_secret_access_key = kwargs.get("aws_secret_access_key", os.getenv("AWS_SECRET_ACCESS_KEY"))
        self.region_name = kwargs.get("region_name", os.getenv("AWS_REGION"))
        self.bucket_name = kwargs.get("bucket_name", os.getenv("AWS_BUCKET_NAME"))

    def _bytes_from_figure(self, f: Figure, **kwargs) -> bytes:
        """
        Convert a Plotly Figure to a PNG image as bytes.

        Args:
            f (Figure): The Plotly Figure object to be converted.

        Returns:
            bytes: The PNG image data as bytes.
            :param f:  The Plotly Figure object to be converted into a PNG image.
        """

        format_file = kwargs.get("format_file", "png")  # The format of the image to be converted to
        width = kwargs.get("width", 640)  # The width of the image in pixels
        height = kwargs.get("height", 480)  # The height of the image in pixels

        with io.BytesIO() as bytes_buffer:
            f.write_image(bytes_buffer, 
                        format=format_file, 
                        width = width, 
                        height = height)  # Write the figure to the bytes buffer as a PNG image
            bytes_buffer.seek(0)  # Reset the buffer position to the beginning
            return bytes_buffer.getvalue()  # Return the bytes data

    def _html_from_figure(self, f: Figure) -> str:
        """
        Convert a Plotly Figure to an HTML string.

        Args:
            f (Figure): The Plotly Figure object to be converted.

        Returns:
            str: The HTML representation of the figure as a string.
        """
        with io.BytesIO() as bytes_buffer:
            # Wrap the BytesIO with a TextIOWrapper to handle strings
            with io.TextIOWrapper(bytes_buffer, encoding='utf-8') as text_buffer:
                f.write_html(text_buffer)  # Write the figure to the text buffer
                text_buffer.flush()  # Ensure all data is written
                bytes_buffer.seek(0)  # Reset the buffer position to the beginning
                return bytes_buffer.getvalue().decode('utf-8')  # Decode bytes to string and return

    async def _get_s3_client_async(self) -> Any:
        """
        Get an asynchronous S3 client using the provided AWS credentials and region.

        Args:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str): AWS region name.

        Returns:
            Any: Asynchronous S3 client object.
        """
        session = aioboto3.Session()
        return session.resource(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def _get_s3_client(self) -> Any:
        """
        Get an asynchronous S3 client using the provided AWS credentials and region.

        Args:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str): AWS region name.

        Returns:
            Any: Asynchronous S3 client object.
        """
        return boto3.client(
            's3',
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
            region_name=self.region_name
        )

    def _get_s3_resource(self) -> Any:
        """
        Get an S3 client using the provided AWS credentials and region.

        Args:
            aws_access_key_id (str): AWS access key ID.
            aws_secret_access_key (str): AWS secret access key.
            region_name (str): AWS region name.

        Returns:
            Any: S3 client object.

        Raises:
            Exception: If there is an error creating the S3 client.
        """
        try:

            return boto3.resource('s3',
                                aws_access_key_id=self.aws_access_key_id,
                                aws_secret_access_key=self.aws_secret_access_key,
                                region_name=self.region_name)
        except Exception as e:
            logger.error(f"Error getting S3 client: {str(e)}")
            raise Exception(f"Error getting S3 client: {str(e)}")

    def _create_url(self, s3_client, bucket_name: str, object_name: str) -> str:
        """
        Generate a pre-signed URL for an S3 object.

        Args:
            s3_client: The S3 client object.
            bucket_name (str): The name of the S3 bucket.
            object_name (str): The name of the S3 object.

        Returns:
            str: The pre-signed URL for the S3 object.
        """
        temp_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': bucket_name,
                'Key': object_name
            },
            ExpiresIn=900  # 15 minutes
        )

        logger.info(f"Pre-signed URL: {temp_url}")

        return temp_url

    def upload_image(self, *args, **kwargs: Any) -> str:
        """
        Upload a Plotly Figure as a PNG image to an S3 bucket and generate a pre-signed URL.

        Args:
            fig (Figure): The Plotly Figure object to upload.
            bucket_name (str): The name of the S3 bucket.
            object_name (str): The name of the S3 object.

        Keyword Args:
            format_file (str): Format of the image. Defaults to 'png'.

        Returns:
            str: Pre-signed URL for the uploaded image.

        Raises:
            Exception: If there is an error uploading the image.
        """
        try:
            
            if args:
                fig = args[0] if len(args) > 0 else None
                object_name = args[1] if len(args) > 1 else None
            else:
                fig = kwargs.get("fig", None) 
                object_name = kwargs.get("object_name", None)
            
            if fig is None:
                raise Exception("Figure is None")
            
            if object_name is None:
                raise Exception("Object name is None")

            format_file : FormatFile = kwargs.get("format_file", "svg")
            mimetypes = "image/svg+xml"
            
            if format_file not in ["png", "jpeg", "svg", "html"]:
                raise Exception("Invalid format_file provided. Supported formats are: png, jpeg, svg, html")
            if format_file == "png":
                mimetypes = "image/png"
            elif format_file == "jpeg":
                mimetypes = "image/jpeg"
            elif format_file == "svg":
                mimetypes = "image/svg+xml"
            elif format_file == "html":
                mimetypes = "text/html"
            else:
                raise Exception("Invalid MIME type provided")

            # Get S3 client and resource
            s3_client = self._get_s3_client()
            s3_resource = self._get_s3_resource()

            if format_file == "html":
                # Convert the figure to SVG
                file_text = self._html_from_figure(fig)
                # Upload the html text to s3
                s3_resource.Bucket(self.bucket_name).Object(object_name).put(Body=file_text, ContentType=mimetypes)
            else:
                # Convert the figure to bytes
                file_buffer = self._bytes_from_figure(fig, format_file=format_file)
                # Upload the image bytes to S3
                s3_resource.Bucket(self.bucket_name).Object(object_name).put(Body=file_buffer, ContentType=mimetypes)

            # Generate and return a pre-signed URL for the uploaded image
            return self._create_url(s3_client, self.bucket_name, object_name)

        except Exception as e:
            logger.error(f"Error uploading image: {str(e)}")
            raise Exception(f"Error uploading image: {str(e)}")

    def upload_from_dataframe(self, *args : Any, **kwargs: Any) -> str:
        """
        Upload a DataFrame as an Excel file to an S3 bucket and generate a pre-signed URL.

        Args:
            df (DataFrame): The DataFrame to upload.
            **kwargs (Any): Additional keyword arguments for AWS credentials, bucket name, and object name.
            Keyword Args:
                format_file (str): Format of the file. Defaults to 'xlsx'.
        
        Returns:
            str: Pre-signed URL for the uploaded file.

        Raises:
            Exception: If there is an error uploading the file.
        """
        try:

            if args:    
                # Get the DataFrame and object name from the arguments
                df = args[0] if len(args) > 0 else None
                object_name = args[1] if len(args) > 1 else None
            else:
                # Get the DataFrame and object name from the keyword arguments
                df = kwargs.get("df", None)
                object_name = kwargs.get("object_name", None)

            if df is None:
                raise Exception("Figure is None")
            
            if object_name is None:
                raise Exception("Object name is None")
            
            format_file : FormatFile = kwargs.get("format_file", "csv")

            if format_file not in ["xlsx", "csv", "pdf"]:
                raise Exception("Invalid format_file provided. Supported formats are: xlsx, csv, pdf")
            
            if format_file == "xlsx":
                mimetypes = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif format_file == "csv":
                mimetypes = "text/csv"
            elif format_file == "pdf":
                mimetypes = "application/pdf"
            else:
                raise Exception("Invalid MIME type provided")

            s3_client = self._get_s3_client()
            s3_resource = self._get_s3_resource()

            # Create a file buffer
            ext: str = ""
            with io.BytesIO() as file_buffer:
                if mimetypes == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet":
                    ext = "xlsx"
                    # Convert DataFrame to Excel
                    with pd.ExcelWriter(file_buffer, engine="openpyxl") as writer:
                        df.to_excel(writer, index=False)
                elif mimetypes == "text/csv":
                    ext = "csv"
                    # Convert DataFrame to CSV
                    df.to_csv(file_buffer, index=False)
                elif mimetypes == "application/pdf":
                    ext = "pdf"
                    # Convert DataFrame to PDF
                    fig, ax = plt.subplots(figsize=(12, 4))  # Set the size of the figure
                    ax.axis('tight')
                    ax.axis('off')
                    table(ax, df, loc='center', cellLoc='center', colWidths=[0.1] * len(df.columns))
                    plt.savefig(file_buffer, format='pdf')

                file_buffer.seek(0)
                # Append the file extension to the object name
                object_name = f"{object_name}.{ext}"
                # Upload the file to S3
                s3_resource.Bucket(self.bucket_name).Object(object_name).put(Body=file_buffer, ContentType=mimetypes)

            logger.info(f"Uploaded file to S3: {object_name}")

            return self._create_url(s3_client, self.bucket_name, object_name)
        except Exception as e:
            logger.error(f"Error uploading file: {str(e)}")
            raise Exception(f"Error uploading file: {str(e)}")

    async def delete_all(self, filter : str | None = None) -> None:
        """
        Delete all files from an S3 bucket.

        Args:
            filter (str | None): Optional filter to delete specific files. If None, all files will be deleted.
        Raises:
            Exception: If there is an error deleting the files.
        """
        try:
            s3_client = self._get_s3_client()

            # List all objects in the bucket
            objects = s3_client.list_objects_v2(Bucket=self.bucket_name)

            # Check if the bucket contains any objects
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    if filter in obj['Key']:
                        # Delete each object
                        s3_client.delete_object(Bucket=self.bucket_name, Key=obj['Key'])
                        print(f"Deleted {obj['Key']}")
        except Exception as e:
            logger.error(f"Error deleting files: {str(e)}")
            raise Exception(f"Error deleting files: {str(e)}")

    def upload_to_pdf(self, *args: Any, **kwargs: Any) -> str:
        """
        Export the given text as a PDF and upload it to the S3 bucket.

        Args:
            text (str): The text to write in the PDF.
            object_name (str): The name of the S3 object.
        Raises:
            Exception: If there is an error exporting the PDF.
        Returns:
            str: Pre-signed URL for the uploaded PDF.
        """
        try:
            if args:
                text = args[0] if len(args) > 0 else None
                object_name = args[1] if len(args) > 1 else None
            else:
                text = kwargs.get("text", None)
                object_name = kwargs.get("object_name", None)

            if text is None:
                raise Exception("Text is None")

            if object_name is None:
                raise Exception("Object name is None")

            mimetypes = "application/pdf"
            s3_client = self._get_s3_client()
            s3_resource = self._get_s3_resource()

            # Crea il PDF in memoria
            pdf_buffer = BytesIO()
            c = canvas.Canvas(pdf_buffer, pagesize=A4)
            width, height = A4
            c.setFont("Helvetica", 10)
            x_margin = 20 * mm
            y = height - 20 * mm

            for line in text.strip().split('\n'):
                line = line.strip()
                if y < 20 * mm:
                    c.showPage()
                    c.setFont("Helvetica", 10)
                    y = height - 20 * mm

                # Markdown-style header detection
                if line.startswith("### "):
                    c.setFont("Helvetica-Bold", 11)
                    line = line[4:]
                elif line.startswith("## "):
                    c.setFont("Helvetica-Bold", 12)
                    line = line[3:]
                elif line.startswith("# "):
                    c.setFont("Helvetica-Bold", 14)
                    line = line[2:]
                else:
                    c.setFont("Helvetica", 10)

                c.drawString(x_margin, y, line)
                y -= 12

            c.save()
            pdf_buffer.seek(0)

            # Upload su S3
            s3_resource.Bucket(self.bucket_name).Object(object_name).put(
                Body=pdf_buffer,
                ContentType=mimetypes
            )
            return self._create_url(s3_client, self.bucket_name, object_name)

        except Exception as e:
            logger.error(f"Error exporting PDF: {str(e)}")
            raise Exception(f"Error exporting PDF: {str(e)}")
        
    def download(self, *args : Any, **kwargs : Any):
        """
        Download a file from S3 bucket.

        Args:
            object_name (str): The name of the S3 object to download.
            **kwargs (Any): Additional keyword arguments for local path and stream.
                - local_path (str): Local path to save the downloaded file. If None, the file will be streamed.
                - stream (bool): If True, the file will be streamed instead of saved locally.
        Raises:
            Exception: If there is an error downloading the file.
        Returns:
            str: The local path of the downloaded file.
        """
        try:
            
            if args:
                object_name = args[0] if len(args) > 0 else None
            else:
                object_name = kwargs.get("object_name", None)
            
            if object_name is None:
                raise Exception("Object name is None")
            
            local_path = kwargs.get("local_path", None)
            stream = kwargs.get("stream", False)
            
            if not stream and local_path is None:
                raise Exception("Local path is None if stream is False")
            
            s3_client = self._get_s3_client()
            response = s3_client.download_file(self.bucket_name, object_name, local_path)
            
            if stream:
                return response['Body'].read()
            
            return local_path
        except Exception as e:
            logger.error(f"Error downloading file: {str(e)}")
            raise Exception(f"Error downloading file: {str(e)}")
        
    def list_files(self, *args: Any, **kwargs : Any) -> list[str]:
        """
        List all files in the S3 bucket.

        Args:
            filter (str | None): Optional filter to list specific files. If None, all files will be listed.
        Raises:
            Exception: If there is an error listing the files.
        Returns:
            list[str]: List of file names in the S3 bucket.
        """
        try:
            prefix = args[0] if args else None
            if prefix is None:
                prefix = kwargs.get("prefix", None) 
                
            if prefix is None:
                raise Exception("Prefix is None")    
                
            filter = kwargs.get("filter", None)
            
            s3_client = self._get_s3_client()
            objects = s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)

            # Check if the bucket contains any objects
            docs : list[str] = []
            if 'Contents' in objects:
                for obj in objects['Contents']:
                    if obj['Key']:
                        # Log the object key
                        if filter is not None:
                            if filter in obj['Key']:
                                logger.info(f"Object: {obj['Key']}")
                                docs.append(obj['Key'])
                        else:
                            docs.append(obj['Key'])
            return docs
        except Exception as e:
            logger.error(f"Error listing files: {str(e)}")
            raise Exception(f"Error listing files: {str(e)}")
        
    def delete_file(self, *args : Any) -> None: 
        """
        Delete a file from the S3 bucket.

        Args:
            object_name (str): The name of the S3 object to delete.
        Raises:
            Exception: If there is an error deleting the file.
        """
        try:
            object_name = args[0] if len(args) > 0 else None
            if object_name is None:
                raise Exception("Object name is None")
            
            s3_client = self._get_s3_client()
            s3_client.delete_object(Bucket=self.bucket_name, Key=object_name)
        except Exception as e:
            logger.error(f"Error deleting file: {str(e)}")
            raise Exception(f"Error deleting file: {str(e)}")
        

