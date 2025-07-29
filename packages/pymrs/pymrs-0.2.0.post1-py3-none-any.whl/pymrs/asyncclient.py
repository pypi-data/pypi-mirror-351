import httpx
import json
import logging
from pydantic import (
    ValidationError,
    BaseModel,
    Field,
    HttpUrl,
    TypeAdapter,
)
from .exceptions import MRSClientError
from json.decoder import JSONDecodeError
from typing import Callable, Any, Dict


class _MRSClientConfig(BaseModel):
    """
    Private class used for input validation
    """

    hostname: HttpUrl
    kadme_token: str = Field(min_length=1)
    username: str = Field(min_length=1)
    password: str = Field(min_length=1)


class ElasticsearchConfig(BaseModel):
    host: str
    port: int

    @property
    def url(self) -> HttpUrl:
        return TypeAdapter(HttpUrl).validate_strings(f"http://{self.host}:{self.port}")


class AsyncMRSClient:
    """This class is used for login, logout, and ticket validation by MRS (Memoza  Rest Server).

    Attributes:
        hostname (str): The complete base URL of the MRS server including the rest server path (e.g., 'http://server.com/memoza-rest-server').
        kadme_token (str): The KADME security token.
        username (str): The username for authentication.
        password (str): The password for authentication.
        ticket (str): The authentication ticket.
        client (httpx.Client): The HTTP client used to make requests.
    """

    def __init__(
        self,
        hostname,
        kadme_token: str,
        username: str,
        password: str | None = None,
        ticket: str | None = None,
        timeout: float = 120,
    ):
        """
        Initializes the MRSClient with the given parameters and authenticates the user.

        Args:
            hostname (str): The complete base URL of the MRS server including the rest server path 
                          (e.g., 'http://server.com/memoza-rest-server' or 'http://server.com/whereoil-rest-server').
            kadme_token (str): The KADME security token.
            username (str): The username for authentication.
            password (str): The password for authentication.
            ticket (str, optional): The authentication ticket. Default is None.
            timeout (int, optional): Request timeout in seconds. Default is 120.

        """

        # ```py
        # import asyncmrs

        # #input data can be stored in environmental variable or secrets.ini file
        # #example of storing login information with secrets.ini file

        # import configparser
        # config = configparser.ConfigParser()
        # config.read("secrets.ini")
        # host = config["API"]["HOSTNAME"]
        # kadme_token = config["API"]["KADME_TOKEN"]
        # username = config["API"]["USERNAME"]
        # password = config["API"]["PASSWORD"]

        # #initialization
        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # #unlike synchronous implementation needs to to be manually autheticated
        # await client.client.aclose() #close session after usage
        # ```
        try:
            if password is not None:
                _MRSClientConfig(
                    hostname=hostname,
                    kadme_token=kadme_token,
                    username=username,
                    password=password,
                )
        except ValidationError as e:
            raise ValueError(e)

        self.hostname = hostname
        self.username = username
        self.kadme_token = kadme_token
        self.client = httpx.AsyncClient(
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "kadme.security.token": self.kadme_token,
            },
            timeout=timeout,
        )
        if password is not None:
            self._ticket = ""
            self.password = password
        else:
            self._ticket = ticket
            self.client.headers.update({"ticket": f"{ticket}"})
        # {<namespace>: {"role_service": <role_service_value>, "roles": [<role_name>, ...]}}
        self._roles_cache: Dict[str, Dict[str, list[str]]] = {}

    async def _authenticate(self, oauth_token=None) -> str:
        """
        Authenticates the user and retrieves an authentication ticket.

        This method can also use an OAuth token from Azure for authentication.

        Args:
            oauth_token (str, optional): The OAuth token from Azure.

        Returns:
            str: The authentication ticket.
        """

        if hasattr(self, "password"):
            payload = {"userName": self.username, "password": self.password}
            url = f"{self.hostname}/security/auth/login.json"
            logging.debug(f"POST: {url}")
            if oauth_token != None:
                headers = {"Authorization": f"Bearer {oauth_token}"}
                r = await self.client.post(url, headers=headers, json=payload)
            else:
                r = await self.client.post(url, json=payload)
            r_json = r.json()
            if r.status_code != 200:
                await self._handle_error(r)
            ticket = r_json["ticket"]
            self.client.headers.update({"ticket": f"{ticket}"})
            return ticket
        else:
            return ""

    async def validate_ticket(self):
        """
        Validates the current authentication ticket.

        If the ticket is invalid or expired, it re-authenticates to get a new ticket.

        """
        # ```py
        # import asyncmrs

        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # await client.validate_ticket()
        # await client.client.aclose() #close session after usage
        # ```
        if hasattr(self, "password"):
            headers = {"ticket": f"{self._ticket}"}
            payload = {"userName": self.username, "password": self.password}
            if self._ticket == "":
                self._ticket = await self._authenticate()
            else:
                url = f"{self.hostname}/security/auth/validateticket.json"
                logging.debug(f"GET: {url}")
                r = await self.client.get(url, headers=headers, params=payload)
                if r.status_code == 401:
                    # logging.info(f"Retrieved error: {r.text}")
                    self._ticket = await self._authenticate()

    @property
    async def headers(self):
        """
        Property that returns headers stored in current client session after validating them.
        Validation doesn't happen if AsyncMRSClient was was initialized with kadme token and ticket only.
        """
        if hasattr(self, "password"):
            await self.validate_ticket()
        return self.client.headers

    @property
    async def ticket(self):
        """
        Property that returns currently stored ticket after validating it.
        Validation doesn't happen if AsyncMRSClient was was initialized with kadme token and ticket only.
        """
        if hasattr(self, "password"):
            await self.validate_ticket()
        return self._ticket

    async def close(self):
        """
        Logs out from MRS, ending all active sessions.

        Raises:
            httpx.HTTPStatusError: If an HTTP error occurs during logout.

        """

        # ```py
        # import asyncmrs

        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # await client.close() #dangerous call in itself not recommended for usage
        # await client.client.aclose() #close session after usage
        # ```
        headers = {
            "ticket": f"{self._ticket}",
        }
        logout_url = f"{self.hostname}/security/auth/logout.json"
        try:
            r = await self.client.post(logout_url, headers=headers, timeout=10.0)

            logging.info(f"Logout successful: {r.text}")
            r.raise_for_status()
        except httpx.HTTPStatusError as e:
            # if e.response.status_code == 401:
            #     logging.warning(
            #         "Received 401 Unauthorized during logout. Assuming the session is deactivated."
            #     )
            # else:
            #     logging.error(f"HTTP error occurred during logout: {e}")
            await self.client.aclose()
            raise e

    async def __aenter__(self):
        """
        Enters the runtime context related to this object.
        """
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Exits the runtime context related to this object, ensuring the session is closed.
        """
        await self.client.aclose()

    async def _handle_error(self, response: httpx.Response):
        """
        Handles errors raised during a RESTful request.

        Args:
            response (httpx.Response): The HTTP response object.

        Raises:
            MRSClientError: If the response status code is not 200 (OK). The exception
                            will contain the error code and message returned by the server.
        """
        error_data = response.json()
        logging.error(error_data)

        # Check if the error data contains a code
        if isinstance(error_data.get("error"), dict):
            error_code = error_data["error"].get("code", response.status_code)
            error_message = error_data["error"].get("message", "Unknown Error")
        else:
            error_code = response.status_code
            error_message = error_data.get("error", "Unknown Error")

        raise MRSClientError(error_code, error_message)

    async def request(
        self,
        method: str,
        endpoint: str,
        data=None,
        json=None,
        headers=None,
        enable_validation=True,
    ) -> dict | None:
        """
        Makes a RESTful request to the specified endpoint using the provided HTTP method and JSON data.

        Args:
            method (str): The HTTP method (GET, POST, PUT, DELETE).
            endpoint (str): The endpoint path relative to the MRS server base URL.
            json (dict, optional): The JSON data to send with the request (default is None).
            enable_validation (bool, optional): by default this method always validates ticket before sending the request but this field
                        can be set to False to skip tocket validation. For example this can be useful when sending multiple requests knowing that ticket hasn't been expired yet

        Returns:
            dict | None: The JSON response data parsed as a Python dictionary.

        Raises:
            ValueError: If the HTTP method is not one of GET, POST, PUT, or DELETE.
        """

        # ```py
        # import mrs

        # client = AsyncMRSClient(host, kadme_token, username, password)
        # await client._autheticate()
        # r = await client.request("POST", "/security/auth/login.json", "{"userName": username, "password": password}")
        # await client.client.aclose() #close session after usage
        # ```

        if hasattr(self, "password") and enable_validation:
            await self.validate_ticket()
        if method not in ("GET", "POST", "PUT", "DELETE"):
            raise ValueError("The REST method is not supported!")
        url: str = f"{self.hostname}{endpoint}"
        logging.debug(f"HTTP {method}: {url}")
        if data:
            logging.debug(f"BODY: {data}")
        r = await self.client.request(
            method, url, headers=headers, data=data, json=json
        )
        if r.status_code != 200:
            await self._handle_error(r)
        try:
            return r.json()
        except JSONDecodeError:
            return None

    async def get_all_namespaces(self):
        return await self.request("GET", "/schema/nsp.json")

    async def get_namespace(self, namespace: str):
        return await self.request("GET", f"/schema/nsp/{namespace}.json")

    async def get_datatype(self, namespace: str, datatype: str):
        return await self.request("GET", f"/schema/nsp/{namespace}/{datatype}.json")

    async def es_request(
        self,
        es_host: str,
        es_port: int,
        memoza_namespace: str,
        memoza_class: str,
        es_index: str,
        es_query: Callable[[str, bool, list[str]], Dict[str, Any]],
        enable_validation: bool = True,
    ):
        """
        Makes a request to the Elasticsearch "es_index/_search" API endpoint using POST method.
        User roles are used to filter the data returned by Elasticsearch (via "kmeta:Ent" field).
        create_es_query must contain:
            - "terms" with "kmeta:Ent" field to use roles filtering.
            - "term" with "type" field to specify the Memoza class.
        Args:
            es_host (str): The Elasticsearch host.
            es_port (int): The Elasticsearch port.
            memoza_namespace (str): The Memoza namespace.
            memoza_class (str): The Memoza class.
            es_index (str): The Elasticsearch index.
            es_query (Callable[[str], Dict[str, Any]]): The Elasticsearch query function.
            enable_validation (bool, optional): by default this method always validates ticket before sending the request but this field
                can be set to False to skip tocket validation. For example this can be useful when sending multiple requests knowing that ticket
            hasn't been expired yet

        Returns:
            dict: The JSON response data parsed as a Python dictionary.

        Raises:
            PermissionError: If user does not have access to the Memoza namespace or class.
        """

        # ```py
        # Example usage for es_query callable:
        # def create_es_query(mrs_class: str, apply_roles_filter: bool, kmeta_ent: List[str]) -> Dict[str, Any]:
        # if apply_roles_filter:
        #    query = {
        #        "query": {
        #           "bool": {
        #                "must": [
        #                    {"term": {"type": mrs_class}},
        #                    {"match": {"field": "value"}},
        #                ]
        #            }
        #        }
        #    }
        #    if apply_roles_filter:
        #        query["query"]["bool"]["must"].append({
        #            "terms": {
        #                "kmeta:Ent": kmeta_ent
        #            }
        #        })
        # ```

        es_config = ElasticsearchConfig(
            host=es_host,
            port=es_port,
        )

        # Check user permissions
        permissions_url = f"/permissions/permissions.json?object={memoza_namespace}"
        permissions_response = await self.request(
            "GET", permissions_url, enable_validation=enable_validation
        )
        logging.debug(
            f"es_request: Permissions {memoza_namespace} response: {permissions_response}"
        )

        if not permissions_response or not permissions_response["VISIBLE"]:
            raise PermissionError(
                f"User does not have access to namespace: {memoza_namespace}"
            )

        permissions_url = f"/permissions/permissions.json?object={memoza_class}"
        permissions_response = await self.request(
            "GET", permissions_url, enable_validation=enable_validation
        )
        logging.debug(
            f"es_request: Permissions {memoza_class} response: {permissions_response}"
        )

        if not permissions_response or not permissions_response["VISIBLE"]:
            raise PermissionError(
                f"User does not have access to class: {memoza_class} in namespace: {memoza_namespace}"
            )

        apply_roles_filter, user_roles = await self.get_user_roles(memoza_namespace)
        logging.debug(f"User roles for namespace {memoza_namespace}: {user_roles}")
        query = es_query(memoza_class, apply_roles_filter, user_roles)

        # Encode the query to ensure proper handling of non-ASCII characters
        encoded_query = json.dumps(query, ensure_ascii=False).encode("utf-8")

        logging.debug(f"Generated Elasticsearch query: {encoded_query.decode('utf-8')}")

        # Prepare and send request to Elasticsearch
        es_url = f"{es_config.url}{es_index}/_search"
        headers = {"Content-Type": "application/json; charset=utf-8"}
        logging.debug(f"Sending request to Elasticsearch: {es_url}")
        logging.debug(f"Request headers: {headers}")
        logging.debug(f"Request body: {encoded_query.decode('utf-8')}")

        async with httpx.AsyncClient() as es_client:
            response = await es_client.post(es_url, json=query, headers=headers)
            logging.debug(f"es_request: Elasticsearch response: {response}")

        if response.status_code != 200:
            await self._handle_error(response)
        try:
            return response.json()
        except JSONDecodeError:
            return None

    async def get_user_roles(self, namespace: str) -> tuple[bool, list[str]]:
        """
        Get user roles for a specific namespace. Roles are relevant only if role_service is enabled.
        If role_service is not enabled, the method returns an empty list. If role_service is enabled,
        the method returns a list of roles for the user, role "P" (Public) is added automatically.
        Retrieved roles are cached for the namespace.

        Args:
            namespace (str): The namespace to get roles for.

        Returns:
            tuple[bool, list[str]]: A tuple containing:
                - A boolean indicating whether role_service is enabled
                - A list of strings containing the user's roles for the specified namespace.

        Note:
            This method caches the results for each namespace to avoid unnecessary requests.
        """
        logging.debug(f"Getting user roles for namespace: {namespace}")

        if namespace not in self._roles_cache:
            logging.debug(
                f"Roles for namespace {namespace} not found in cache. Fetching from server."
            )
            endpoint = f"/settings/data/{namespace}.json"
            role_service_r = await self.request("GET", endpoint)
            self._roles_cache[namespace] = {}
            self._roles_cache[namespace]["role_service"] = role_service_r.get(
                "role_service"
            )

            if self._roles_cache[namespace]["role_service"]:
                logging.debug(
                    f"Role service enabled for namespace {namespace}. Fetching roles."
                )
                endpoint = f"/security/roles/nsp/{namespace}.json"
                roles = await self.request("GET", endpoint)
                self._roles_cache[namespace]["roles"] = roles + ["P"]
                logging.debug(
                    f"Roles fetched for namespace {namespace}: {self._roles_cache[namespace]['roles']}"
                )
            else:
                logging.debug(
                    f"Role service not enabled for namespace {namespace}. Using empty role list."
                )
                self._roles_cache[namespace]["roles"] = []
        else:
            logging.debug(f"Using cached roles for namespace {namespace}")

        role_service_enabled = bool(self._roles_cache[namespace]["role_service"])
        roles = self._roles_cache[namespace]["roles"]
        logging.debug(
            f"Returning roles for namespace {namespace}: role_service_enabled={role_service_enabled}, roles={roles}"
        )
        return role_service_enabled, roles

    async def upload_file(
        self, domain: dict, destinationPath: str, data: bytes
    ) -> dict | None:
        """
        Upload a file to the server.

        Args:
            domain (dict):  The metaDomain record linked to the file. In JSON format: {"type": "theschemaclass", "uri": "UNIQUEID"}
            destinationPath (str): The desired path to the file in MRS server.
            data (bytes): The actual file to be uploaded in binary format.

        Returns:
            dict | None: The response is a JSON-format of the metaDomain that was submitted,
                with additional properties populated reflecting the stored file in the respective storage.
                None if an error happend during request.
        """
        files = {
            "domain": (json.dumps(domain), "application/json"),
            "destinationPath": (destinationPath, "text/plain"),
            "file": (data, "application/octet-stream"),
        }
        url: str = f"/upload/fileTo.json"
        headers = {"Content-Type": f"multipart/form-data; boundary={domain['uri']}"}

        response = await self.request(
            method="POST", endpoint=url, data=files, headers=headers
        )
        return response
