import logging
from enum import Enum
from typing import Sequence, Union

import mcp.types as types
from mcp.server import Server
from monday import MondayClient

from mcp_server_monday.board import (
    handle_monday_create_board,
    handle_monday_create_new_board_group,
    handle_monday_get_board_columns,
    handle_monday_get_board_groups,
    handle_monday_list_boards,
)
from mcp_server_monday.document import (
    handle_monday_add_doc_block,
    handle_monday_create_doc,
    handle_monday_get_doc_content,
    handle_monday_get_docs,
    handle_monday_get_item_files,
    handle_monday_get_update_files,
)
from mcp_server_monday.item import (
    handle_monday_archive_item,
    handle_monday_create_item,
    handle_monday_create_update_on_item,
    handle_monday_delete_item,
    handle_monday_get_item_by_id,
    handle_monday_get_item_updates,
    handle_monday_list_items_in_groups,
    handle_monday_list_subitems_in_items,
    handle_monday_move_item_to_group,
    handle_monday_update_item,
)

logger = logging.getLogger("mcp-server-monday")


class ToolName(str, Enum):
    # Boards
    LIST_BOARDS = "monday-list-boards"
    GET_BOARD_GROUPS = "monday-get-board-groups"
    GET_BOARD_COLUMNS = "monday-get-board-columns"
    CREATE_BOARD = "monday-create-board"
    CREATE_BOARD_GROUP = "monday-create-board-group"

    # Items
    CREATE_ITEM = "monday-create-item"
    UPDATE_ITEM = "monday-update-item"
    CREATE_UPDATE = "monday-create-update"
    LIST_ITEMS_IN_GROUPS = "monday-list-items-in-groups"
    LIST_SUBITEMS_IN_ITEMS = "monday-list-subitems-in-items"

    GET_ITEM_BY_ID = "monday-get-items-by-id"
    MOVE_ITEM_TO_GROUP = "monday-move-item-to-group"
    DELETE_ITEM = "monday-delete-item"
    ARCHIVE_ITEM = "monday-archive-item"
    GET_ITEM_UPDATES = "monday-get-item-updates"

    GET_ITEM_FILES = "monday-get-item-files"
    GET_DOCS = "monday-get-docs"
    GET_DOC_CONTENT = "monday-get-doc-content"
    CREATE_DOC = "monday-create-doc"
    ADD_DOC_BLOCK = "monday-add-doc-block"
    GET_UPDATE_FILES = "monday-get-update-files"


