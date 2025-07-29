from fastmcp import FastMCP
from typing import List, Dict, Any
from typing import Annotated
from pydantic import Field
import json
import os

from memory_plus.memory_protocol import MemoryProtocol
from memory_plus.utils import get_app_dir

# Create memory protocol instance
memory_protocol = MemoryProtocol()

# Load user-defined memory preferences from environment
memory_preferences = os.getenv('MEMORY_PLUS_PREFERENCES', '')
if memory_preferences:
    memory_preferences_text = f"""
    
    9. User-Defined Memory Preferences:
       {memory_preferences}
       
    These preferences dictate what kinds of information should be prioritized for recording.
    They are the most important directive for memory handling and must be strictly followed at all times — even above general heuristics.
    When in doubt, defer to these preferences.
    """
else:
    memory_preferences_text = ""

# Initialize FastMCP with memory protocol
mcp = FastMCP(
    name="memory_server",
    instructions=f"""
    General Instructions: You should continuously record user preferences, background facts, and recurring topics as memories, ideally during every interaction — without requiring explicit user prompts. You should also proactively retrieve relevant memories to personalize responses. 
    For example, if the user says "use my favourite programming language to write a program", you should retrieve their favourite programming language from memory instead of asking again or denying the request.

    1. User Identification: Use `default_user` as the user identifier for all interactions.

    2. Category Initialization: Load memory categories from `resource://recorded_memory_categories`.

    3. Memory Retrieval: Indicate with `Remembering...` before calling `retrieve()` or `recent()` as needed.

    4. Active Listening: Pay attention to user-provided information such as identity, preferences, goals, and skills.

    5. Memory Recording Workflow:
       - First, check for similar memories using `retrieve(content, top_k)`.
       - If a similar memory exists, update it with `update(memory_id, new_content, metadata)`.
       - If not, record a new memory using `record(content, metadata)`.
       - Always use existing categories from the manifest in the `metadata`.
       - Ensure `resource://recorded_memory_categories` is loaded before recording.

    6. Metadata Format:
       For all memory-related operations requiring metadata, use the following structure:
       {{
           'source': string // Source identifier (e.g., "Cursor", "Cline", "Claude Desktop"). For `import_file`, use the file path.
           'category': string // Memory classification (e.g., "personal_detail", "preference").
           'tags': [string] // Keywords for filtering (e.g., ["coding_style", "favorite_music"]).
           'intent': string // Purpose/context of the memory (e.g., "reminder", "setup_preference").
           'privacy_level': string // Level of sensitivity (e.g., "public", "private", "sensitive").
           'previous_versions': [string] // List of prior versions (only required for `update`).
       }}

    7. Tool Usage:
       - Begin by loading `resource://recorded_memory_categories` to reference valid categories.
       - Use `retrieve()` to avoid redundant entries.
       - Use `recent()` when recency/context matters.
       - Use `record()` for new entries and `update()` for existing ones.
       - Use `visualize()` sparingly for memory overviews or debugging.
       - Use `delete()` only with explicit user confirmation.
       - Use `import_file()` for bulk memory imports.
       - Use `export()` to save and share memory contents externally.

    8. Visualization: Provide memory visualizations upon request or for diagnostic/debugging purposes.

    All operations should be performed seamlessly to enhance personalization without requiring explicit user intervention.
    """
)



@mcp.resource("resource://recorded_memory_categories")
def get_recorded_memory_categories() -> str:
    """
    Provides overview of existing memory domains to determine appropriate retrieval context.
    Essential for understanding what categories of memories exist before recording and retrieving new memories.
    Returns JSON mapping each category to its list of known tags.
    """
    return json.dumps(memory_protocol.load_recorded_categories())

@mcp.tool("record")
def record_memory(
    content: Annotated[str, Field(description="User's exact words or close paraphrase to preserve intent and tone")],
    metadata: Annotated[Dict[str, Any], Field(description="Metadata dict following format in metadata instructed format")] = None,
) -> List[int]:
    """
    Records new user-specific information when details are detected.
    Automatically invoked for preferences, background facts, or recurring topics.
    Should be preceded by retrieve() call to check for similar existing memories.
    You should also provide the metadata to the user's memory.
    Returns list of newly assigned memory IDs.
    """
    if metadata:
        memory_protocol.update_recorded_categories(metadata)
    return memory_protocol.record_memory(content, metadata)

