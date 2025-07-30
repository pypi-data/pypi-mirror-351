import base64
import enum
import hashlib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

import requests
from pydantic import BaseModel

from pyscicat.model import (
    Attachment,
    CreateDatasetOrigDatablockDto,
    Dataset,
    Instrument,
    Proposal,
    Sample,
)

logger = logging.getLogger("pyscicat")
can_debug = logger.isEnabledFor(logging.DEBUG)


class ScicatLoginError(Exception):
    """Represents an error encountered logging into SciCat"""

    def __init__(self, message):
        self.message = message


class ScicatCommError(Exception):
    """Represents an error encountered during communication with SciCat."""

    def __init__(self, message):
        self.message = message


class Severity(str, enum.Enum):
    warning = "warning"
    fatal = "fatal"


class ScicatClient:
    """Responsible for communicating with the Scicat Catamel server via http"""

    def __init__(
        self,
        base_url: str,
        token: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        timeout_seconds: Optional[int] = None,
        auto_login=True,
    ):
        """Initialize a new instance. This method attempts to create a token
        from the provided username and password

        Parameters
        ----------
        base_url : str
            Base url. e.g. `http://localhost:3000/api/v3`
        username : str
            username to login with
        password : str
            password to login with
        timeout_seconds : [int], optional
            timeout in seconds to wait for http connections to return, by default None
        """
        self._base_url = base_url
        self._timeout_seconds = (
            timeout_seconds  # we are hitting a transmission timeout...
        )
        self._username = username  # default username
        self._password = password  # default password
        self._token = token  # store token here
        self._headers = {}  # store headers

        if not self._token:
            assert (self._username is not None) and (
                self._password is not None
            ), "SciCat login credentials (username, password) must be provided if token is not provided"
            if auto_login:
                self.login()
        else:
            self._headers["Authorization"] = "Bearer {}".format(self._token)

    def _send_to_scicat(
        self, cmd: str, endpoint: str, data: Optional[BaseModel] = None
    ):
        """sends a command to the SciCat API server using url and token, returns the response JSON
        Get token with the getToken method"""
        endpoint_url = "/".join(s.strip("/") for s in [self._base_url, endpoint])
        return requests.request(
            method=cmd,
            url=endpoint_url,
            json=data.model_dump(exclude_none=True) if data is not None else None,
            params={"access_token": self._token},
            headers=self._headers,
            timeout=self._timeout_seconds,
            stream=False,
            verify=True,
        )

    def login(self):
        """Attempts to authenticate using the stored username and password.
        Does not check if authentication has already occured."""
        self._token = get_token(
            self._base_url, self._username, self._password, self._headers
        )
        self._headers["Authorization"] = "Bearer {}".format(self._token)

    def _call_endpoint(
        self,
        cmd: str,
        endpoint: str,
        data: Optional[BaseModel] = None,
        operation: str = "",
    ) -> Optional[dict]:
        response = self._send_to_scicat(cmd=cmd, endpoint=endpoint, data=data)

        result = response.json() if len(response.content) > 0 else None
        if not response.ok:
            raise ScicatCommError(f"Error in operation {operation}: {result}")

        logger.info(
            "Operation '%s' successful%s",
            operation,
            f"pid={result['pid']}" if result and "pid" in result else "",
        )
        return result

    def datasets_create(self, dataset: Dataset) -> str:
        """
        Upload a new dataset. Uses the generic dataset endpoint.
        Relies on the endpoint to sense the dataset type
        This function was renamed.
        It is still accessible with the original name for backward compatibility
        The original name were create_dataset and upload_new_dataset

        Parameters
        ----------
        dataset : Dataset
            Dataset to create

        Returns
        -------
        str
            pid of the dataset

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        result = self._call_endpoint(
            cmd="post", endpoint="Datasets", data=dataset, operation="datasets_create"
        )
        assert result and "pid" in result and isinstance(result["pid"], str)
        return result["pid"]

    """
        Upload a new dataset
        Original name, kept for for backward compatibility
    """
    upload_new_dataset = datasets_create
    create_dataset = datasets_create

    def datasets_update(self, dataset: Dataset, pid: str) -> str:
        """Updates an existing dataset
        This function was renamed.
        It is still accessible with the original name for backward compatibility
        The original name was update_dataset.

        Parameters
        ----------
        dataset : Dataset
            Dataset to update

        pid
            pid (or unique identifier) of dataset being updated

        Returns
        -------
        str
            pid (or unique identifier) of the dataset
        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        result = self._call_endpoint(
            cmd="patch",
            endpoint=f"Datasets/{quote_plus(pid)}",
            data=dataset,
            operation="datasets_update",
        )
        assert result and "pid" in result and isinstance(result["pid"], str)
        return result["pid"]

    """
        Update a dataset
        Original name, kept for for backward compatibility
    """
    update_dataset = datasets_update

    def datasets_origdatablock_create(
        self, dataset_id: str, datablockDto: CreateDatasetOrigDatablockDto
    ) -> dict:
        """
        Create a new SciCat Dataset OrigDatablock
        This function has been renamed.
        It is still accessible with the original name for backward compatibility
        The original names were create_dataset_origdatablock and upload_dataset_origdatablock

        Parameters
        ----------
        origdatablock :
            The OrigDatablock to create

        Returns
        -------
        dict
            The created OrigDatablock with id

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned

        """
        endpoint = f"Datasets/{quote_plus(dataset_id)}/origdatablocks"
        result = self._call_endpoint(
            cmd="post",
            endpoint=endpoint,
            data=datablockDto,
            operation="datasets_origdatablock_create",
        )
        assert isinstance(result, dict)
        return result

    """
        Create a new SciCat Dataset OrigDatablock
        Original name, kept for for backward compatibility
    """
    upload_dataset_origdatablock = datasets_origdatablock_create
    create_dataset_origdatablock = datasets_origdatablock_create

    def datasets_attachment_create(
        self, attachment: Attachment, datasetType: str = "Datasets"
    ) -> dict:
        """
        Create a new Attachment for a dataset.
        Note that datasetType can be provided to determine the type of dataset
        that this attachment is attached to. This is required for creating the url that SciCat uses.
        This function has been renamed.
        It is still accessible with the original name for backward compatibility
        The original names were create_dataset_attachment and upload_attachment

        Parameters
        ----------
        attachment : Attachment
            Attachment to upload

        datasetType : str
            Type of dataset to upload to, default is `RawDatasets`
        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        endpoint = f"{datasetType}/{quote_plus(attachment.datasetId)}/attachments"
        result = self._call_endpoint(
            cmd="post",
            endpoint=endpoint,
            data=attachment,
            operation="datasets_attachment_create",
        )
        assert isinstance(result, dict)
        return result

    """
        Create a new attachement for a dataset
        Original name, kept for for backward compatibility
    """
    upload_attachment = datasets_attachment_create
    create_dataset_attachment = datasets_attachment_create

    def samples_create(self, sample: Sample) -> str:
        """
        Create a new sample.
        An error is raised when a sample with the same sampleId already exists.
        This function is also accessible as upload_sample.


        Parameters
        ----------
        sample : Sample
            Sample to upload

        Returns
        -------
        str
            ID of the newly created sample

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        result = self._call_endpoint(
            cmd="post",
            endpoint="Samples",
            data=sample,
            operation="samples_create",
        )
        assert result and "sampleId" in result and isinstance(result["sampleId"], str)
        return result["sampleId"]

    upload_sample = samples_create

    def samples_update(self, sample: Sample, sampleId: Optional[str] = None) -> str:
        """Updates an existing sample

        Parameters
        ----------
        sample : Sample
            Sample to update

        sampleId
            ID of sample being updated. By default, ID is taken from sample parameter.

        Returns
        -------
        str
            ID of the sample

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned

        AssertionError
            Raises if no ID is provided
        """
        if sampleId is None:
            assert sample.sampleId is not None, "sampleId should not be None"
            sampleId = sample.sampleId
        sample.sampleId = None
        result = self._call_endpoint(
            cmd="patch",
            endpoint=f"Samples/{quote_plus(sampleId)}",
            data=sample,
            operation="samples_update",
        )
        assert result and "sampleId" in result and isinstance(result["sampleId"], str)
        return result["sampleId"]

    def instruments_create(self, instrument: Instrument):
        """
        Create a new instrument.
        Note that in SciCat admin rights are required to upload instruments.
        An error is raised when an instrument with the same pid already exists.
        This function is also accessible as upload_instrument.


        Parameters
        ----------
        instrument : Instrument
            Instrument to upload

        Returns
        -------
        str
            pid (or unique identifier) of the newly created instrument

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        result = self._call_endpoint(
            cmd="post",
            endpoint="Instruments",
            data=instrument,
            operation="instruments_create",
        )
        assert result and "pid" in result and isinstance(result["pid"], str)
        return result["pid"]

    upload_instrument = instruments_create

    def instruments_update(
        self, instrument: Instrument, pid: Optional[str] = None
    ) -> str:
        """Updates an existing instrument.
        Note that in SciCat admin rights are required to upload instruments.

        Parameters
        ----------
        instrument : Instrument
            Instrument to update

        pid
            pid (or unique identifier) of instrument being updated.
            By default, pid is taken from instrument parameter.

        Returns
        -------
        str
            ID of the instrument

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned

        AssertionError
            Raises if no ID is provided
        """
        if pid is None:
            assert instrument.pid is not None, "pid should not be None"
            pid = instrument.pid
        instrument.pid = None
        result = self._call_endpoint(
            cmd="patch",
            endpoint=f"Instruments/{quote_plus(pid)}",
            data=instrument,
            operation="instruments_update",
        )
        assert result and "pid" in result and isinstance(result["pid"], str)
        return result["pid"]

    def proposals_create(self, proposal: Proposal):
        """
        Create a new proposal.
        Note that in SciCat admin rights are required to upload proposals.
        An error is raised when a proposal with the same proposalId already exists.
        This function is also accessible as upload_proposal.


        Parameters
        ----------
        proposal : Proposal
            Proposal to upload

        Returns
        -------
        str
            ID of the newly created proposal

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned
        """
        result = self._call_endpoint(
            cmd="post",
            endpoint="Proposals",
            data=proposal,
            operation="proposals_create",
        )
        assert (
            result and "proposalId" in result and isinstance(result["proposalId"], str)
        )
        return result["proposalId"]

    upload_proposal = proposals_create

    def proposals_update(
        self, proposal: Proposal, proposalId: Optional[str] = None
    ) -> str:
        """Updates an existing proposal.
        Note that in SciCat admin rights are required to upload proposals.

        Parameters
        ----------
        proposal : Proposal
            Proposal to update

        proposalId
            ID of proposal being updated. By default, this is taken from proposal parameter.

        Returns
        -------
        str
            ID of the proposal

        Raises
        ------
        ScicatCommError
            Raises if a non-20x message is returned

        AssertionError
            Raises if no ID is provided
        """
        if proposalId is None:
            assert proposal.proposalId is not None, "proposalId should not be None"
            proposalId = proposal.proposalId
        # TODO updates should allow partial proposals, where all fields are optional. See #58
        proposal.proposalId = None  # type: ignore [assignment]
        result = self._call_endpoint(
            cmd="patch",
            endpoint=f"Proposals/{quote_plus(proposalId)}",
            data=proposal,
            operation="proposals_update",
        )
        assert (
            result and "proposalId" in result and isinstance(result["proposalId"], str)
        )
        return result["proposalId"]

    def datasets_find(
        self, skip: int = 0, limit: int = 25, query_fields: Optional[dict] = None
    ) -> Optional[dict]:
        """
        Gets datasets using the fullQuery mechanism of SciCat. This is
        appropriate for cases where might want paging and cases where you want to perform
        a text search on the Datasets collection. The full features of fullQuery search
        are beyond this document.

        There is no known mechanism to query for fields that are missing or contain a
        a null value.

        To query based on the full text search, send `{"text": "<text to query"}` as query field

        This function was renamed.
        It is still accessible with the original name for backward compatibility
        The original name was find_datasets_full_query and get_datasets_full_query

        Parameters
        ----------
        skip : int
            number of items to skip

        limit : int
            number of items to return

        query_fields : dict
            dictionary of terms to send to the query (must be json serializable)

        """
        if not query_fields:
            query_fields = {}
        query_field_str = json.dumps(query_fields)
        query = f'fields={query_field_str}&limits={{"skip":{skip},"limit":{limit},"order":"creationTime:desc"}}'

        return self._call_endpoint(
            cmd="get",
            endpoint=f"Datasets/fullquery?{query}",
            operation="datasets_find",
        )

    """
        find a set of datasets according the full query provided
        Original name, kept for for backward compatibility
    """
    get_datasets_full_query = datasets_find
    find_datasets_full_query = datasets_find

    def datasets_get_many(self, filter_fields: Optional[dict] = None) -> Optional[dict]:
        """
        Gets datasets using the simple filter mechanism. This
        is appropriate when you do not require paging or text search, but
        want to be able to limit results based on items in the Dataset object.
        This function has been renamed and the old name has been mantained for backward compatibility
        The previous names are find_datasets and get_datasets

        For example, a search for Datasets of a given proposalId would have
        ```python
        filterField = {"proposalId": "1234"}
        ```
        A search for Datasets  with no proposalId would be:
        ```python
        filterField = {"proposalId": ""}
        ```
        If you want to search on partial strings, you can use "like":
        ```python
        filterField = {"proposalId": {"like":"123"}}
        ```

        Parameters
        ----------
        filter_fields : dict
            Dictionary of filtering fields. Must be json serializable.
        """
        if filter_fields is None:
            filter_fields = {}
        filter_field_str = json.dumps(filter_fields)
        endpoint = f'Datasets?filter={{"where":{filter_field_str}}}'
        return self._call_endpoint(
            cmd="get", endpoint=endpoint, operation="datasets_get_many"
        )

    """
        find a set of datasets according to the simple filter provided
        Original name, kept for for backward compatibility
    """
    get_datasets = datasets_get_many
    find_datasets = datasets_get_many

    def samples_get_many(self, filter_fields: Optional[dict] = None) -> Optional[dict]:
        """
        Gets samples using the simple filter mechanism. This
        is appropriate when you do not require paging or text search, but
        want to be able to limit results based on items in the Sample object.

        For example, a search for Samples of a given ownerGroup would have
        ```python
        filterField = {"ownerGroup": "1234"}
        ```
        If you want to search on partial strings, you can use "like":
        ```python
        filterField = {"ownerGroup": {"like":"123"}}
        ```
        To search within the JSON metadata, join sub-fields with ".":
        ```python
        filterField = {"sampleCharacteristics.myCustomObject.myField": "1234"}
        ```

        Parameters
        ----------
        filter_fields : dict
            Dictionary of filtering fields. Must be json serializable.
        """
        if filter_fields is None:
            filter_fields = {}
        filter_field_str = json.dumps(filter_fields)
        endpoint = f'Samples?filter={{"where":{filter_field_str}}}'
        return self._call_endpoint(
            cmd="get", endpoint=endpoint, operation="samples_get_many"
        )

    def published_data_get_many(self, filter=None) -> Optional[dict]:
        """
        retrieve all the published data using the simple filter mechanism. This
        is appropriate when you do not require paging or text search, but
        want to be able to limit results based on items in the Dataset object.
        This function has been renamed and the old name has been maintained for backward compatibility
        The previous name are find_published_data and get_published_data

        For example, a search for published data of a given doi would have
        ```python
        filter = {"doi": "1234"}
        ```

        Parameters
        ----------
        filter : dict
            Dictionary of filtering fields. Must be json serializable.
        """
        if filter:
            filter = json.dumps(filter)

        endpoint = "PublishedData" + (f'?filter={{"where":{filter}}}' if filter else "")
        return self._call_endpoint(
            cmd="get",
            endpoint=endpoint,
            operation="published_data_get_many",
        )

    """
        find a set of published data according to the simple filter provided
        Original name, kept for for backward compatibility
    """
    get_published_data = published_data_get_many
    find_published_data = published_data_get_many

    def datasets_get_one(self, pid: str) -> Optional[dict]:
        """
        Gets dataset with the pid provided.
        This function has been renamed. Provious name has been maintained for backward compatibility.
        Previous names was get_dataset_by_pid

        Parameters
        ----------
        pid : string
            pid of the dataset requested.
        """
        return self._call_endpoint(
            cmd="get",
            endpoint=f"Datasets/{quote_plus(pid)}",
            operation="datasets_get_one",
        )

    get_dataset_by_pid = datasets_get_one

    def instruments_get_one(
        self, pid: Optional[str] = None, name: Optional[str] = None
    ) -> Optional[dict]:
        """
        Get an instrument by pid or by name.
        If pid is provided it takes priority over name.

        This function has been renamed. Previous name has been maintained for backward compatibility.
        Previous name was get_instrument

        Parameters
        ----------
        pid : str
            Pid of the instrument

        name : str
            The name of the instrument

        Returns
        -------
        dict
            The instrument with the requested name
        """

        if pid:
            endpoint = f"Instruments/{quote_plus(pid)}"
        elif name:
            query = json.dumps({"where": {"name": {"like": name}}})
            endpoint = f"Instruments/findOne?{query}"
        else:
            raise ValueError("You must specify instrument pid or name")

        return self._call_endpoint(
            cmd="get",
            endpoint=endpoint,
            operation="instruments_get_one",
        )

    get_instrument = instruments_get_one

    def samples_get_one(self, pid: str) -> Optional[dict]:
        """
        Get a sample by pid.
        This function has been renamed. Previous name has been maintained for backward compatibility.
        Previous name was get_sample


        Parameters
        ----------
        pid : str
            The pid of the sample

        Returns
        -------
        dict
            The sample with the requested pid
        """
        return self._call_endpoint(
            cmd="get",
            endpoint=f"Samples/{quote_plus(pid)}",
            operation="samples_get_one",
        )

    get_sample = samples_get_one

    def proposals_get_one(self, pid: str) -> Optional[dict]:
        """
        Get proposal by pid.
        This function has been renamed. Previous name has been maintained for backward compatibility.
        Previous name was get_proposal

        Parameters
        ----------
        pid : str
            The pid of the proposal

        Returns
        -------
        dict
            The proposal with the requested pid
        """
        return self._call_endpoint(cmd="get", endpoint=f"Proposals/{quote_plus(pid)}")

    get_proposal = proposals_get_one

    def datasets_origdatablocks_get_one(self, pid: str) -> Optional[dict]:
        """
        Get dataset orig datablocks by dataset pid.
        This function has been renamed. Previous name has been maintained for backward compatibility.
        Previous name was get_dataset_origdatablocks

        Parameters
        ----------
        pid : str
            The pid of the dataset

        Returns
        -------
        dict
            The orig_datablocks of the dataset with the requested pid
        """
        return self._call_endpoint(
            cmd="get",
            endpoint=f"Datasets/{quote_plus(pid)}/origdatablocks",
            operation="datasets_origdatablocks_get_one",
        )

    get_dataset_origdatablocks = datasets_origdatablocks_get_one

    def datasets_delete(self, pid: str) -> Optional[dict]:
        """
        Delete dataset by pid
        This function has been renamed. Previous name has been maintained for backward compatibility.
        Previous name was delete_dataset

        Parameters
        ----------
        pid : str
            The pid of the dataset to be deleted

        Returns
        -------
        dict
            response from SciCat backend
        """
        return self._call_endpoint(
            cmd="delete",
            endpoint=f"Datasets/{quote_plus(pid)}",
            operation="datasets_delete",
        )

    delete_dataset = datasets_delete


def get_file_size(pathobj: Path):
    filesize = pathobj.lstat().st_size
    return filesize


def get_checksum(pathobj: Path):
    with open(pathobj, "rb") as file_to_check:
        # pipe contents of the file through
        return hashlib.md5(file_to_check.read()).hexdigest()


def encode_thumbnail(filename, imType="jpg"):
    logger.info(f"Creating thumbnail for dataset: {filename}")
    header = "data:image/{imType};base64,".format(imType=imType)
    with open(filename, "rb") as f:
        data = f.read()
    dataBytes = base64.b64encode(data)
    dataStr = dataBytes.decode("UTF-8")
    return header + dataStr


def get_file_mod_time(pathobj: Path):
    # may only work on WindowsPath objects...
    # timestamp = pathobj.lstat().st_mtime
    return str(datetime.fromtimestamp(pathobj.lstat().st_mtime))


def from_token(base_url: str, token: str):
    return ScicatClient(base_url, token)


def from_credentials(base_url: str, username: str, password: str):
    token = get_token(base_url, username, password)
    return from_token(base_url, token)


def _log_in_via_users_login(base_url, username, password, headers={}):
    login_url = "/".join(s.strip("/") for s in [base_url, "auth/login"])
    response = requests.post(
        login_url,
        json={"username": username, "password": password},
        headers=headers,
        stream=False,
        verify=True,
    )
    if not response.ok:
        try:
            response_text = response.json()
        except json.decoder.JSONDecodeError:
            response_text = response.text
        logger.info(f" Failed to log in via endpoint Users/login: {response_text}")
    return response


def get_token(base_url, username, password, headers={}):
    """logs in using the provided username / password combination
    and receives token for further communication use"""
    # Users/login only works for functional accounts and auth/msad for regular users.
    # Try both and see what works. This is not nice but seems to be the only
    # feasible solution right now.
    logger.info(" Getting new token")

    response = _log_in_via_users_login(base_url, username, password, headers)
    if response.ok:
        return response.json()["id"]  # not sure if semantically correct

    try:
        response_text = response.json()
    except json.decoder.JSONDecodeError:
        response_text = response.text
    logger.error(f" Failed log in:  {response_text}")
    raise ScicatLoginError(response.content)


if __name__ == "__main__":
    import os

    client = from_credentials(
        os.getenv("SCICAT_URL"), os.getenv("SCICAT_USER"), os.getenv("SCICAT_PASSWORD")
    )
    print(client.datasets_find())
