# Documents

Types:

```python
from particle_sdk.types import Document, ResponseMessage, DocumentGetPatientDocumentsResponse
```

Methods:

- <code title="get /api/v1/documents/{id}">client.documents.<a href="./src/particle_sdk/resources/documents.py">retrieve</a>(id) -> <a href="./src/particle_sdk/types/document.py">Document</a></code>
- <code title="delete /api/v1/documents/{id}">client.documents.<a href="./src/particle_sdk/resources/documents.py">delete</a>(id) -> <a href="./src/particle_sdk/types/response_message.py">ResponseMessage</a></code>
- <code title="get /api/v1/documents/patient/{id}">client.documents.<a href="./src/particle_sdk/resources/documents.py">get_patient_documents</a>(id) -> <a href="./src/particle_sdk/types/document_get_patient_documents_response.py">DocumentGetPatientDocumentsResponse</a></code>
- <code title="post /api/v1/documents">client.documents.<a href="./src/particle_sdk/resources/documents.py">submit</a>(\*\*<a href="src/particle_sdk/types/document_submit_params.py">params</a>) -> <a href="./src/particle_sdk/types/document.py">Document</a></code>

# Files

Methods:

- <code title="get /api/v1/files/{query_id}/{file_id}">client.files.<a href="./src/particle_sdk/resources/files.py">download</a>(file_id, \*, query_id) -> BinaryAPIResponse</code>
- <code title="get /api/v1/files/{query_id}/zip">client.files.<a href="./src/particle_sdk/resources/files.py">download_zip</a>(query_id) -> BinaryAPIResponse</code>

# Patients

Types:

```python
from particle_sdk.types import Patient, PatientListResponse, PatientSearchResponse
```

Methods:

- <code title="get /api/v1/patients/{id}">client.patients.<a href="./src/particle_sdk/resources/patients.py">retrieve</a>(id) -> <a href="./src/particle_sdk/types/patient.py">Patient</a></code>
- <code title="get /api/v1/patients">client.patients.<a href="./src/particle_sdk/resources/patients.py">list</a>(\*\*<a href="src/particle_sdk/types/patient_list_params.py">params</a>) -> <a href="./src/particle_sdk/types/patient_list_response.py">PatientListResponse</a></code>
- <code title="delete /api/v1/patients/{id}">client.patients.<a href="./src/particle_sdk/resources/patients.py">delete</a>(id) -> <a href="./src/particle_sdk/types/response_message.py">ResponseMessage</a></code>
- <code title="post /api/v1/patients/search">client.patients.<a href="./src/particle_sdk/resources/patients.py">search</a>(\*\*<a href="src/particle_sdk/types/patient_search_params.py">params</a>) -> <a href="./src/particle_sdk/types/patient_search_response.py">PatientSearchResponse</a></code>
- <code title="post /api/v1/patients">client.patients.<a href="./src/particle_sdk/resources/patients.py">submit</a>(\*\*<a href="src/particle_sdk/types/patient_submit_params.py">params</a>) -> <a href="./src/particle_sdk/types/patient.py">Patient</a></code>

# Projects

## Batches

Types:

```python
from particle_sdk.types.projects import Batch
```

Methods:

- <code title="post /api/v1/projects/{project_id}/batches">client.projects.batches.<a href="./src/particle_sdk/resources/projects/batches.py">create</a>(project_id, \*\*<a href="src/particle_sdk/types/projects/batch_create_params.py">params</a>) -> <a href="./src/particle_sdk/types/projects/batch.py">Batch</a></code>
- <code title="get /api/v1/projects/{project_id}/batches/{batch_id}">client.projects.batches.<a href="./src/particle_sdk/resources/projects/batches.py">retrieve</a>(batch_id, \*, project_id) -> <a href="./src/particle_sdk/types/projects/batch.py">Batch</a></code>
- <code title="get /api/v1/projects/{project_id}/batches">client.projects.batches.<a href="./src/particle_sdk/resources/projects/batches.py">list</a>(project_id) -> <a href="./src/particle_sdk/types/projects/batch.py">Batch</a></code>

# Queries

Types:

```python
from particle_sdk.types import Query, QueryListResponse
```

Methods:

- <code title="post /api/v1/queries">client.queries.<a href="./src/particle_sdk/resources/queries.py">create</a>(\*\*<a href="src/particle_sdk/types/query_create_params.py">params</a>) -> <a href="./src/particle_sdk/types/query.py">Query</a></code>
- <code title="get /api/v1/queries/{id}">client.queries.<a href="./src/particle_sdk/resources/queries.py">retrieve</a>(id) -> <a href="./src/particle_sdk/types/query.py">Query</a></code>
- <code title="get /api/v1/queries/">client.queries.<a href="./src/particle_sdk/resources/queries.py">list</a>() -> <a href="./src/particle_sdk/types/query_list_response.py">QueryListResponse</a></code>

# Auth

Types:

```python
from particle_sdk.types import AuthGenerateTokenResponse
```

Methods:

- <code title="get /auth">client.auth.<a href="./src/particle_sdk/resources/auth.py">generate_token</a>() -> str</code>

# Deltas

Types:

```python
from particle_sdk.types import (
    DeltaCollectFlatDatasetsResponse,
    DeltaRetrieveResourceResponse,
    DeltaSubmitResponse,
)
```

Methods:

- <code title="get /deltas/flat/{particle_patient_id}">client.deltas.<a href="./src/particle_sdk/resources/deltas.py">collect_flat_datasets</a>(particle_patient_id, \*\*<a href="src/particle_sdk/types/delta_collect_flat_datasets_params.py">params</a>) -> <a href="./src/particle_sdk/types/delta_collect_flat_datasets_response.py">DeltaCollectFlatDatasetsResponse</a></code>
- <code title="get /deltas/flat/{particle_patient_id}/{resource_type}/{resource_id}">client.deltas.<a href="./src/particle_sdk/resources/deltas.py">retrieve_resource</a>(resource_id, \*, particle_patient_id, resource_type) -> <a href="./src/particle_sdk/types/delta_retrieve_resource_response.py">DeltaRetrieveResourceResponse</a></code>
- <code title="get /deltas/{particle_patient_id}">client.deltas.<a href="./src/particle_sdk/resources/deltas.py">retrieve_status</a>(particle_patient_id) -> <a href="./src/particle_sdk/types/query.py">Query</a></code>
- <code title="post /deltas">client.deltas.<a href="./src/particle_sdk/resources/deltas.py">submit</a>(\*\*<a href="src/particle_sdk/types/delta_submit_params.py">params</a>) -> <a href="./src/particle_sdk/types/delta_submit_response.py">DeltaSubmitResponse</a></code>
