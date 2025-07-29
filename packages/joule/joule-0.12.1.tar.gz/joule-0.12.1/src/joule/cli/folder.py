import click
import asyncio
from treelib import Tree

import joule.api
from joule import errors
from joule.cli.config import Config, pass_config
from joule.api import BaseNode
from joule.api.folder import Folder
from joule.api.data_stream import DataStream
from joule.api.event_stream import EventStream
import joule.constants

@click.command(name="move")
@click.argument("source")
@click.argument("destination")
@pass_config
def move(config: Config, source: str, destination: str):
    """Move a folder to a new location."""

    try:
        asyncio.run(
            config.node.folder_move(source, destination))
    except errors.ApiError as e:
        raise click.ClickException(str(e)) from e
    finally:
        asyncio.run(
            config.close_node())

    click.echo("OK")


@click.command(name="rename")
@click.argument("folder")
@click.argument("name")
@pass_config
def rename(config: Config, folder, name):
    """Rename a folder."""

    try:
        asyncio.run(
            _run_rename(config.node, folder, name))
    except errors.ApiError as e:
        raise click.ClickException(str(e)) from e
    finally:
        asyncio.run(
            config.close_node())

    click.echo("OK")


async def _run_rename(node: BaseNode, folder_path: str, name: str):
    folder = await node.folder_get(folder_path)
    folder.name = name
    await node.folder_update(folder)


@click.command(name="delete")
@click.option("--recursive", "-r", is_flag=True)
@click.argument("folder")
@pass_config
def delete(config, folder, recursive):
    """Delete a folder and all contents."""

    try:
        asyncio.run(
            config.node.folder_delete(folder, recursive))
        click.echo("OK")
    except errors.ApiError as e:
        raise click.ClickException(str(e))
    finally:
        asyncio.run(
            config.close_node())


@click.command(name="list")
@click.argument("path", default="/")
@click.option("--layout", "-l", is_flag=True, help="include stream layout")
@click.option("--status", "-s", is_flag=True, help="include stream status")
@click.option("--id", "-i", is_flag=True, help="show ID's")
@pass_config
def list(config, path, layout, status, id):
    """Display folder hierarchy (directory layout)."""

    try:
        asyncio.run(
            _run_list(config.node, path, layout, status, id))
    except errors.ApiError as e:
        raise click.ClickException(str(e)) from e
    finally:
        asyncio.run(
            config.close_node())


async def _run_list(node: BaseNode, path: str, layout: bool, status: bool, showid: bool):
    tree = Tree()
    if path == "/":
        root = await node.folder_root()
        root.name = ""  # omit root name
        if len(root.children) == 0:
            click.echo("No folders, this node is empty.")
            return
    else:
        root = await node.folder_get(path)
    _process_folder(tree, root, None, layout, status, showid)
    click.echo("Legend: [" + click.style("Folder", bold=True) + "] [Data Stream] ["
               + click.style("Event Stream", fg='cyan') + "]")
    if status:
        click.echo("\t" + click.style("\u25CF ", fg="green") + "active  " +
                   click.style("\u25CF ", fg="cyan") + "configured")
    click.echo(tree.show(stdout=False))


def _process_folder(tree: Tree, folder: Folder, parent_id,
                    layout: bool, status: bool, showid: bool):
    tag = click.style(folder.name, bold=True)
    if showid:
        tag += " (%d)" % folder.id
    identifier = "f%d" % folder.id
    tree.create_node(tag, identifier, parent_id)
    for stream in folder.data_streams:
        _process_data_stream(tree, stream, identifier, layout, status, showid)
    for stream in folder.event_streams:
        _process_event_stream(tree, stream, identifier, showid)
    for child in folder.children:
        _process_folder(tree, child, identifier, layout, status, showid)


def _process_data_stream(tree: Tree, stream: DataStream, parent_id,
                         layout: bool, status: bool, showid: bool):
    tag = stream.name
    if showid:
        tag += " (%d)" % stream.id
    if layout:
        tag += " (%s)" % stream.layout
    if status:
        if stream.active:
            tag = click.style("\u25CF ", fg="green") + tag
        elif stream.locked:
            tag = click.style("\u25CF ", fg="cyan") + tag

    identifier = "s%d" % stream.id
    tree.create_node(tag, identifier, parent_id)


def _process_event_stream(tree: Tree, stream: EventStream, parent_id, showid: bool):
    tag = stream.name
    if showid:
        tag += " (%d)" % stream.id
    tag = click.style(tag, fg="cyan")
    identifier = "e%d" % stream.id
    tree.create_node(tag, identifier, parent_id)


action_on_event_conflict = None

@click.command(name="copy")
@click.argument("source")
@click.argument("destination")
@click.option('-s', "--start", help="timestamp or descriptive string")
@click.option('-e', "--end", help="timestamp or descriptive string")
@click.option("-d", "--destination-node")
@pass_config
def copy(config, source, destination, start, end, destination_node):
    """Recursively copy a folder to a new, empty location"""
    try:
        if destination_node is not None:
            destination_node = joule.api.get_node(destination_node)
        else:
            destination_node = config.node
        asyncio.run(_validate_destination_is_empty(destination_node, destination))
        asyncio.run(
            _run_copy(config.node, source, destination, start, end, destination_node))
    except errors.ApiError as e:
        raise click.ClickException(str(e)) from e
    finally:
        asyncio.run(
            config.close_node())

async def _validate_destination_is_empty(destination_node: BaseNode, destination: str):
    try:
        folder = await destination_node.folder_get(destination)
        if len(folder.children) > 0 or len(folder.data_streams) > 0 or len(folder.event_streams) > 0:
            raise click.ClickException(f"Destination folder [{destination}] is not empty")
    except errors.ApiError as e:
        if joule.constants.ApiErrorMessages.folder_does_not_exist in str(e):
            return
        raise e
    
async def _run_copy(source_node, source, destination, start, end, destination_node) -> None:
    from joule.cli.data.copy import _run as run_data_copy # lazy import
    from joule.cli.event.copy import _run as run_event_copy # lazy import

    if type(source) is str: # initial call is a string, the recursive calls are Folder objects
        source_folder = await source_node.folder_get(source)
    else:
        source_folder = source
    
    for child in source_folder.children:
        await _run_copy(source_node, child, f"{destination}/{child.name}", start, end,
                        destination_node)
    for data_stream in source_folder.data_streams:
        click.echo(f"Writing Data Stream {destination}/{data_stream.name}")
        try:
            await run_data_copy(source_node, start, end, new=False, 
                                destination_node=destination_node, 
                                source=data_stream,
                                destination=f"{destination}/{data_stream.name}")
        except errors.ApiError as e:
            if "has no data" in str(e):
                print("\t skipping, this stream has no data")
            else:
                raise e
            
    for source_stream in source_folder.event_streams:
        destination_stream = f"{destination}/{source_stream.name}"
        click.echo(f"Writing Event Stream {destination_stream}")
        
        await run_event_copy(source_node, destination_node, start, end, 
                             new=False, replace=False, source=source_stream,
                             destination=destination_stream)


@click.group(name="folder")
def folders():
    """Manage folders."""
    pass  


folders.add_command(copy)
folders.add_command(move)
folders.add_command(delete)
folders.add_command(rename)
folders.add_command(list)
