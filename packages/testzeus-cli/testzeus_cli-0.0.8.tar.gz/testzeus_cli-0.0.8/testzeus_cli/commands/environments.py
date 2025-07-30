"""
Environment management commands for TestZeus CLI.
"""

import asyncio
import click
from pathlib import Path
from rich.console import Console
from testzeus_sdk import TestZeusClient
from testzeus_cli.config import get_client_config
from testzeus_cli.utils.formatters import format_output
from testzeus_cli.utils.auth import initialize_client_with_token
from testzeus_cli.utils.validators import parse_key_value_pairs

console = Console()

def _read_data_file(file_path: str) -> str:
    """
    Read data content from a file as plain text
    Args:
        file_path: Path to the data file
    Returns:
        The raw text content of the file
    """
    data_path = Path(file_path)
    if not data_path.exists():
        raise click.BadParameter(f"Data file not found: {file_path}")

    try:
        with open(data_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    except Exception as e:
        raise click.BadParameter(f"Failed to read data file: {str(e)}")

    # Always return the raw text content
    return content

@click.group()
def environments_group():
    """Manage environments in TestZeus"""
    pass


@environments_group.command(name="create")
@click.option("--name", required=True, help="Environment name")
@click.option("--status", default="draft", help="Environment status (draft, ready, deleted)")
@click.option("--data", help="Environment data as text")
@click.option("--data-file", "-df", type=click.Path(exists=True), help="Path to text file with environment data")
@click.option("--tags", help="Comma-separated list of tags")
@click.pass_context
def create(ctx, name, status, data, data_file, tags):
    """Create a new environment"""
    
    if data and data_file:
        raise click.UsageError("Cannot use both --data and --data-file")
    
    if not data and not data_file:
        raise click.UsageError("Either --data or --data-file is required")
    
    # Process the data content (from file or directly)
    data_content = _read_data_file(data_file) if data_file else data

    async def _run():
        config, token, stored_tenant_id, stored_user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)

        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()
            
            params = {"name": name, "status": status, "tenant": stored_tenant_id, "modified_by": stored_user_id}
            
            if data_content:
                params["data"] = data_content

            if tags:
                params["tags"] = tags.split(",")
            
            env = await client.environments.create(params)
            return env.data

    try:
        result = asyncio.run(_run())
        console.print(
            f"[green]Environment created successfully with ID: {result['id']}[/green]"
        )
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        console.print(f"[red]Error creating environment: {str(e)}[/red]")
        raise click.Abort()


@environments_group.command(name="list")
@click.option("--filters", "-f", multiple=True, help="Filter results (format: key=value)")
@click.option("--sort", help="Sort by field")
@click.option("--expand", help="Expand related entities")
@click.pass_context
def list(ctx, filters, sort, expand):
    """List all environments"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)
        filter_dict = parse_key_value_pairs(filters) if filters else {}
        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()
            result = await client.environments.get_list(
                expand=expand, sort=sort, filters=filter_dict
            )
            return result

    try:
        result = asyncio.run(_run())
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        console.print(f"[red]Error listing environments: {str(e)}[/red]")
        raise click.Abort()


@environments_group.command(name="delete")
@click.argument("env_id")
@click.pass_context
def delete(ctx, env_id):
    """Delete an environment"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)
        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()
            await client.environments.delete(env_id)
            return {"id": env_id}

    try:
        result = asyncio.run(_run())
        console.print(f"[green]Environment {result['id']} deleted successfully[/green]")
    except Exception as e:
        console.print(f"[red]Error deleting environment: {str(e)}[/red]")
        raise click.Abort()

@environments_group.command(name="get")
@click.argument("env_id")
@click.option("--expand", help="Expand related entities")
@click.pass_context
def get(ctx, env_id, expand):
    """Get an environment by ID"""

    async def _run():
        config, token, _, _ = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)
        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()
            env = await client.environments.get_one(env_id, expand=expand)
            return env.data

    try:
        result = asyncio.run(_run())
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        console.print(f"[red]Error getting environment: {str(e)}[/red]")
        raise click.Abort()


@environments_group.command(name="update")
@click.argument("env_id")
@click.option("--name", help="New environment name")
@click.option("--status", help="New environment status (draft, ready, deleted)")
@click.option("--data", help="New environment data as text")
@click.option("--data-file", "-df", type=click.Path(exists=True), help="Path to text file with new environment data")
@click.option("--tags", help="Comma-separated list of tags")
@click.pass_context
def update(ctx, env_id, name, status, data, data_file, tags):
    """Update an environment"""

    if data and data_file:
        raise click.UsageError("Cannot use both --data and --data-file")
    
    # Process the data content (from file or directly)
    data_content = None
    if data_file:
        data_content = _read_data_file(data_file)
    elif data:
        data_content = data


    async def _run():
        config, token, tenant_id, user_id = get_client_config(
            ctx.obj["PROFILE"], api_url=ctx.obj.get("API_URL")
        )
        client = TestZeusClient(**config)
        async with client:
            if token:
                initialize_client_with_token(client, token)
            else:
                await client.ensure_authenticated()
            updates = {"tenant": tenant_id, "modified_by": user_id}
            has_updates = False

            if name:
                updates["name"] = name
                has_updates = True

            if status:
                updates["status"] = status
                has_updates = True

            if data_content:
                updates["data"] = data_content
                has_updates = True

            if tags and tags != "none":
                updates["tags"] = tags.split(",")
                has_updates = True

            if tags == "none":
                updates["tags"] = None
                has_updates = True

            if has_updates:
                updated_env = await client.environments.update(env_id, updates)
                return updated_env.data
            else:
                console.print("[yellow]No updates provided[/yellow]")
                return None

    try:
        result = asyncio.run(_run())
        console.print(f"[green]Environment updated successfully[/green]")
        format_output(result, ctx.obj["FORMAT"])
    except Exception as e:
        console.print(f"[red]Error updating environment: {str(e)}[/red]")
        raise click.Abort()
