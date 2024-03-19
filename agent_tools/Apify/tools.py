from langchain.tools import BaseTool
from langchain_community.document_loaders import ApifyDatasetLoader
from langchain_core.documents import Document
from pydantic import BaseModel, Field
from dotenv import load_dotenv
import os


load_dotenv()

apify_api_token = os.getenv("APIFY_API_TOKEN")
if not apify_api_token:
    raise ValueError("Apify API token not found. Please set the APIFY_API_TOKEN environment variable.")

class CrawlInput(BaseModel):
    dataset_id: str = Field(description="The ID of the dataset on the Apify platform.")

class CrawlOutput(BaseModel):
    response_code: str = Field(description="Response code for the crawl.")
    crawled_data: list = Field(description="List of extracted data from crawled pages.")

def dataset_mapping_function(dataset_item: dict) -> Document:
    """Convert an Apify dataset item to a Document."""
    return Document(
        page_content=dataset_item.get("text", ""),
        metadata={"source": dataset_item.get("url")}
    )

def perform_crawl(dataset_id: str) -> CrawlOutput:
    """Load and process a dataset from Apify using the provided dataset ID."""
    from apify_client import ApifyClient

    # Initialize the ApifyClient with the API token
    apify_client = ApifyClient(apify_api_token)

    loader = ApifyDatasetLoader(
        apify_client=apify_client,
        dataset_id=dataset_id,
        dataset_mapping_function=dataset_mapping_function
    )
    documents = loader.load()

    # Process the documents as needed
    crawled_data = [{
        "url": doc.metadata["source"],
        "content": doc.page_content
    } for doc in documents]

    return CrawlOutput(
        response_code="success",
        crawled_data=crawled_data
    )

class CrawlWebsiteTool(BaseTool):
    name = "perform_crawl"
    description = "Tool for loading and processing datasets from Apify using an API token."
    args_schema = CrawlInput
    result_schema = CrawlOutput

    def _run(self, inputs: dict) -> CrawlOutput:
        # Validate inputs
        if not isinstance(inputs, dict) or 'dataset_id' not in inputs:
            raise ValueError("Invalid inputs for CrawlWebsiteTool. 'dataset_id' is required.")
        
        dataset_id = inputs['dataset_id']
        return perform_crawl(dataset_id)
