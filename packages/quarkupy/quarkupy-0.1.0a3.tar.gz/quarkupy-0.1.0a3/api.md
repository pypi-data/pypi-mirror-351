# Management

Types:

```python
from quark.types import (
    Identity,
    SuccessResponseMessage,
    ManagementRetrieveResponse,
    ManagementRetrievePythonStatusResponse,
    ManagementRetrieveTokioResponse,
)
```

Methods:

- <code title="get /management">client.management.<a href="./src/quark/resources/management.py">retrieve</a>() -> <a href="./src/quark/types/management_retrieve_response.py">ManagementRetrieveResponse</a></code>
- <code title="post /management/ping">client.management.<a href="./src/quark/resources/management.py">ping</a>() -> <a href="./src/quark/types/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /management/auth_status">client.management.<a href="./src/quark/resources/management.py">retrieve_auth_status</a>() -> <a href="./src/quark/types/identity.py">Identity</a></code>
- <code title="get /management/python_status">client.management.<a href="./src/quark/resources/management.py">retrieve_python_status</a>() -> <a href="./src/quark/types/management_retrieve_python_status_response.py">ManagementRetrievePythonStatusResponse</a></code>
- <code title="get /management/tokio">client.management.<a href="./src/quark/resources/management.py">retrieve_tokio</a>(\*\*<a href="src/quark/types/management_retrieve_tokio_params.py">params</a>) -> <a href="./src/quark/types/management_retrieve_tokio_response.py">ManagementRetrieveTokioResponse</a></code>

# Agent

Types:

```python
from quark.types import AgentRetrieveResponse
```

Methods:

- <code title="get /agent">client.agent.<a href="./src/quark/resources/agent.py">retrieve</a>() -> <a href="./src/quark/types/agent_retrieve_response.py">AgentRetrieveResponse</a></code>
- <code title="post /agent/echo">client.agent.<a href="./src/quark/resources/agent.py">echo</a>() -> <a href="./src/quark/types/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="post /agent/one_step_rag_inference">client.agent.<a href="./src/quark/resources/agent.py">one_step_rag_inference</a>(\*\*<a href="src/quark/types/agent_one_step_rag_inference_params.py">params</a>) -> object</code>

# Registry

Types:

```python
from quark.types import RegistryListResponse
```

Methods:

- <code title="get /registry">client.registry.<a href="./src/quark/resources/registry/registry.py">list</a>() -> <a href="./src/quark/types/registry_list_response.py">RegistryListResponse</a></code>

## Quark

Types:

```python
from quark.types.registry import DescribedInputField, QuarkRegistryItem, QuarkTag, SchemaInfo
```

Methods:

- <code title="get /registry/quark/{cat}/{name}">client.registry.quark.<a href="./src/quark/resources/registry/quark/quark.py">retrieve</a>(name, \*, cat) -> <a href="./src/quark/types/registry/quark_registry_item.py">QuarkRegistryItem</a></code>

### Files

#### S3ReadFilesBinary

Types:

```python
from quark.types.registry.quark.files import QuarkHistoryItem
```

Methods:

