"""Retriever wrapper for SmartBucket API."""
from typing import List
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from pydantic import BaseModel, Field, SecretStr
from raindrop import Raindrop, AsyncRaindrop
import os
import json
import uuid

class LangchainSmartBucketRetriever(BaseRetriever, BaseModel):
    """Retriever that uses the SmartBucket API for semantic search.
    
    This retriever uses the SmartBucket API to perform semantic search across your saved documents.
    For more information about the API, see: https://docs.liquidmetal.ai/

    Example:
        .. code-block:: python

            from lm_raindrop_integrations import LangchainSmartBucketRetriever
            
            # Will try to get API key from RAINDROP_API_KEY env var if not provided
            retriever = LangchainSmartBucketRetriever(
                api_key="your-api-key", 
                bucket_name="my-bucket"
            )  
            documents = retriever.invoke("your query")  # Use invoke instead of get_relevant_documents

    Args:
        api_key (str, optional): SmartBucket API key. If not provided, will try to get from RAINDROP_API_KEY env var.
            You can obtain an API key by signing up at https://raindrop.run
        bucket_name (str): Name of the bucket to search in. This is required.
    """

    api_key: SecretStr = Field(default_factory=lambda: SecretStr(os.getenv("RAINDROP_API_KEY") or ""))
    bucket_name: str = Field(..., description="Name of the bucket to search in")
    client: Raindrop = None
    async_client: AsyncRaindrop = None

    def __init__(self, **kwargs):
        # First call the parent class's __init__ to set up the model
        super().__init__(**kwargs)
        
        # Then check for API key
        api_key_value = kwargs.get("api_key")
        if api_key_value:
            # If provided directly, wrap in SecretStr if it's not already
            api_key = api_key_value if isinstance(api_key_value, SecretStr) else SecretStr(api_key_value)
        else:
            api_key = self.api_key
        
        # Get the actual string value for validation and client initialization
        api_key_str = api_key.get_secret_value() if api_key else ""
        if not api_key_str:
            raise ValueError(
                "No API key provided. Please provide an API key either through the constructor "
                "or by setting the RAINDROP_API_KEY environment variable."
            )
        
        # Check for bucket name
        if not self.bucket_name:
            raise ValueError(
                "bucket_name is required. Please provide a bucket name through the constructor."
            )
        
        # Initialize the clients
        self.client = Raindrop(api_key=api_key_str)
        self.async_client = AsyncRaindrop(api_key=api_key_str)

    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Get documents relevant to a query.

        Args:
            query: String to find relevant documents for
            run_manager: Callbacks to track the run

        Returns:
            List of relevant documents
        """
        # Create a unique request ID for this search
        request_id = str(uuid.uuid4())

        # Perform the chunk search with new API format
        response = self.client.query.chunk_search(
            bucket_locations=[{
                "bucket": {
                    "name": self.bucket_name
                }
            }],
            input=query,
            request_id=request_id,
        )

        # Convert results to Documents
        documents = []
        # Handle case where response.results might be None
        results = response.results if response.results is not None else []
        for result in results:
            # Handle the new nested source structure
            source = result.source
            
            # Extract useful information from the source structure
            source_metadata = {}
            if hasattr(source, 'object') and hasattr(source, 'bucket'):
                # New API format with ResultSource object
                source_metadata["object_name"] = source.object
                if hasattr(source.bucket, 'bucket_name'):
                    source_metadata["bucket_name"] = source.bucket.bucket_name
                if hasattr(source.bucket, 'application_name'):
                    source_metadata["application_name"] = source.bucket.application_name
                if hasattr(source.bucket, 'module_id'):
                    source_metadata["module_id"] = source.bucket.module_id
                if hasattr(source.bucket, 'application_version_id'):
                    source_metadata["application_version_id"] = source.bucket.application_version_id
                # Keep the full source for backwards compatibility
                source_metadata["source_raw"] = source
            elif isinstance(source, str):
                # Handle string sources (legacy or JSON)
                try:
                    source_dict = json.loads(source)
                    if "object" in source_dict:
                        source_metadata["object_name"] = source_dict["object"]
                    if "bucket" in source_dict and isinstance(source_dict["bucket"], dict):
                        bucket_info = source_dict["bucket"]
                        source_metadata["bucket_name"] = bucket_info.get("bucketName")
                        source_metadata["application_name"] = bucket_info.get("applicationName")
                        source_metadata["module_id"] = bucket_info.get("moduleId")
                        source_metadata["application_version_id"] = bucket_info.get("applicationVersionId")
                    source_metadata["source_raw"] = source_dict
                except json.JSONDecodeError:
                    source_metadata["source_raw"] = {"raw": source}
            else:
                # Fallback for other formats
                source_metadata["source_raw"] = source

            # Create Document with text content and metadata
            doc = Document(
                page_content=result.text,
                metadata={
                    "chunk_signature": result.chunk_signature,
                    "payload_signature": result.payload_signature,
                    "score": result.score,
                    "type": result.type,
                    "source": source_metadata
                }
            )
            documents.append(doc)

        return documents

    async def _aget_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Asynchronously get documents relevant to a query.
        
        This implementation uses the AsyncSmartBucket client for better performance.

        Args:
            query: String to find relevant documents for
            run_manager: Callbacks to track the run

        Returns:
            List of relevant documents
        """
        # Create a unique request ID for this search
        request_id = str(uuid.uuid4())

        # For now, use the sync client as AsyncRaindrop may not be available
        # TODO: Update when AsyncRaindrop supports query.chunk_search
        response = self.client.query.chunk_search(
            bucket_locations=[{
                "bucket": {
                    "name": self.bucket_name
                }
            }],
            input=query,
            request_id=request_id,
        )

        # Convert results to Documents
        documents = []
        # Handle case where response.results might be None
        results = response.results if response.results is not None else []
        for result in results:
            # Handle the new nested source structure
            source = result.source
            
            # Extract useful information from the source structure
            source_metadata = {}
            if hasattr(source, 'object') and hasattr(source, 'bucket'):
                # New API format with ResultSource object
                source_metadata["object_name"] = source.object
                if hasattr(source.bucket, 'bucket_name'):
                    source_metadata["bucket_name"] = source.bucket.bucket_name
                if hasattr(source.bucket, 'application_name'):
                    source_metadata["application_name"] = source.bucket.application_name
                if hasattr(source.bucket, 'module_id'):
                    source_metadata["module_id"] = source.bucket.module_id
                if hasattr(source.bucket, 'application_version_id'):
                    source_metadata["application_version_id"] = source.bucket.application_version_id
                # Keep the full source for backwards compatibility
                source_metadata["source_raw"] = source
            elif isinstance(source, str):
                # Handle string sources (legacy or JSON)
                try:
                    source_dict = json.loads(source)
                    if "object" in source_dict:
                        source_metadata["object_name"] = source_dict["object"]
                    if "bucket" in source_dict and isinstance(source_dict["bucket"], dict):
                        bucket_info = source_dict["bucket"]
                        source_metadata["bucket_name"] = bucket_info.get("bucketName")
                        source_metadata["application_name"] = bucket_info.get("applicationName")
                        source_metadata["module_id"] = bucket_info.get("moduleId")
                        source_metadata["application_version_id"] = bucket_info.get("applicationVersionId")
                    source_metadata["source_raw"] = source_dict
                except json.JSONDecodeError:
                    source_metadata["source_raw"] = {"raw": source}
            else:
                # Fallback for other formats
                source_metadata["source_raw"] = source

            # Create Document with text content and metadata
            doc = Document(
                page_content=result.text,
                metadata={
                    "chunk_signature": result.chunk_signature,
                    "payload_signature": result.payload_signature,
                    "score": result.score,
                    "type": result.type,
                    "source": source_metadata
                }
            )
            documents.append(doc)

        return documents 