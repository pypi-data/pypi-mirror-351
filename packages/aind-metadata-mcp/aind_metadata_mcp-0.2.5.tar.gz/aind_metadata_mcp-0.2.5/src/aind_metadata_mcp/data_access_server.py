
from mcp.server.fastmcp import FastMCP

from aind_data_access_api.document_db import MetadataDbClient
from pathlib import Path


from aind_metadata_mcp.schema_context_retriever import SchemaContextRetriever
from typing import Literal

mcp = FastMCP("aind_data_access")

def setup_mongodb_client():
    """Set up and return the MongoDB client"""
    API_GATEWAY_HOST = "api.allenneuraldynamics.org"
    DATABASE = "metadata_index"
    COLLECTION = "data_assets"
    
    return MetadataDbClient(
        host=API_GATEWAY_HOST,
        database=DATABASE,
        collection=COLLECTION,
    )

@mcp.tool()
def get_records(filter: dict = {}, 
                projection: dict = {},
                limit: int = 5) -> dict:
    """
    Retrieves documents from MongoDB database using simple filters
    and projections.
    For additional context on how to create filters and projections, 
    use the retrieve_schema_context tool.

    WHEN TO USE THIS FUNCTION:
    - For straightforward document retrieval based on specific criteria
    - When you need only a subset of fields from documents
    - When the query logic doesn't require multi-stage processing
    - For better performance with simpler queries

    NOT RECOMMENDED FOR:
    - Complex data transformations (use aggregation_retrieval instead)
    - Grouping operations or calculations across documents
    - Joining or relating data across collections

    Parameters
    ----------
    filter : dict
        MongoDB query filter to narrow down the documents to retrieve.
        Example: {"subject.sex": "Male"}
        If empty dict object, returns all documents.

    projection : dict
        Fields to include or exclude in the returned documents.
        Use 1 to include a field, 0 to exclude.
        Example: {"subject.genotype": 1, "_id": 0}
        will return only the genotype field.
        If empty dict object, returns all documents.

    limit: int
        Limit retrievals to a reasonable number, try to not exceed 100

    Returns
    -------
    list
        List of dictionary objects representing the matching documents.
        Each dictionary contains the requested fields based on the projection.

    """

    docdb_api_client = setup_mongodb_client()

    try:
        records = docdb_api_client.retrieve_docdb_records(
            filter_query=filter, projection=projection, limit=limit
        )
        return records

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message

@mcp.tool()
def aggregation_retrieval(agg_pipeline:list):
    """
    Executes a MongoDB aggregation pipeline for complex data transformations
    and analysis.

    For additional context on how to create filters and projections, 
    use the retrieve_schema_context tool.
    
    WHEN TO USE THIS FUNCTION:
    - When you need to perform multi-stage data processing operations
    - For complex queries requiring grouping, filtering, sorting in sequence
    - When you need to calculate aggregated values (sums, averages, counts)
    - For data transformation operations that can't be done with simple queries

    NOT RECOMMENDED FOR:
    - Simple document retrieval (use get_records instead)
    - When you only need to filter data without transformations
    
    Parameters
    ----------
    agg_pipeline : list
        A list of dictionary objects representing MongoDB aggregation stages.
        Each stage should be a valid MongoDB aggregation operator.
        Common stages include: $match, $project, $group, $sort, $unwind.
        
    Returns
    -------
    list
        Returns a list of documents resulting from the aggregation pipeline.
        If an error occurs, returns an error message string describing
        the exception.
    
    Notes
    -----
    - Include a $project stage early in the pipeline to reduce data transfer
    - Avoid using $map operator in $project stages as it requires array inputs
    """
    docdb_api_client = setup_mongodb_client()
    
    try:
        result = docdb_api_client.aggregate_docdb_records(
            pipeline=agg_pipeline
        )
        return result

    except Exception as ex:
        template = "An exception of type {0} occurred. Arguments:\n{1!r}"
        message = template.format(type(ex).__name__, ex.args)
        return message
    
# @mcp.tool()
# async def retrieve_vectorized_assets(query: str, query_filter: dict):
#     """
#     WHEN TO USE THIS FUNCTION: 
#     - ONLY use for queries that mention a subject id or name (structured like experiment modality_subject_date)
#     - Simple field lookups on specific records (e.g., "What's the genotype of subject 678543?")
#     - Semantic similarity searches requiring understanding of content
#     - Complex questions about specific records needing contextual understanding
#     - Timeline reconstructions for individual subjects/experiments
#     - Questions that benefit from embedding-based similarity rather than exact matching
#     - Limited to top 5 most relevant documents, so use when precision > recall

