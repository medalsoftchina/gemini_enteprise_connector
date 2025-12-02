# Usage · 自定义 Connector

本指南介绍如何在本地或 CI 环境中配置并运行 Gemini Enterprise SERVICEME Connector，涵盖配置文件说明、环境变量、以及同步命令。

## 1. 项目配置文件

- 核心配置位于 `src/connector/config.py`，该模块通过 `ConnectorSettings.from_env()` 读取环境变量并完成以下工作：
  - `ServicemeAuthSettings`：封装 SERVICEME 认证信息，并根据账号生成唯一 scope（`serviceme::<account>::full_access`）。
  - `SyncSettings`：支持通过 `SYNC_WORKSPACE_IDS` / `SYNC_WORKSPACE_NAMES` 筛选特定文档空间，若为空则默认同步全部空间。
  - `GeminiSettings`：描述 Gemini 项目、数据仓库及 Identity Mapping Store。

> 因此无须单独维护 `.yaml` 或 `.json` 配置，只需提供相应环境变量即可。

## 2. 环境准备步骤

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 3. 设置环境变量

在项目根目录创建 `.env.local`（或使用您习惯的秘密管理方案），参考如下模板：

```dotenv
SERVICEME_BASE_URL=https://your-serviceme.example.com
SERVICEME_CLIENT_ID=xxx
SERVICEME_CLIENT_SECRET=xxx
SERVICEME_ACCOUNT=workspace-sync-user@example.com

GEMINI_PROJECT_ID=gcp-project-id
GEMINI_LOCATION=global
GEMINI_DATA_STORE_ID=serviceme-kb
GEMINI_IDENTITY_MAPPING_STORE_ID=serviceme-ims
GEMINI_DATA_STORE_DISPLAY_NAME=SERVICEME Connector
GEMINI_AUTO_CREATE_RESOURCES=true
GEMINI_DATA_STORE_ACL_ENABLED=false
GEMINI_ACL_MODE=idp_wide
# principal_list 模式需要配置默认读者（逗号分隔 email / group: / external:）
GEMINI_DEFAULT_ACL_READERS=

# 同步模式与过滤
SYNC_MODE=incremental
SYNC_WORKSPACE_IDS=ws-123,ws-789
SYNC_WORKSPACE_NAMES=产品知识库,内部FAQ
SYNC_DEBUG_DUMP_MARKDOWN=false
SYNC_DEBUG_DUMP_DIR=tmp
```

- `SYNC_WORKSPACE_IDS` / `SYNC_WORKSPACE_NAMES` 可以任选其一或同时使用，逗号分隔；若都为空则同步全部空间。
- `GCS_BUCKET`、`GCS_BLOB_PREFIX` 目前仅为未来“GCS 全量同步（JSONL + ImportDocuments）”预留，当前代码路径尚未调用；如果有这类需求，需要实现 `GeminiIngestService` 中的 GCS 导入逻辑后再启用。
- `GEMINI_DATA_STORE_ACL_ENABLED`：是否启用 Discovery Engine ACL。`false` 表示创建/使用无 ACL 的 Data Store（无需 Identity Mapping Store）；`true` 时才需要配置 Identity Store 及下方 ACL 选项。
- `GEMINI_ACL_MODE`：仅在 Data Store 启用 ACL 时生效，用于告诉 Connector 如何生成 `Document.acl_info`。
  - `idp_wide`（默认）：文档对当前 Identity Provider 内的全部用户开放，适合 SERVICEME 暂未暴露成员列表或只想快速验证的场景。
  - `principal_list`：从 `Document.metadata['aclReaders']` 以及 `GEMINI_DEFAULT_ACL_READERS` 中收集账号，构造 `Principal`（支持 `user@example.com`、`group:xxx@example.com`、`external:xxx`）。若二者都为空，同步流程会抛出 `GeminiIngestError`。
- `GEMINI_DEFAULT_ACL_READERS`：在 `principal_list` 模式下的兜底读者列表，逗号分隔。
- `SYNC_DEBUG_DUMP_MARKDOWN` / `SYNC_DEBUG_DUMP_DIR`：打开后会在项目根目录下的 `tmp/<timestamp>/` 里按 workspace + 原路径把下载的 Markdown 文件落盘，方便调试（默认关闭，记得在生产关闭）。

### SERVICEME OAuth2.0 认证

- `ServicemeClient` 会在每次运行时调用 `/openapi/auth/client_with_account` 接口，以 `SERVICEME_CLIENT_ID` + `SERVICEME_CLIENT_SECRET` + `SERVICEME_ACCOUNT` 生成签名并换取 `access_token`，随后缓存至过期。
- 成功认证后，程序会先调用 `/v1/openapi/workspace/file` 列举空间内的文件，再通过 `/v1/openapi/workspace/file/downloadDocument2MD` 将内容转换为 Markdown 后同步至 Gemini。
- 若访问 `/v1/openapi/workspace/all` 返回 401，请重新确认上述三个变量或账号权限；新的逻辑已默认在 30 秒前刷新 token，因此无需手动干预。

### 如何获取 `GEMINI_DATA_STORE_ID` 与 `GEMINI_IDENTITY_MAPPING_STORE_ID`

