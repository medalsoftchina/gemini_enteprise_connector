from connector.schema.workspace import Workspace
from connector.utils.debug_dump import MarkdownDumpManager


def test_dump_writes_files_with_structure(tmp_path) -> None:
    dumper = MarkdownDumpManager(enabled=True, root_dir=str(tmp_path))
    workspace = Workspace(id="ws-1", name="Test Workspace", category=None, raw={})
    documents = [
        {
            "id": "doc-1",
            "content": "Hello",
            "fullPath": "/folder/doc",
            "_debug_download": {
                "url": "https://example.com/api",
                "authorization": "openapi token",
                "body": {"id": 1},
            },
        },
        {"id": "doc-2", "content": "World", "name": "Readme"},
    ]

    dumper.dump(workspace, documents)

    assert dumper.run_dir is not None
    dumped_files = list(dumper.run_dir.glob("**/*.md"))
    contents = [path.read_text(encoding="utf-8") for path in dumped_files]
    assert "Hello" in contents
    assert "World" in contents
    curl_files = list(dumper.run_dir.glob("**/*.curl.sh"))
    assert curl_files


def test_dump_disabled_creates_nothing(tmp_path) -> None:
    dumper = MarkdownDumpManager(enabled=False, root_dir=str(tmp_path))
    workspace = Workspace(id="ws-1", name="Test", category=None, raw={})

    dumper.dump(workspace, [])

    assert dumper.run_dir is None
    assert not list(tmp_path.iterdir())