@mcp.tool("retrieve")
def retrieve_memory(
    query: Annotated[str, Field(description="Natural language query to search memory store")],
    top_k: Annotated[int, Field(description="Max number of entries to return", ge=5, le=100)] = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve semantically similar memories based on natural language query.
    Essential for contextual awareness and checking for duplicates before recording.
    Automatically called when additional context needed for better responses.
    Returns memory entries with content and metadata, ordered by semantic relevance.
    Check recorded_memory_categories first to understand available memory domains.
    """
    return memory_protocol.retrieve_memory(query, top_k)

@mcp.tool("recent")
def get_recent_memories(
    limit: Annotated[int, Field(description="Max number of recent memories to retrieve", ge=1, le=100)] = 5
) -> List[Dict[str, Any]]:
    """
    Retrieve most recently recorded memory entries for temporal context.
    Useful when composing responses that benefit from fresh context.
    Automatically called when referencing recent user statements or preferences.
    Returns memory entries ordered from newest to oldest with full metadata.
    """
    return memory_protocol.get_recent_memories(limit)



@mcp.tool("update")
def update_memory(
    memory_id: Annotated[int, Field(description="ID of memory to update")],
    new_content: Annotated[str, Field(description="New content to replace existing memory")],
    metadata: Annotated[Dict[str, Any], Field(description="Updated metadata dict following format in metadata instructed format")] = None,
) -> bool:
    """
    Update existing memory with new content and metadata when similar memory found.
    Use instead of record() when retrieve() finds high similarity to existing memory.
    Maintains memory history while updating with latest information.
    The metadata must include the 'previous_versions' field with a list of previous versions of the memory.
    Returns True if update successful, raises exception otherwise.
    """
    return memory_protocol.update_memory(memory_id, new_content, metadata)

@mcp.tool("visualize")
def visualize_memories() -> str:
    """
    Create interactive visualization of memory embeddings showing semantic clusters and trends.
    Highlights relationships between different preferences and user details over time.
    Use sparingly for memory overview or debugging, not for routine operations.
    Automatically opens a hosted interactive visualization dashboard.
    """
    return memory_protocol.visualize_memories()

@mcp.tool("delete")
def delete_memory(
    memory_id: Annotated[int, Field(description="ID of memory to delete")],
    confirmation: Annotated[bool, Field(description="Must be True to confirm deletion")] = False
) -> bool:
    """
    Delete specific memory by ID with explicit confirmation required.
    Only use when user explicitly requests memory deletion.
    Should retrieve and show memory content to user before deletion.
    Requires confirmation=True parameter to proceed with deletion.
    Returns True if deletion successful, raises exception otherwise.
    """
    if not confirmation:
        raise ValueError("Deletion requires explicit confirmation")
    return memory_protocol.delete_memory(memory_id)

@mcp.tool("import_file")
def import_file(
    file_path: Annotated[str, Field(description="Path to file to import")],
    metadata: Annotated[Dict[str, Any], Field(description="Metadata dict following format in metadata instructed format")] = None
) -> List[int]:
    """
    Import file contents into memory database.
    File must exist and be readable (txt, md, etc.).
    Returns list of memory IDs for all imported chunks.
    """
    return memory_protocol.import_file(file_path, metadata)

@mcp.tool("export")
def export_memories(
    export_path: Annotated[str, Field(description="Optional export file path")] = None,
    limit: Annotated[int, Field(description="Max records to export", ge=1, le=10000)] = 1000
) -> str:
    """
    Export memory records to JSON file for external viewing and analysis.
    Saves up to specified limit of memory records with full metadata.
    Exported file can be viewed at https://memory-plus-viewer.vercel.app/, show this to the user!
    Defaults to app_dir/qdrant_export.json if no path specified.
    Returns the file path where exported JSON was saved.
    """
    return memory_protocol.export_memories(export_path, limit)

@mcp.prompt("Save Chat History")
def save_chat() -> str:
    """
    Analyze ongoing chat to identify and persist important user-specific information.
    Extracts stable preferences, background facts, and recurring topics for memory storage.
    """
    return "Based on the chat history, identify some of the important things and save them."

@mcp.prompt("Visualize (plot)")
def visualize_memories() -> str:
    """
    Create interactive visualization of user memory embeddings showing semantic relationships.
    Displays clusters and temporal trends among stored memories for analysis.
    """
    return "Create and return a URL or embedded HTML snippet for an interactive visualization of user memory embeddings."

def main():
    """Entry point for the memory server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Memory Server using FastMCP")
    parser.add_argument("--host", default="localhost", help="Host to run the server on")
    parser.add_argument("--port", type=int, default=8000, help="Port to run the server on")
    parser.add_argument("--log-level", default="ERROR", choices=["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"],
                      help="Logging level")
    
    args = parser.parse_args()
    
    try:
        memory_protocol.initialize()
        
        # Update FastMCP configuration
        mcp.host = args.host
        mcp.port = args.port
        mcp.log_level = args.log_level
        
        mcp.run()
        # print('memory server started')
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == "__main__":
    main() 