1. **自动创建（默认）**
   - 当 `GEMINI_AUTO_CREATE_RESOURCES=true` 时，`python -m connector.sync` 会先运行 `connector.utils.gemini_resources.GeminiResourceManager`：
     1. 枚举 `IdentityMappingStore`，若不存在则调用 `IdentityMappingStoreServiceClient.create_identity_mapping_store` 创建；
     2. 确认 Discovery Engine Data Store 是否存在；若不存在则绑定刚创建的 Identity Store 并调用 `DataStoreServiceClient.create_data_store`（父级 `default_collection`）；
     3. 创建成功后直接使用返回的 `name` 执行后续数据写入，无需手动回填。
   - 若希望在 CI/CD 之外由管理员统一创建，可把 `GEMINI_AUTO_CREATE_RESOURCES` 设为 `false`，程序将跳过该步骤并假设资源已存在。
   - **注意**：自动创建需要可用的 Google Application Default Credentials（设置 `GOOGLE_APPLICATION_CREDENTIALS`、`GOOGLE_APPLICATION_CREDENTIALS_JSON` 或执行 `gcloud auth application-default login`）。否则程序会报错提示缺少凭证。

2. **手动创建（关闭自动模式时参考）**

   **Identity Mapping Store**
   - 参阅 `docs/Create custom connector.md` 中的 “Retrieve or create identity store” 章节。
   - 使用 `IdentityMappingStoreServiceClient`（或直接调用 Discovery Engine REST API）创建存储，记录响应里的 `name`，形如  
     `projects/<PROJECT_ID>/locations/<LOCATION>/identityMappingStores/<STORE_ID>`。
   - `GEMINI_IDENTITY_MAPPING_STORE_ID` 就是上面路径中的 `<STORE_ID>`，保持与数据仓库绑定的一致性。
   **Discovery Engine Data Store**
   - 执行同一章节里的 “Create data store” 流程，或在控制台创建 Discovery Engine 数据库。
   - 创建时需指定 `industry_vertical`、绑定到上一步的 Identity Store，并开启 ACL。
   - 记录返回的 `name`（`projects/.../dataStores/<DATA_STORE_ID>`）；将 `<DATA_STORE_ID>` 赋值给 `GEMINI_DATA_STORE_ID`。
3. **验证设置**
   - 运行 `gcloud discoveryengine data-stores list --project=$GEMINI_PROJECT_ID --location=$GEMINI_LOCATION` 核对 ID 是否存在。
   - 同理使用 `identity-mapping-stores list` 命令确认 Identity Store 是否可用。
   - 如果 Data Store 开启了 ACL（`GEMINI_DATA_STORE_ACL_ENABLED=true`），请同步 `IdentityMappingStore`：调用 `IdentityMappingStoreServiceClient.import_identity_mappings` 或 REST API，把 SERVICEME 账号 / 组织与 Google Identity (user / group) 的映射写入其中，否则 `principal_list` 模式的 `Principal.user_id` 将无法被识别。

> 如果要在 CI 中自动化这两个资源，可在部署脚本里调用相应 REST/客户端 API，并在输出中显式打印 `STORE_ID` 与 `DATA_STORE_ID`，方便回填到密钥管理服务。

## 4. 运行同步

激活虚拟环境并加载 `.env.local` 后执行：

```bash
python -m connector.sync
```

命令会：
1. 调用 SERVICEME `/openapi/auth/client_with_account` 交换 access token（第 3 节的配置必须正确）。
2. 枚举工作空间，逐个调用 `/v1/openapi/workspace/file` 和 `/v1/openapi/workspace/file/downloadDocument2MD` 下载 Markdown，生成带 metadata 的 `Document`。
3. 使用 `google-cloud-discoveryengine` 的 `DocumentServiceClient.import_documents` 将文档写入 `projects/$GEMINI_PROJECT_ID/locations/$GEMINI_LOCATION/dataStores/$GEMINI_DATA_STORE_ID`（增量模式）。
4. 在控制台输出 JSON 汇总，形如：

```json
{
  "total_documents": 42,
  "workspaces": [
    {"workspace_id": "ws-123", "workspace_name": "产品知识库", "document_count": 30},
    {"workspace_id": "ws-789", "workspace_name": "内部FAQ", "document_count": 12}
  ]
}
```

## 5. 常见验证步骤

1. `pytest`：确保 OAuth 模拟、筛选器及同步流程的单元测试全部通过。
2. `ruff check src tests && ruff format src tests`：保持项目风格一致。
3. `mypy src`：静态类型校验，避免部署时才发现接口不一致。

按照以上步骤即可完成配置并触发同步。若后续扩展真实的 Discovery Engine 客户端或 GCS 全量同步，只需继续在 `config.py` 中声明新的环境变量，并在 `docs/usage.md` 更新对应说明。

### Data Store 中看不到文档？

依次确认：
- `pip install -r requirements.txt` 成功，并包含 `google-cloud-discoveryengine`；
- 运行同步的终端已经加载 `.env.local`，且 `GEMINI_*` 指向的资源真实存在；
- 执行 `python -m connector.sync` 时日志中 **没有** `connector.client.gemini` 抛出的 `GeminiIngestError` 或 Google API 错误；
- 服务账号 / ADC 对 Data Store 拥有 Discovery Engine Admin 权限，以及组织位置策略允许使用 `GEMINI_LOCATION`。

若仍为空，请复制同步日志中 `connector.client.gemini` 的 INFO/ERROR 行，结合 `docs/Create custom connector.md` §“Upload documents inline”说明排查。