ServerTools = [
    types.Tool(
        name=ToolName.CREATE_ITEM,
        description="Create a new item in a Monday.com Board. Optionally, specify the parent Item ID to create a Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "itemTitle": {
                    "type": "string",
                    "description": "Name of the Monday.com Item or Sub-item that will be created.",
                },
                "groupId": {
                    "type": "string",
                    "description": "Monday.com Board's Group ID to create the Item in. If set, parentItemId should not be set.",
                },
                "parentItemId": {
                    "type": "string",
                    "description": "Monday.com Item ID to create the Sub-item under. If set, groupId should not be set.",
                },
                "columnValues": {
                    "type": "object",
                    "description": "Dictionary of column values to set {column_id: value}",
                },
            },
            "required": ["boardId", "itemTitle"],
        },
    ),
    types.Tool(
        name=ToolName.GET_ITEM_BY_ID,
        description="Fetch specific Monday.com item by its ID",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "ID of the Monday.com item to fetch.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.UPDATE_ITEM,
        description="Update a Monday.com item's or sub-item's column values.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "itemId": {
                    "type": "string",
                    "description": "Monday.com Item or Sub-item ID to update the columns of.",
                },
                "columnValues": {
                    "type": "object",
                    "description": "Dictionary of column values to update the Monday.com Item or Sub-item with. ({column_id: value})",
                },
            },
            "required": ["boardId", "itemId", "columnValues"],
        },
    ),
    types.Tool(
        name=ToolName.GET_BOARD_COLUMNS,
        description="Get the Columns of a Monday.com Board.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
            },
            "required": ["boardId"],
        },
    ),
    types.Tool(
        name=ToolName.GET_BOARD_GROUPS,
        description="Get the Groups of a Monday.com Board.",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
            },
            "required": ["boardId"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_UPDATE,
        description="Create an update (comment) on a Monday.com Item or Sub-item.",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {"type": "string"},
                "updateText": {
                    "type": "string",
                    "description": "Content to update the Item or Sub-item with.",
                },
            },
            "required": ["itemId", "updateText"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_BOARDS,
        description="Get all Boards from Monday.com",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of Monday.com Boards to return.",
                },
                "page": {
                    "type": "integer",
                    "description": "Page number for pagination.",
                },
            },
        },
    ),
    types.Tool(
        name=ToolName.LIST_ITEMS_IN_GROUPS,
        description="List all items in the specified groups of a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the Item or Sub-item is on.",
                },
                "groupIds": {"type": "array", "items": {"type": "string"}},
                "limit": {"type": "integer"},
                "cursor": {"type": "string"},
            },
            "required": ["boardId", "groupIds", "limit"],
        },
    ),
    types.Tool(
        name=ToolName.LIST_SUBITEMS_IN_ITEMS,
        description="List all Sub-items of a list of Monday.com Items",
        inputSchema={
            "type": "object",
            "properties": {
                "itemIds": {"type": "array", "items": {"type": "string"}},
            },
            "required": ["itemIds"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_BOARD,
        description="Create a new Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "board_name": {
                    "type": "string",
                    "description": "Name of the Monday.com board to create",
                },
                "board_kind": {
                    "type": "string",
                    "description": "Kind of the Monday.com board to create (public, private, shareable). Default is public.",
                },
            },
            "required": ["board_name"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_BOARD_GROUP,
        description="Create a new group in a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "boardId": {
                    "type": "string",
                    "description": "Monday.com Board ID that the group will be created in.",
                },
                "groupName": {
                    "type": "string",
                    "description": "Name of the group to create.",
                },
            },
            "required": ["boardId", "groupName"],
        },
    ),
    types.Tool(
        name=ToolName.MOVE_ITEM_TO_GROUP,
        description="Move an item to a group in a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "Monday.com Item ID to move.",
                },
                "groupId": {
                    "type": "string",
                    "description": "Monday.com Group ID to move the Item to.",
                },
            },
            "required": ["itemId", "groupId"],
        },
    ),
    types.Tool(
        name=ToolName.DELETE_ITEM,
        description="Delete an item from a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "Monday.com Item ID to delete.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.ARCHIVE_ITEM,
        description="Archive an item from a Monday.com board",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "Monday.com Item ID to archive.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.GET_ITEM_UPDATES,
        description="Get updates for a specific item in Monday.com",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "ID of the Monday.com item to get updates for.",
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of updates to retrieve. Default is 25.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.GET_DOCS,
        description="Get a list of documents from Monday.com.",
        inputSchema={
            "type": "object",
            "properties": {
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of documents to retrieve. Default is 25.",
                },
            },
        },
    ),
    types.Tool(
        name=ToolName.GET_DOC_CONTENT,
        description="Get the content of a specific document by ID",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "ID of the Monday.com document to retrieve.",
                },
            },
            "required": ["doc_id"],
        },
    ),
    types.Tool(
        name=ToolName.CREATE_DOC,
        description="Create a new document in Monday.com. Specify either workspace_id (with kind) or board_id (with column_id and item_id) as the location.",
        inputSchema={
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Title of the document to create.",
                },
                "workspace_id": {
                    "type": "integer",
                    "description": "Workspace ID to create the document in (required if using workspace as location).",
                },
                "kind": {
                    "type": "string",
                    "description": "Kind of document (private, public, share). Required if using workspace_id.",
                },
                "board_id": {
                    "type": "integer",
                    "description": "Board ID to create the document in (required if using board as location).",
                },
                "column_id": {
                    "type": "string",
                    "description": "Column ID for the board location (required if using board_id).",
                },
                "item_id": {
                    "type": "integer",
                    "description": "Item ID for the board location (required if using board_id).",
                },
            },
            "required": ["title"],
            "oneOf": [
                {"required": ["workspace_id", "kind"]},
                {"required": ["board_id", "column_id", "item_id"]},
            ],
        },
    ),
    types.Tool(
        name=ToolName.ADD_DOC_BLOCK,
        description="Add a block to a document",
        inputSchema={
            "type": "object",
            "properties": {
                "doc_id": {
                    "type": "string",
                    "description": "ID of the Monday.com document to add a block to.",
                },
                "block_type": {
                    "type": "string",
                    "description": "Type of block to add (normal_text, bullet_list, numbered_list, heading, divider, etc.).",
                },
                "content": {
                    "type": "string",
                    "description": "Content of the block to add.",
                },
                "after_block_id": {
                    "type": "string",
                    "description": "Optional ID of the block to add this block after.",
                },
            },
            "required": ["doc_id", "block_type", "content"],
        },
    ),
    types.Tool(
        name=ToolName.GET_ITEM_FILES,
        description="Get files (PDFs, documents, images, etc.) attached to a Monday.com item",
        inputSchema={
            "type": "object",
            "properties": {
                "itemId": {
                    "type": "string",
                    "description": "ID of the Monday.com item to get files from.",
                },
            },
            "required": ["itemId"],
        },
    ),
    types.Tool(
        name=ToolName.GET_UPDATE_FILES,
        description="Get files (PDFs, documents, images, etc.) attached to a specific update in Monday.com",
        inputSchema={
            "type": "object",
            "properties": {
                "updateId": {
                    "type": "string",
                    "description": "ID of the Monday.com update to get files from.",
                },
            },
            "required": ["updateId"],
        },
    ),
]


