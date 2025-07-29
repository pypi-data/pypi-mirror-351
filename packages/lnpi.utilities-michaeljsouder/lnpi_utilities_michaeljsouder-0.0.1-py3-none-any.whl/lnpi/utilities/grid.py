import io, json, os, requests, string, zipfile

from datetime import datetime

class Grid:
    def __init__(self, api_token, population_id):
        self.base_url = f"https://lnpiapp.med.umn.edu/api/grid/studies/{population_id}"
        self.api_token = api_token
        self.headers = {
            "Authorization" : self.api_token 
        }
        self.population_id = population_id

    def _get_event_template(self, 
                            subject_id: int, 
                            procedure_id: int, 
                            event_start: datetime, 
                            event_end: datetime,
                            event_status: int,
                            event_quality: int,
                            note: str) -> object:
        """
        Parameters
        ----------
        subject_id : int
            The Grid subject id.
        procedure_id : int
            The Grid procedure id that corresponds to this event.
        event_start : datetime
            The start datetime of the event.
        event_end : datetime
            The end datetime of the event.
        event_status: int
            The id of the corresponding event status type.
        event_quality: int
            This corresponds to the event quality.
        note: str
            Any additional details or description of event.
        """
        return {
            "study_id": self.population_id,
            "subject_id": subject_id,
            "procedure_id": procedure_id,
            "event_start_time": event_start,
            "event_end_time": event_end,
            "event_status": event_status,
            "event_quality": event_quality,
            "event_note": note,
            "key_person": "API Client",
            "ignore": None,
            "created_by": "API Client",
            "updated_by": None,
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
            "lock_version": 0
        }

    def _get_subject_template(self,
                              contact_id: int,
                              first_name: str,
                              last_name: str,
                              birthdate: datetime,
                              sex: int,
                              ssn: int,
                              medical_record_number: str,
                              research_status: str,
                              race_id: int,
                              ethnicity_id: int,
                              note: str) -> object:
        """
            Parameters
            ----------
            contact_id : int
                The corresponding Grid contact id.
            first_name : str
                The first name of the subject.
            last_name : str
                The last name of the subject.
            birthdate : datetime
                The datetime representing the subject's birthdate. 
            sex: int
                This is the id the corresponds to the correct sex in the Grid system.
            ssn: int
                This is the social security number for the subject.
            medical_record_number: str
                This is the medical record number for this subject.
            research_status: str
            race_id: int
                This is the id that corresponds to the correct race in the Grid system.
            ethnicity_id: int
                This is the id that corresponds to the correct ethnicity in the Grid system.
            note: str
                This contains any notable information about this subject.
        """
        return {
            "contact_id": None,
            "first_name": first_name,
            "last_name": last_name,
            "date_of_birth": birthdate,
            "sex": sex,
            "ssn": ssn,
            "medical_record_number": medical_record_number,
            "research_status": research_status,
            "race_id": race_id,
            "ethnicity_id": ethnicity_id,
            "note": note,
            "created_by": "Python API Client",
            "updated_by": "Python API Client",
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
            "lock_version": 0
        }
    
    def _get_subject_study_template(self,
                                    subject_id: int,
                                    note: str,
                                    study_of_origin: str,
                                    study_entry_date: datetime,
                                    participant_status: int,
                                    group_id: int):
        """
            Parameters
            ----------
            subject_id : int
                The corresponding Grid subject id.
            note : str
                The corresponding note about when subject was added to study.
            study_of_origin: str
                Study that particpant came from if any.
            study_entry_date: datetime
                Datetime of when participant joined study.
            participant_status: int
                The id that corresponds to the correct status record indicating current state.
            groupd_id: int
                Id for the group the participant belongs to.
        """
        return {
            "subject_id": subject_id,
            "study_id": self.population_id,
            "note": note,
            "study_of_origin": study_of_origin,
            "study_entry_date": study_entry_date,
            "participant_status": participant_status,
            "group_id": group_id,
            "created_by": "Python API Client",
            "updated_by": "Python API Client",
            "created_at": str(datetime.now()),
            "updated_at": str(datetime.now()),
            "lock version": 0
        }


    def event_get(self, id: int) -> object:
        request = requests.get(f"{self.base_url}/events/{id}", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def event_get_all(self) -> [object]:
        request = requests.get(f"{self.base_url}/events/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def event_create(self, data: object) -> object:
        request = requests.post(f"{self.base_url}/events/", headers=self.headers, data=data)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def event_details_get(self, event_id: int, id: int) -> object:
        request = requests.get(f"{self.base_url}/events/{event_id}/details/{id}", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def event_details_get_all(self, event_id: int) -> list[object]:
        request = requests.get(f"{self.base_url}/events/{event_id}/details/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def event_details_create(self, event_id: int, data: object) -> object:
        request = requests.post(f"{self.base_url}/events/{event_id}/details/", headers=self.headers, data=data)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_get(self, id: int) -> object:
        request = requests.get(f"{self.base_url}/subjects/{id}/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_get_all(self) -> list[object]:
        request = requests.get(f"{self.base_url}/subjects/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_create(self, data: object) -> object:
        request = requests.post(f"{self.base_url}/subjects/", data=data, headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_study_get(self, id: int) -> object:
        request = requests.get(f"{self.base_url}/subjectstudies/{id}/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_study_get_all(self) -> list[object]:
        request = requests.get(f"{self.base_url}/subjectstudies/", headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")

    def subject_study_create(self, data:object) -> object:
        request = requests.post(f"{self.base_url}/subjectstudies/", data=data, headers=self.headers)

        try:
            return request.json()
        except:
            print("Error: Could not decode JSON.")
