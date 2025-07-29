# LiquidMetal Raindrop Integrations

Python SDK for integrating LiquidMetal's Raindrop API with popular frameworks and tools.

## Installation

Install the base package:

```shell
pip install lm-raindrop-integrations
```

## Supported Integrations

Raindrop SmartBuckets currently supports the following integrations:

### LangChain Retriever

Example usage with LangChain:

```python
from lm_raindrop_integrations import LangchainSmartBucketRetriever
import os

# Initialize the retriever
retriever = LangchainSmartBucketRetriever(api_key="your-api-key")  # or use RAINDROP_API_KEY env var

# Search for documents
results = retriever.invoke("What is machine learning?")

# Process results
for doc in results:
    print(f"Content: {doc.page_content}")
    print(f"Score: {doc.metadata['score']}")
    print(f"Source: {doc.metadata['source']}")
    print("---")
```


