import string

from boxsdk import Client, JWTAuth

class BoxClient:
    def __init__(self, settings_file_path: str):
        self.auth = JWTAuth.from_settings_file(settings_file_path)
        self.access_token = self.auth.authenticate_instance()
        self.client = Client(self.auth)

    def create_folder(self, root_folder_id: str, new_folder_name: string):
        return self.client.folder(root_folder_id).create_subfolder(new_folder_name)

    def upload(self, folder_id: str, file_path: str, file_name: str):
        folder = self.client.folder(folder_id).get()
        return folder.upload(file_path, file_name)

    def cleanup_local_directory(dir_path: str):
        try:
            os.rmdir(dir_path)
            print(f"Directory '{dir_path}' deleted successfully.")
        except FileNotFoundError:
            print(f"Directory '{dir_path}' not found.")
        except OSError:
            print(f"Directory '{dir_path}' is not empty.")
