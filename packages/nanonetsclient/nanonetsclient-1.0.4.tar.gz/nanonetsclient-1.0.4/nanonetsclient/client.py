import requests
from typing import Any, Dict, List, Optional

class NanonetsClient:
    def __init__(self, api_key: str, base_url: str = 'https://app.nanonets.com/api/v4'):
        self.api_key = api_key
        self.base_url = base_url
        self.auth = (api_key, '')

    class Workflows:
        def __init__(self, client: 'NanonetsClient'):
            self.client = client

        # Workflow Management
        def list(self) -> list:
            """List all workflows in the account."""
            url = f"{self.client.base_url}/workflows"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json().get('workflows', [])

        def get(self, workflow_id: str) -> dict:
            """Get a workflow by ID."""
            url = f"{self.client.base_url}/workflows/{workflow_id}"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def get_types(self) -> list:
            """Get available workflow types."""
            url = f"{self.client.base_url}/workflow_types"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json().get('workflow_types', [])

        def create(self, description: str, workflow_type: str = "") -> dict:
            """Create a new workflow."""
            url = f"{self.client.base_url}/workflows"
            payload = {"description": description, "workflow_type": workflow_type}
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def set_fields(self, workflow_id: str, fields: list, table_headers: list = None) -> dict:
            """Set fields and table headers for a workflow."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/fields"
            payload = {"fields": fields}
            if table_headers is not None:
                payload["table_headers"] = table_headers
            response = requests.put(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def update_field(self, workflow_id: str, field_id: str, name: str) -> dict:
            """Update a field or table header name."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/fields/{field_id}"
            payload = {"name": name}
            response = requests.patch(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def delete_field(self, workflow_id: str, field_id: str) -> dict:
            """Delete a field or table header from a workflow."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/fields/{field_id}"
            response = requests.delete(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def update_metadata(self, workflow_id: str, description: str) -> dict:
            """Update workflow metadata (description)."""
            url = f"{self.client.base_url}/workflows/{workflow_id}"
            payload = {"description": description}
            response = requests.patch(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def update_settings(self, workflow_id: str, table_capture: bool) -> dict:
            """Update workflow settings (table_capture)."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/settings"
            payload = {"table_capture": table_capture}
            response = requests.patch(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        # Document Processing
        def upload_document(self, workflow_id: str, file_path: Optional[str] = None, document_url: Optional[str] = None, async_mode: bool = False, metadata: Optional[Dict[str, Any]] = None) -> Dict:
            """Upload a document for processing (file or URL)."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents"
            headers = {}
            data = {'async': str(async_mode).lower()}
            if metadata:
                data['metadata'] = metadata if isinstance(metadata, str) else str(metadata)
            if file_path:
                files = {'file': open(file_path, 'rb')}
                response = requests.post(url, data=data, files=files, auth=self.client.auth, headers=headers)
            elif document_url:
                json_data = {'document_url': document_url, 'async': async_mode}
                if metadata:
                    json_data['metadata'] = metadata
                response = requests.post(url, json=json_data, auth=self.client.auth, headers=headers)
            else:
                raise ValueError('Either file_path or document_url must be provided')
            response.raise_for_status()
            return response.json()

        def get_document(self, workflow_id: str, document_id: str) -> Dict:
            """Get the processing status and results of a document."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def list_documents(self, workflow_id: str, page: int = 1, limit: int = 10) -> List[Dict]:
            """List all documents in a workflow."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents"
            params = {'page': page, 'limit': limit}
            response = requests.get(url, params=params, auth=self.client.auth)
            response.raise_for_status()
            return response.json().get('documents', [])

        def delete_document(self, workflow_id: str, document_id: str) -> Dict:
            """Delete a document from the workflow."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}"
            response = requests.delete(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def get_document_fields(self, workflow_id: str, document_id: str) -> Dict:
            """Get all extracted fields from a document."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/fields"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def get_document_tables(self, workflow_id: str, document_id: str) -> Dict:
            """Get all extracted tables from a document."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/tables"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def get_document_original_file(self, workflow_id: str, document_id: str) -> bytes:
            """Download the original document file."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/original"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.content

        def get_page_data(self, workflow_id: str, document_id: str, page_id: str) -> Dict:
            """Get the processing results for a specific page of a document."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}"
            response = requests.get(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        # Moderation: Field Management
        def update_field_value(self, workflow_id: str, document_id: str, page_id: str, field_data_id: str, value: Any) -> Dict:
            """Update a specific field value in a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/fields/{field_data_id}"
            payload = {'value': value}
            response = requests.patch(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def add_field_value(self, workflow_id: str, document_id: str, page_id: str, field_name: str, value: Any, bbox: List[int], confidence: float, verification_status: str, verification_message: str = "") -> Dict:
            """Add a new field value to a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/fields"
            payload = {
                'field_name': field_name,
                'value': value,
                'bbox': bbox,
                'confidence': confidence,
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def delete_field_value(self, workflow_id: str, document_id: str, page_id: str, field_data_id: str) -> Dict:
            """Delete a field value from a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/fields/{field_data_id}"
            response = requests.delete(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        # Moderation: Table Management
        def add_table(self, workflow_id: str, document_id: str, page_id: str, bbox: List[int], headers: List[str], verification_status: str, verification_message: str, cells: List[Dict]) -> Dict:
            """Add a new table to a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables"
            payload = {
                'bbox': bbox,
                'headers': headers,
                'verification_status': verification_status,
                'verification_message': verification_message,
                'cells': cells
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def delete_table(self, workflow_id: str, document_id: str, page_id: str, table_id: str) -> Dict:
            """Delete a table from a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}"
            response = requests.delete(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def update_table_cell(self, workflow_id: str, document_id: str, page_id: str, table_id: str, cell_id: str, value: Any) -> Dict:
            """Update a specific cell in a table."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}/cells/{cell_id}"
            payload = {'value': value}
            response = requests.patch(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def add_table_cell(self, workflow_id: str, document_id: str, page_id: str, table_id: str, row: int, col: int, header: str, text: str, bbox: List[int], verification_status: str, verification_message: str) -> Dict:
            """Add a new cell to a table on a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}/cells"
            payload = {
                'row': row,
                'col': col,
                'header': header,
                'text': text,
                'bbox': bbox,
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def delete_table_cell(self, workflow_id: str, document_id: str, page_id: str, table_id: str, cell_id: str) -> Dict:
            """Delete a cell from a table on a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}/cells/{cell_id}"
            response = requests.delete(url, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        # Moderation: Verification
        def verify_field(self, workflow_id: str, document_id: str, page_id: str, field_data_id: str, verification_status: str, verification_message: str) -> Dict:
            """Verify a field in a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/fields/{field_data_id}/verify"
            payload = {
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def verify_table_cell(self, workflow_id: str, document_id: str, page_id: str, table_id: str, cell_id: str, verification_status: str, verification_message: str) -> Dict:
            """Verify a table cell in a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}/cells/{cell_id}/verify"
            payload = {
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def verify_table(self, workflow_id: str, document_id: str, page_id: str, table_id: str, verification_status: str, verification_message: str) -> Dict:
            """Verify an entire table in a document page."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/pages/{page_id}/tables/{table_id}/verify"
            payload = {
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

        def verify_document(self, workflow_id: str, document_id: str, verification_status: str, verification_message: str) -> Dict:
            """Verify an entire document."""
            url = f"{self.client.base_url}/workflows/{workflow_id}/documents/{document_id}/verify"
            payload = {
                'verification_status': verification_status,
                'verification_message': verification_message
            }
            response = requests.post(url, json=payload, auth=self.client.auth)
            response.raise_for_status()
            return response.json()

    @property
    def workflows(self):
        if not hasattr(self, '_workflows'):
            self._workflows = self.Workflows(self)
        return self._workflows 