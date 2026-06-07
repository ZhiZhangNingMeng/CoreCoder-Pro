"""Knowledge base retrieval tool."""

from .base import Tool
from ..rag_storage import get_collection


class KnowledgeSearchTool(Tool):
    name = "knowledge_search"
    description = (
        "Use this tool when you need to query the exclusive knowledge base or local documents. "
        "Pass a keyword to return the most relevant matching text snippets."
    )
    parameters = {
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "The keyword or core question to search in the knowledge base."
            }
        },
        "required": ["query"]
    }

    def execute(self, query: str) -> str:
        try:
            collection = get_collection()
            results = collection.query(
                query_texts=[query],
                n_results=3  # Retrieve the top 3 most relevant text chunks
            )

            if not results['documents'] or not results['documents'][0]:
                return "No relevant content found in the knowledge base for this query."

            retrieved_chunks = results['documents'][0]
            sources = results['metadatas'][0] if 'metadatas' in results else []

            formatted_result = f"Retrieval results for '{query}':\n\n"
            for i, (chunk, meta) in enumerate(zip(retrieved_chunks, sources)):
                source_name = meta.get('source', 'Unknown')
                formatted_result += f"--- Snippet {i + 1} (Source: {source_name}) ---\n{chunk}\n\n"

            return formatted_result

        except Exception as e:
            return f"Error occurred while searching the knowledge base: {str(e)}"