#     NOT RECOMMENDED FOR:
#     - Any count based questions
#     - Retrievals that require a numerical answer

#     query filter instructions:
#     Step 1: Create Match Filter (MANDATORY)
#     Analyze the query to identify filterable fields (subject_id, name)
#     Construct a valid MongoDB $match stage as a Python dictionary
#     Format it as: {"$match": {...filter conditions...}}
#     NEVER skip this step - every response must include a match filter
#     Step 2: Determine Document Count
#     Only after creating a match filter, determine how many documents to retrieve:

#     Field Recognition Guidelines:
#     Subject IDs: Any 6-digit number (like 678905, 654326) should be treated as a subject_id

#     Even if the query refers to "mouse 657812" rather than "subject 657812"
#     Example filter: {"$match": {"subject_id": "657812"}}
#     Key Fields to Watch For:

#     subject_id (highest priority for filtering)
#     name (contains ONLY experiment modality, subject ID, and date)
#     Query: "Show me all SmartSPIM data from February 2023" Filter: {"$match": {"name": {"$regex": "SmartSPIM.*2023-02"}}}

#     Query: "Tell me about mouse 608551's single-plane-ophys experiments" 
#     Filter: {"$match": {"subject_id": "608551"}}
#     """
#     retriever = DocDBRetriever(k=3)
#     documents = await retriever.aget_relevant_documents(
#         query=query, query_filter=query_filter
#     )
#     return documents

@mcp.tool()
async def retrieve_schema_context(query: str, 
                                  collection: Literal[
                                      "data_schema_fields_index",
                                      "data_schema_defs_index",
                                      "data_schema_core_index"
                                  ]):
    """
    collection - 
    1. data_schema_fields_index: 
    - Search for information about schema properties, field definitions, data types, validation rules, and 
    field-specific requirements. 
    - Use when you need to understand what fields are available or how specific properties work.
    - Use cases:
        - Building field selections (`$project`)
        - Understanding field types for queries
        - Checking required vs optional fields
        - Field-specific validation rules
    2. data_schema_defs_index: 
    - Search for schema definitions, enums, nested object structures, and reusable components. 
    - Use when you need to understand data models, allowed values, or complex nested structures.
    - Use cases:
        - Working with enum values (`$match` with specific values)
        - Understanding nested object structures
        - Looking up allowed values for fields
        - Complex data type definitions
    3. data_schema_core_index: 
    - Search for Python implementation details, validation logic, business rules, and model relationships. 
    - Use when you need to understand how validation works or implementation-specific context.
    query instructions:
    - Simplify the user's query for the relevant collection, keep in mind that this query will be used to perform vector search against a database
    - Use cases:
        - Understanding business logic validation
        - Model relationships and dependencies
        - Implementation-specific constraints
        - Custom validation rules

    **Process:** Always search the most relevant vector store first, then use additional stores if you need more context.
    Hierarchical Search Strategy:
    1. **Primary Search**: Use the vector store most relevant to your query type
    2. **Context Search**: If needed, search related vector stores for additional context
    3. **Validation Search**: Check core vector store for any business rules that might affect your query

    Example: For a query filtering by "sex" field:
    1. Search Properties → understand "sex" field structure  
    2. Search Defs → get allowed values (Male/Female)
    3. Search Core → check any validation rules
    4. Query Type Mapping
    Provide explicit mappings:

    Query Intent → Vector Store Priority:

    **Field Existence/Types**: Properties → Core → Defs
    **Value Filtering**: Defs → Properties → Core  
    **Aggregation Pipelines**: Properties → Defs → Core
    **Validation Context**: Core → Properties → Defs
    **Schema Structure**: Defs → Properties → Core

    """
    retriever = SchemaContextRetriever(k=4, collection = collection)
    documents = await retriever._aget_relevant_documents(query=query)
    return documents

@mcp.resource("resource://aind_api")
def get_aind_data_access_api() -> str:
    """
    Get context on how to use the AIND data access api to show users how to wrap
    tool calls 
    """
    resource_path = Path(__file__).parent / "resources" / "aind_api_prompt.txt"
    with open(resource_path, 'r') as file:
        file_content = file.read()
    return file_content

@mcp.resource("resource://high_level_schema")
def get_high_level_schema() -> str:
    """
    Get context of high level data schema.
    This schema only has the parent nodes of each field and doesn't account for nesting.
    Useful for getting context on how to construct simple queries
    """
    resource_path = Path(__file__).parent / "resources" / "high_level_schema.txt"
    with open(resource_path, 'r') as file:
        file_content = file.read()
    return file_content


def main():
    """Entry point for the MCP server"""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()
