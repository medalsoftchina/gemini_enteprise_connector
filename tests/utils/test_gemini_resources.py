from connector.config import GeminiSettings
from connector.utils.gemini_resources import GeminiResourceManager


class FakeNotFound(Exception):
    code = 404


class FakeOperation:
    def __init__(self, payload):
        self._payload = payload

    def result(self):
        return self._payload


class FakeIdentityClient:
    def __init__(self, *, exists: bool) -> None:
        self.exists = exists
        self.created = False

    def location_path(self, project: str, location: str) -> str:
        return f"projects/{project}/locations/{location}"

    def identity_mapping_store_path(self, project: str, location: str, identity_mapping_store: str) -> str:
        return f"projects/{project}/locations/{location}/identityMappingStores/{identity_mapping_store}"

    def get_identity_mapping_store(self, name: str):
        if not self.exists:
            raise FakeNotFound()
        return {"name": name}

    def create_identity_mapping_store(self, request):
        self.created = True
        self.exists = True
        name = f"{request['parent']}/identityMappingStores/{request['identity_mapping_store_id']}"
        return {"name": name}


class FakeDataStoreClient:
    def __init__(self, *, exists: bool) -> None:
        self.exists = exists
        self.created_request = None

    def collection_path(self, project: str, location: str, collection: str) -> str:
        return f"projects/{project}/locations/{location}/collections/{collection}"

    def data_store_path(self, project: str, location: str, data_store: str) -> str:
        return f"projects/{project}/locations/{location}/dataStores/{data_store}"

    def get_data_store(self, name: str):
        if not self.exists:
            raise FakeNotFound()
        return {"name": name}

    def create_data_store(self, request):
        self.created_request = request
        self.exists = True
        name = f"{request['parent']}/dataStores/{request['data_store_id']}"
        return FakeOperation({"name": name})


def make_settings(**overrides) -> GeminiSettings:
    params = dict(
        project_id="demo-project",
        location="global",
        data_store_id="serviceme-kb",
        identity_mapping_store_id="serviceme-ims",
        data_store_display_name="SERVICEME Connector",
        auto_create_resources=True,
        acl_enabled=True,
    )
    params.update(overrides)
    return GeminiSettings(**params)


def test_resource_manager_returns_existing_names() -> None:
    identity_client = FakeIdentityClient(exists=True)
    data_store_client = FakeDataStoreClient(exists=True)
    manager = GeminiResourceManager(
        make_settings(),
        identity_client=identity_client,
        data_store_client=data_store_client,
    )

    handles = manager.ensure()

    assert handles.identity_mapping_store_name.endswith("serviceme-ims")
    assert handles.data_store_name.endswith("serviceme-kb")
    assert identity_client.created is False
    assert data_store_client.created_request is None


def test_resource_manager_creates_missing_resources() -> None:
    identity_client = FakeIdentityClient(exists=False)
    data_store_client = FakeDataStoreClient(exists=False)
    manager = GeminiResourceManager(
        make_settings(),
        identity_client=identity_client,
        data_store_client=data_store_client,
    )

    handles = manager.ensure()

    assert identity_client.created is True
    assert data_store_client.created_request is not None
    assert handles.identity_mapping_store_name.endswith("serviceme-ims")
    assert handles.data_store_name.endswith("serviceme-kb")


def test_resource_manager_skips_identity_when_acl_disabled() -> None:
    identity_client = FakeIdentityClient(exists=False)
    data_store_client = FakeDataStoreClient(exists=False)
    manager = GeminiResourceManager(
        make_settings(acl_enabled=False),
        identity_client=identity_client,
        data_store_client=data_store_client,
    )

    handles = manager.ensure()

    assert handles.identity_mapping_store_name is None
    assert identity_client.created is False
    assert data_store_client.created_request is not None
    assert "identity_mapping_store" not in data_store_client.created_request["data_store"]
