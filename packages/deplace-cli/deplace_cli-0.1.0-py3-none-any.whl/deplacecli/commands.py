from deplacecli.storage import AzureBlobStorage

class Command:

    @staticmethod
    def download(
        token: str,
        file_path: str,
    ):
        
        dataset_storage = AzureBlobStorage(
            account_name="deplacestorage",
            account_key=token,
            container_name="datasets"
        )

        dataset_storage.import_remote_directory(
            remote_directory_path="v1",
            target_directory_path="file_path"
        )

        