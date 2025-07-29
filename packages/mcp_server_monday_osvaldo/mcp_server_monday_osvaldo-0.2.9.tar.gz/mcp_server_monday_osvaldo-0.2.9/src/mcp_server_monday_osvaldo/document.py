from __future__ import annotations

import json
from typing import Optional

from mcp import types
from monday import MondayClient

from mcp_server_monday.constants import MONDAY_WORKSPACE_URL


async def handle_monday_get_item_files(
    itemId: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    """Get files attached to a specific item in Monday.com"""

    query = f"""
    query {{
        items (ids: {itemId}) {{
            name
            column_values {{
                id
                title
                type
                value
                text
            }}
            assets {{
                id
                name
                url
                public_url
                file_extension
                file_size
                created_at
                uploaded_by {{
                    id
                    name
                }}
            }}
        }}
    }}
    """

    response = monday_client.custom._query(query)

    if not response or "data" not in response or not response["data"]["items"]:
        return [
            types.TextContent(type="text", text=f"No items found with ID {itemId}.")
        ]

    item = response["data"]["items"][0]

    # Check for files in column values (like file columns)
    file_columns = []
    for column in item.get("column_values", []):
        if column.get("type") == "file" and column.get("value"):
            try:
                # File column values are stored as JSON strings
                file_data = json.loads(column.get("value", "{}"))
                if "files" in file_data:
                    for file in file_data["files"]:
                        file_info = f"File Name: {file.get('name')}\n"
                        file_info += f"URL: {file.get('url')}\n"
                        file_info += f"Column: {column.get('title')}\n\n"
                        file_columns.append(file_info)
            except (json.JSONDecodeError, KeyError):
                pass

    # Check for files in assets
    asset_files = []
    for asset in item.get("assets", []):
        asset_info = f"Asset Name: {asset.get('name')}\n"
        asset_info += f"URL: {asset.get('url')}\n"
        if asset.get("public_url"):
            asset_info += f"Public URL: {asset.get('public_url')}\n"
        asset_info += f"Type: {asset.get('file_extension')}\n"
        asset_info += f"Size: {asset.get('file_size')} bytes\n"
        asset_info += f"Created: {asset.get('created_at')}\n\n"
        asset_files.append(asset_info)

    # Combine results
    if not file_columns and not asset_files:
        return [
            types.TextContent(type="text", text=f"No files found for item {itemId}.")
        ]

    result = f"Files attached to item {itemId} ({item.get('name')}):\n\n"

    if file_columns:
        result += "FILES IN COLUMNS:\n" + "".join(file_columns) + "\n"

    if asset_files:
        result += "ASSETS:\n" + "".join(asset_files)

    return [types.TextContent(type="text", text=result)]


async def handle_monday_get_update_files(
    updateId: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    """Get files attached to a specific update in Monday.com"""

    query = f"""
    query {{
        updates (ids: {updateId}) {{
            id
            body
            created_at
            assets {{
                id
                name
                url
                public_url
                file_extension
                file_size
                created_at
            }}
        }}
    }}
    """

    response = monday_client.custom._query(query)

    if not response or "data" not in response or not response["data"]["updates"]:
        return [
            types.TextContent(type="text", text=f"No update found with ID {updateId}.")
        ]

    update = response["data"]["updates"][0]

    # Check for files in assets
    asset_files = []
    for asset in update.get("assets", []):
        asset_info = f"Asset Name: {asset.get('name')}\n"
        asset_info += f"URL: {asset.get('url')}\n"
        if asset.get("public_url"):
            asset_info += f"Public URL: {asset.get('public_url')}\n"
        asset_info += f"Type: {asset.get('file_extension')}\n"
        asset_info += f"Size: {asset.get('file_size')} bytes\n"
        asset_info += f"Created: {asset.get('created_at')}\n\n"
        asset_files.append(asset_info)

    if not asset_files:
        return [
            types.TextContent(
                type="text", text=f"No files found for update {updateId}."
            )
        ]

    result = f"Files attached to update {updateId}:\n\n"
    result += "".join(asset_files)

    return [types.TextContent(type="text", text=result)]


async def handle_monday_get_docs(
    monday_client: MondayClient, limit: int
) -> list[types.TextContent]:
    """Get a list of documents from Monday.com, optionally filtered by folder"""

    # Add folder filter if provided

    query = f"""
    query {{
        docs (limit: {limit}) {{
            id
            name
            created_at
            workspace_id
            doc_folder_id
            created_by {{
                id
                name
            }}
        }}
    }}
    """

    response = monday_client.custom._query(query)

    if not response or "data" not in response or not response["data"]["docs"]:
        return [types.TextContent(type="text", text="No documents found.")]

    docs = response["data"]["docs"]

    formatted_docs = []
    for doc in docs:
        doc_text = f"Document ID: {doc['id']}\n"
        doc_text += f"Name: {doc['name']}\n"
        doc_text += f"Created: {doc['created_at']}\n"
        doc_text += f"Workspace ID: {doc['workspace_id']}\n"
        doc_text += f"Folder ID: {doc.get('doc_folder_id', 'None')}\n"
        doc_text += f"Created by: {doc['created_by']['name']} (ID: {doc['created_by']['id']})\n\n-----\\n\n"
        formatted_docs.append(doc_text)

    return [
        types.TextContent(type="text", text=f"Documents:\n\n{''.join(formatted_docs)}")
    ]


async def handle_monday_get_doc_content(
    doc_id: str,
    monday_client: MondayClient,
) -> list[types.TextContent]:
    """Get the content (blocks) of a specific document by ID"""

    query = f"""
    query {{
        docs (ids: {doc_id}) {{
            id
            name
            blocks {{
                id
                type
                content
            }}
        }}
    }}
    """

    response = monday_client.custom._query(query)

    if (
        not response
        or "data" not in response
        or not response["data"].get("docs")
        or not response["data"]["docs"]
    ):
        return [
            types.TextContent(type="text", text=f"Document with ID {doc_id} not found.")
        ]

    doc = response["data"]["docs"][0]
    blocks = doc.get("blocks", [])
    if not blocks:
        return [
            types.TextContent(
                type="text",
                text=f"Document ID: {doc['id']}\nName: {doc['name']}\n\nNo content blocks found.",
            )
        ]

    formatted_blocks = []
    for block in blocks:
        formatted_blocks.append(
            f"Block ID: {block['id']}\nType: {block['type']}\nContent: {block['content']}\n"
        )

    return [
        types.TextContent(
            type="text",
            text=f"Document ID: {doc['id']}\nName: {doc['name']}\n\nBlocks:\n\n{''.join(formatted_blocks)}",
        )
    ]


async def handle_monday_create_doc(
    monday_client: MondayClient,
    title: str,
    workspace_id: Optional[int] = None,
    board_id: Optional[int] = None,
    kind: Optional[str] = None,  # For workspace
    column_id: Optional[str] = None,  # For board
    item_id: Optional[int] = None,  # For board
) -> list[types.TextContent]:
    """Create a new document in Monday.com. Specify either workspace_id (with kind, name) or board_id (with column_id, item_id) as the location."""

    # Build location argument
    if workspace_id:
        if not kind:
            return [
                types.TextContent(
                    type="text", text="'kind' is required when using workspace_id."
                )
            ]
        location = f'location: {{workspace: {{ workspace_id: {workspace_id}, name: "{title}", kind: {kind} }} }}'
    elif board_id:
        if not column_id or not item_id:
            return [
                types.TextContent(
                    type="text",
                    text="'column_id' and 'item_id' are required when using board_id.",
                )
            ]
        location = f'location: {{board: {{ board_id: {board_id}, column_id: "{column_id}", item_id: {item_id} }} }}'
    else:
        return [
            types.TextContent(
                type="text",
                text="You must provide either workspace_id or board_id to create a document.",
            )
        ]

    mutation = f"""
    mutation {{
        create_doc (
            {location}
        ) {{
            id
        }}
    }}
    """

    try:
        response = monday_client.custom._query(mutation)

        if (
            not response
            or "data" not in response
            or not response["data"].get("create_doc")
        ):
            return [types.TextContent(type="text", text="Failed to create document.")]

        created_doc = response["data"]["create_doc"]
        doc_url = f"{MONDAY_WORKSPACE_URL}/docs/{created_doc['id']}"

        return [
            types.TextContent(
                type="text",
                text=f"Document created successfully!\nTitle: {title}\nID: {created_doc['id']}\nURL: {doc_url}",
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=f"An error occurred while creating the document: {str(e)}. Response: {json.dumps(response)}",
            )
        ]


async def handle_monday_add_doc_block(
    doc_id: str,
    block_type: str,
    content: str,
    monday_client: MondayClient,
    after_block_id: Optional[str] = None,
) -> list[types.TextContent]:
    """
    Add a block to a document

    Block types include: normal_text, bullet_list, numbered_list, heading, divider, etc.
    """

    # Escape quotes in content
    escaped_content = content.replace('"', '\\"')

    # Build after_block param
    after_block_param = f", after_block_id: {after_block_id}" if after_block_id else ""

    # Build mutation query
    mutation = f"""
    mutation {{
        add_doc_block (
            doc_id: {doc_id},
            type: {block_type},
            content: "{escaped_content}"{after_block_param}
        ) {{
            id
            type
        }}
    }}
    """

    response = monday_client.custom._query(mutation)

    if not response or "data" not in response or not response["data"]["add_doc_block"]:
        return [types.TextContent(type="text", text="Failed to add block to document.")]

    created_block = response["data"]["add_doc_block"]

    return [
        types.TextContent(
            type="text",
            text=f"Block added successfully!\nID: {created_block['id']}\nType: {created_block['type']}",
        )
    ]
