import os, gzip, bz2, json
from typing import Dict, List, Literal, Union
from azure.storage.blob import BlobServiceClient
from tqdm import tqdm

class AzureBlobStorage:

    def __init__(
            self, 
            account_name: str, 
            account_key: str,
            container_name: str
    ):

        self.account_name = account_name
        self.account_key = account_key

        self.blob_service_client = BlobServiceClient(
            account_url=f"https://{self.account_name}.blob.core.windows.net",
            credential=self.account_key
        )

        self.container_client = self.blob_service_client.get_container_client(container_name)

    def read_file(self, file_path: str) -> bytes:

        blob_client = self.container_client.get_blob_client(file_path)
        blob_data = blob_client.download_blob()
        return blob_data.readall()

    def read_compressed_json_file(
            self,
            file_path: str,
            compression: Literal["gzip", "bz2"] = "gzip"
    ) -> Union[Dict, List]:
        
        data = self.read_file(file_path)

        # Decompress the JSON data
        if compression == "gzip":
            decompressed_data = gzip.decompress(data)
        elif compression == "bz2":
            decompressed_data = bz2.decompress(data)
        else:
            raise ValueError("Unsupported compression type. Use 'gzip' or 'bz2'.")

        json_data = json.loads(decompressed_data.decode("utf-8"))

        return json_data

    def download_file_to_path(
            self, 
            remote_file_path: str, 
            local_file_path: str
    ):
        """
        Downloads a file from Azure Blob Storage to a local path.
        """
        blob_client = self.container_client.get_blob_client(remote_file_path)
        with open(local_file_path, "wb") as local_file:
            blob_data = blob_client.download_blob()
            blob_data.readinto(local_file)
            
    def import_remote_directory(
        self, 
        remote_directory_path: str,
        target_directory_path: str
    ):
        
        if not remote_directory_path.endswith("/"):
            remote_directory_path += "/"

        # Ensure target_directory_path exists
        os.makedirs(target_directory_path, exist_ok=True)

        # All blobs
        blobs = self.container_client.list_blobs(name_starts_with=remote_directory_path)
        blobs = list(blobs)

        # First the .json file 
        mp4_blobs = next((blob for blob in blobs if blob.name.endswith(".mp4")), None)
        remaining_blobs = [blob for blob in blobs if not blob.name.endswith(".mp4")]

        # Download the .mp4 file last 
        blobs = remaining_blobs + ([mp4_blobs] if mp4_blobs else [])
        for blob in tqdm(blobs, desc="Downloading dataset", unit="file"):

            # Construct the local file path
            relative_path = blob.name[len(remote_directory_path):] if remote_directory_path else blob.name
            if relative_path.startswith("/"): 
                relative_path = relative_path[1:]
            local_file_path = os.path.join(target_directory_path, relative_path)

             # Check if the file already exists
            if os.path.exists(local_file_path):
                continue

            # Ensure the directory exists + download
            os.makedirs(os.path.dirname(local_file_path), exist_ok=True)
            self.download_file_to_path(blob.name, local_file_path)

        