def register_tools(server: Server, monday_client: MondayClient) -> None:
    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        return ServerTools

    @server.call_tool()
    async def handle_call_tool(
        name: str, arguments: dict | None
    ) -> Sequence[Union[types.TextContent, types.ImageContent, types.EmbeddedResource]]:
        try:
            match name:
                case ToolName.CREATE_ITEM:
                    return await handle_monday_create_item(
                        boardId=arguments.get("boardId"),
                        itemTitle=arguments.get("itemTitle"),
                        groupId=arguments.get("groupId"),
                        parentItemId=arguments.get("parentItemId"),
                        columnValues=arguments.get("columnValues"),
                        monday_client=monday_client,
                    )
                case ToolName.GET_BOARD_COLUMNS:
                    return await handle_monday_get_board_columns(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )
                case ToolName.GET_BOARD_GROUPS:
                    return await handle_monday_get_board_groups(
                        boardId=arguments.get("boardId"), monday_client=monday_client
                    )

                case ToolName.CREATE_UPDATE:
                    return await handle_monday_create_update_on_item(
                        itemId=arguments.get("itemId"),
                        updateText=arguments.get("updateText"),
                        monday_client=monday_client,
                    )

                case ToolName.UPDATE_ITEM:
                    return await handle_monday_update_item(
                        boardId=arguments.get("boardId"),
                        itemId=arguments.get("itemId"),
                        columnValues=arguments.get("columnValues"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_BOARDS:
                    return await handle_monday_list_boards(
                        monday_client=monday_client,
                        limit=arguments.get("limit", 100),
                        page=arguments.get("page", 1),
                    )

                case ToolName.LIST_ITEMS_IN_GROUPS:
                    return await handle_monday_list_items_in_groups(
                        boardId=arguments.get("boardId"),
                        groupIds=arguments.get("groupIds"),
                        limit=arguments.get("limit"),
                        cursor=arguments.get("cursor"),
                        monday_client=monday_client,
                    )

                case ToolName.LIST_SUBITEMS_IN_ITEMS:
                    return await handle_monday_list_subitems_in_items(
                        itemIds=arguments.get("itemIds"), monday_client=monday_client
                    )

                case ToolName.GET_ITEM_BY_ID:
                    return await handle_monday_get_item_by_id(
                        itemId=arguments.get("itemId"), monday_client=monday_client
                    )

                case ToolName.CREATE_BOARD:
                    return await handle_monday_create_board(
                        board_name=arguments.get("board_name"),
                        board_kind=arguments.get("board_kind"),
                        monday_client=monday_client,
                    )

                case ToolName.CREATE_BOARD_GROUP:
                    return await handle_monday_create_new_board_group(
                        board_id=arguments.get("boardId"),
                        group_name=arguments.get("groupName"),
                        monday_client=monday_client,
                    )

                case ToolName.MOVE_ITEM_TO_GROUP:
                    return await handle_monday_move_item_to_group(
                        monday_client=monday_client,
                        item_id=arguments.get("itemId"),
                        group_id=arguments.get("groupId"),
                    )

                case ToolName.DELETE_ITEM:
                    return await handle_monday_delete_item(
                        monday_client=monday_client,
                        item_id=arguments.get("itemId"),
                    )

                case ToolName.ARCHIVE_ITEM:
                    return await handle_monday_archive_item(
                        monday_client=monday_client,
                        item_id=arguments.get("itemId"),
                    )

                case ToolName.GET_ITEM_UPDATES:
                    return await handle_monday_get_item_updates(
                        itemId=arguments.get("itemId"),
                        limit=arguments.get("limit", 25),
                        monday_client=monday_client,
                    )

                case ToolName.GET_DOCS:
                    return await handle_monday_get_docs(
                        limit=arguments.get("limit", 25),
                        monday_client=monday_client,
                    )

                case ToolName.GET_DOC_CONTENT:
                    return await handle_monday_get_doc_content(
                        doc_id=arguments.get("doc_id"),
                        monday_client=monday_client,
                    )

                case ToolName.CREATE_DOC:
                    return await handle_monday_create_doc(
                        monday_client=monday_client,
                        title=arguments.get("title"),
                        board_id=arguments.get("board_id"),
                        column_id=arguments.get("column_id"),
                        item_id=arguments.get("item_id"),
                        workspace_id=arguments.get("workspace_id"),
                        kind=arguments.get("kind"),
                    )

                case ToolName.ADD_DOC_BLOCK:
                    return await handle_monday_add_doc_block(
                        doc_id=arguments.get("doc_id"),
                        block_type=arguments.get("block_type"),
                        content=arguments.get("content"),
                        after_block_id=arguments.get("after_block_id"),
                        monday_client=monday_client,
                    )

                case ToolName.GET_ITEM_FILES:
                    return await handle_monday_get_item_files(
                        itemId=arguments.get("itemId"),
                        monday_client=monday_client,
                    )

                case ToolName.GET_UPDATE_FILES:
                    return await handle_monday_get_update_files(
                        updateId=arguments.get("updateId"),
                        monday_client=monday_client,
                    )

                case _:
                    raise ValueError(f"Undefined behaviour for tool: {name}")

        except Exception as e:
            logger.error(f"Error calling tool {name}: {e}")
            raise
