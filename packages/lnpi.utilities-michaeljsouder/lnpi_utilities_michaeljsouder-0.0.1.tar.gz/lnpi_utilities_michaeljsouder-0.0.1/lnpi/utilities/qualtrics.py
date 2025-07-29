import io, json, requests, zipfile

from datetime import datetime

class Qualtrics:
    def __init__(self, api_token: str, survey_id: str, data_center: str, workspace_dir: str, video_dir: str):
        self.api_token = api_token
        self.survey_id = survey_id
        self.data_center = data_center 
        self.workspace_dir = workspace_dir
        self.video_dir = video_dir

    def check_new(self):
        return
    
    def download_media_file(self, response_id: int, file_id: int, label: str) -> bytes:
        url = f'https://{self.data_center}.qualtrics.com/API/v3/surveys/{self.survey_id}/responses/{response_id}/uploaded-files/{file_id}'

        headers = {
            'Accept': 'application/octet-stream, application/json',    
            'X-API-TOKEN': self.api_token
        }

        file_name = f'{self.survey_id}-{file_id}.mp4'

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            with open(f"./apps/tasks/workspace/{self.video_dir}/{file_name}", 'wb') as file:
                file.write(response.content)
            print(f'File {file_name} downloaded successfully')
            return response.content
        else:
            print(f'Failed to download file. Status code: {response.status_code} {response.text}')
            return None

    def download_survey_responses(self):
        request_progress = 0.0
        progress_status = "inProgress"
        base_url = f"https://{self.data_center}.qualtrics.com/API/v3/surveys/{self.survey_id}/export-responses/"

        headers = {
            "content-type": "application/json",
            "x-api-token": self.api_token,
        }

        ##
        # Request creation of export file.
        ##
        download_request_url = base_url
        download_request_payload = '{"format":"' + 'json' + '"}'
        download_request_response = requests.request("POST", download_request_url, data=download_request_payload, headers=headers)

        print(download_request_response.json())
        progress_id = download_request_response.json()["result"]["progressId"]

        ##
        # Check status of export and wait for processing.
        ## 
        while progress_status != "complete" and progress_status != "failed":
            requestCheckUrl = base_url + progress_id
            requestCheckResponse = requests.request("GET", requestCheckUrl, headers=headers)
            request_progress = requestCheckResponse.json()["result"]["percentComplete"]

            print("Download is " + str(request_progress) + " complete")

            progress_status = requestCheckResponse.json()["result"]["status"]

        if progress_status == "failed":
            raise Exception("Qualtrics export failed!")

        file_id = requestCheckResponse.json()["result"]["fileId"]

        ##
        # Download the export file.
        ##
        request_download_url = base_url + file_id + '/file'
        request_download = requests.request("GET", request_download_url, headers=headers, stream=True)

        ##
        # Unzip the file to folder containing Qualtrics downloads.
        ##
        zipfile.ZipFile(io.BytesIO(request_download.content)).extractall("./apps/tasks/workspace/qualtrics")
        print('Complete')

    def retrieve_videos_info(self, ids: list[str], file_name: str, download: bool = False) -> list[dict]:
        with open(file_name, 'r') as file:
            data = json.load(file)
        
        responses = data['responses']

        files_info = []

        for response in responses:
            file_info = {}
            for val in response["values"]:
                if val.startswith("QID") and val.endswith("FILE_ID"):
                    file_info["responseId"] = response["responseId"]
                    file_info[val] = response["values"][val]

                    ##
                    # Download video file.
                    ##
                    if download:
                        print(f"Downloading video file {response["values"][val]} for response {response["responseId"]}")
                        download_media_response = self.download_media_file(response["responseId"], response["values"][val]) 
                        print(download_media_response)    
                elif val in ids:
                    file_info[val] = response["values"][val]
                
            if file_info:
                files_info.append(file_info)

        print(files_info)
        return files_info    