- <code title="post /registry/quark/files/s3_read_files_binary/run">client.registry.quark.files.s3_read_files_binary.<a href="./src/quark/resources/registry/quark/files/s3_read_files_binary.py">run</a>(\*\*<a href="src/quark/types/registry/quark/files/s3_read_files_binary_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

#### S3ReadCsv

Methods:

- <code title="post /registry/quark/files/s3_read_csv/run">client.registry.quark.files.s3_read_csv.<a href="./src/quark/resources/registry/quark/files/s3_read_csv.py">run</a>(\*\*<a href="src/quark/types/registry/quark/files/s3_read_csv_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

### Extractor

#### DoclingExtractor

Methods:

- <code title="post /registry/quark/extractor/docling_extractor/run">client.registry.quark.extractor.docling_extractor.<a href="./src/quark/resources/registry/quark/extractor/docling_extractor.py">run</a>(\*\*<a href="src/quark/types/registry/quark/extractor/docling_extractor_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

### AI

#### OpenAIEmbeddings

Methods:

- <code title="post /registry/quark/ai/openai_embeddings/run">client.registry.quark.ai.openai_embeddings.<a href="./src/quark/resources/registry/quark/ai/openai_embeddings.py">run</a>(\*\*<a href="src/quark/types/registry/quark/ai/openai_embedding_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

#### OpenAICompletionBase

Methods:

- <code title="post /registry/quark/ai/openai_completion_base/run">client.registry.quark.ai.openai_completion_base.<a href="./src/quark/resources/registry/quark/ai/openai_completion_base.py">run</a>(\*\*<a href="src/quark/types/registry/quark/ai/openai_completion_base_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

### Transformer

#### DoclingChunker

Methods:

- <code title="post /registry/quark/transformer/docling_chunker/run">client.registry.quark.transformer.docling_chunker.<a href="./src/quark/resources/registry/quark/transformer/docling_chunker.py">run</a>(\*\*<a href="src/quark/types/registry/quark/transformer/docling_chunker_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

#### HandlebarsBase

Methods:

- <code title="post /registry/quark/transformer/handlebars_base/run">client.registry.quark.transformer.handlebars_base.<a href="./src/quark/resources/registry/quark/transformer/handlebars_base.py">run</a>(\*\*<a href="src/quark/types/registry/quark/transformer/handlebars_base_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

### Databases

#### SnowflakeRead

Methods:

- <code title="post /registry/quark/databases/snowflake_read/run">client.registry.quark.databases.snowflake_read.<a href="./src/quark/resources/registry/quark/databases/snowflake_read.py">run</a>(\*\*<a href="src/quark/types/registry/quark/databases/snowflake_read_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

### Vector

#### LancedbIngest

Methods:

- <code title="post /registry/quark/vector/lancedb_ingest/run">client.registry.quark.vector.lancedb_ingest.<a href="./src/quark/resources/registry/quark/vector/lancedb_ingest.py">run</a>(\*\*<a href="src/quark/types/registry/quark/vector/lancedb_ingest_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

#### LancedbSearch

Methods:

- <code title="post /registry/quark/vector/lancedb_search/run">client.registry.quark.vector.lancedb_search.<a href="./src/quark/resources/registry/quark/vector/lancedb_search.py">run</a>(\*\*<a href="src/quark/types/registry/quark/vector/lancedb_search_run_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

## Lattice

Types:

```python
from quark.types.registry import LatticeReactFlowPos, LatticeRegistryItem, LatticeFlowResponse
```

Methods:

- <code title="get /registry/lattice/{id}">client.registry.lattice.<a href="./src/quark/resources/registry/lattice.py">retrieve</a>(id) -> <a href="./src/quark/types/registry/lattice_registry_item.py">LatticeRegistryItem</a></code>
- <code title="get /registry/lattice/{id}/flow">client.registry.lattice.<a href="./src/quark/resources/registry/lattice.py">flow</a>(id) -> <a href="./src/quark/types/registry/lattice_flow_response.py">LatticeFlowResponse</a></code>
- <code title="put /registry/lattice/register">client.registry.lattice.<a href="./src/quark/resources/registry/lattice.py">register</a>(\*\*<a href="src/quark/types/registry/lattice_register_params.py">params</a>) -> <a href="./src/quark/types/success_response_message.py">SuccessResponseMessage</a></code>

# History

Types:

```python
from quark.types import HistoryListResponse, HistoryListLatticesResponse, HistoryListQuarksResponse
```

Methods:

- <code title="get /history">client.history.<a href="./src/quark/resources/history/history.py">list</a>() -> <a href="./src/quark/types/history_list_response.py">HistoryListResponse</a></code>
- <code title="get /history/clear_all_history">client.history.<a href="./src/quark/resources/history/history.py">clear_all</a>() -> <a href="./src/quark/types/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /history/lattices">client.history.<a href="./src/quark/resources/history/history.py">list_lattices</a>(\*\*<a href="src/quark/types/history_list_lattices_params.py">params</a>) -> <a href="./src/quark/types/history_list_lattices_response.py">HistoryListLatticesResponse</a></code>
- <code title="get /history/quarks">client.history.<a href="./src/quark/resources/history/history.py">list_quarks</a>(\*\*<a href="src/quark/types/history_list_quarks_params.py">params</a>) -> <a href="./src/quark/types/history_list_quarks_response.py">HistoryListQuarksResponse</a></code>

## Quark

Methods:

- <code title="get /history/quark/{id}">client.history.quark.<a href="./src/quark/resources/history/quark.py">retrieve</a>(id) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>
- <code title="put /history/quark">client.history.quark.<a href="./src/quark/resources/history/quark.py">update</a>(\*\*<a href="src/quark/types/history/quark_update_params.py">params</a>) -> <a href="./src/quark/types/registry/quark/files/quark_history_item.py">QuarkHistoryItem</a></code>

## Lattice

Types:

```python
from quark.types.history import LatticeHistoryItem
```

Methods:

- <code title="get /history/lattice/{id}">client.history.lattice.<a href="./src/quark/resources/history/lattice.py">retrieve</a>(id) -> <a href="./src/quark/types/history/lattice_history_item.py">LatticeHistoryItem</a></code>
- <code title="put /history/lattice">client.history.lattice.<a href="./src/quark/resources/history/lattice.py">update</a>(\*\*<a href="src/quark/types/history/lattice_update_params.py">params</a>) -> <a href="./src/quark/types/history/lattice_history_item.py">LatticeHistoryItem</a></code>

# Dataset

Types:

```python
from quark.types import (
    DataSetInfo,
    DatasetListResponse,
    DatasetRetrieveCsvResponse,
    DatasetRetrieveJsonResponse,
)
```

Methods:

- <code title="get /dataset/{id}">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve</a>(id) -> <a href="./src/quark/types/data_set_info.py">DataSetInfo</a></code>
- <code title="get /dataset">client.dataset.<a href="./src/quark/resources/dataset.py">list</a>() -> <a href="./src/quark/types/dataset_list_response.py">DatasetListResponse</a></code>
- <code title="get /dataset/clear_generated_datasets">client.dataset.<a href="./src/quark/resources/dataset.py">clear_generated</a>() -> <a href="./src/quark/types/success_response_message.py">SuccessResponseMessage</a></code>
- <code title="get /dataset/{id}/arrow">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve_arrow</a>(id, \*\*<a href="src/quark/types/dataset_retrieve_arrow_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/csv">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve_csv</a>(id, \*\*<a href="src/quark/types/dataset_retrieve_csv_params.py">params</a>) -> str</code>
- <code title="get /dataset/{id}/{file_id}/chunks">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve_file_chunks</a>(file_id, \*, id, \*\*<a href="src/quark/types/dataset_retrieve_file_chunks_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/files">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve_files</a>(id, \*\*<a href="src/quark/types/dataset_retrieve_files_params.py">params</a>) -> BinaryAPIResponse</code>
- <code title="get /dataset/{id}/json">client.dataset.<a href="./src/quark/resources/dataset.py">retrieve_json</a>(id, \*\*<a href="src/quark/types/dataset_retrieve_json_params.py">params</a>) -> str</code>
