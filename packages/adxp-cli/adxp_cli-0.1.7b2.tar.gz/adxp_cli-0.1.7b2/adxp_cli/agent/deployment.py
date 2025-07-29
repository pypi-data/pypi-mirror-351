import click
import requests
from adxp_cli.auth.service import get_credential
from tabulate import tabulate
from typing import Optional

def get_agent_app_list(page: int, size: int, search: Optional[str], all: bool):
    """Get List of Agents"""
    headers, config = get_credential()
    url = f"{config.base_url}/api/v1/agent/agents/apps"

    params = {"page": str(page), "size": str(size), "target_type": "external_graph"}
    if search:
        params["search"] = search

    res = requests.get(url, headers=headers, params=params)
    if res.status_code == 401:
        raise click.ClickException(
            "🔐 401 Unauthorized : Please login again. \n Run Either One of the Following Commands \n 1. adxp-cli auth login \n 2. adxp-cli auth refresh"
        )
    if res.status_code == 200:
        data = res.json().get("data")
        if data:
            # 테이블로 정제해서 출력
            table = []
            if all:
                headers_ = [
                    "id",
                    "name",
                    "description",
                    "created_at",
                    "updated_at",
                    "versions",
                ]
                for item in data:
                    versions = ", ".join(
                        str(d.get("version"))
                        for d in item.get("deployments", [])
                        if d.get("version") is not None
                    )
                    row = [
                        item.get("id", ""),
                        item.get("name", ""),
                        item.get("description", ""),
                        item.get("created_at", ""),
                        item.get("updated_at", ""),
                        versions,
                    ]
                    table.append(row)
            else:
                headers_ = ["id", "name", "versions"]
                for item in data:
                    versions = ", ".join(
                        str(d.get("version"))
                        for d in item.get("deployments", [])
                        if d.get("version") is not None
                    )
                    row = [
                        item.get("id", ""),
                        item.get("name", ""),
                        versions,
                    ]
                    table.append(row)
            click.secho("✅ Deployed Custom Agent APPs:", fg="green")
            click.echo(
                tabulate(table, headers=headers_, tablefmt="github", showindex=True)
            )
        else:
            click.secho("⚠️ No deployed custom agent apps found.", fg="yellow")
    else:
        raise click.ClickException(
            f"❌ Failed to get deployed custom agent apps: {res.status_code}\n{res.text}"
        )
