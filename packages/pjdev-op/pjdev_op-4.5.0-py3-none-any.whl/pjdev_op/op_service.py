import asyncio
from pathlib import Path
from typing import Optional, List

from onepassword import Client, VaultOverview, ItemOverview
from onepassword.types import Item, ItemCreateParams, ItemField, ItemSection
from pjdev_op.models import Config, FieldUpdate

__ctx = {}


def get_client() -> Client:
    return __ctx["client"]


def get_config() -> Config:
    return __ctx["config"]


async def init(env_path: Optional[Path] = None) -> None:
    __ctx["config"] = Config() if env_path is None else Config(_env_file=env_path)

    client = await Client.authenticate(
        auth=get_config().service_token,
        integration_name="pj-stack",
        integration_version="v1.0.0",
    )

    __ctx["client"] = client


async def load_secret(op_path: str) -> str:
    client = get_client()
    return await client.secrets.resolve(f"op://{op_path}")


async def update_secret(
    item_name: str, vault_name: str, fields: List[FieldUpdate]
) -> Item:
    client = get_client()

    vault = await get_vault_by_name(vault_name)
    if vault is None:
        raise ValueError("Vault not found")
    item_overview = await get_item_by_name(vault.id, item_name)
    if item_overview is None:
        raise ValueError(f"Item not found in vault {vault.title}")
    item = await client.items.get(vault_id=vault.id, item_id=item_overview.id)
    for field in fields:
        filtered_fields_indices = [
            ndx for ndx, f in enumerate(item.fields) if f.title == field.title
        ]
        if len(filtered_fields_indices) == 0:
            raise ValueError(f"field [{field.title}] does not exist")

        item.fields[filtered_fields_indices[0]].value = field.new_value
    updated_item = await client.items.put(item)
    return updated_item


async def create_secret(name: str, vault_name: str, fields: List[FieldUpdate]) -> Item:
    client = get_client()

    vault = await get_vault_by_name(vault_name)
    if vault is None:
        raise ValueError("Vault not found")

    item_overview = await get_item_by_name(vault.id, name)
    if item_overview is not None:
        raise ValueError(f"Item {name} already exists in vault {vault.title}")

    to_create = ItemCreateParams(
        title=name,
        category="Password",
        vault_id=vault.id,
        fields=[
            ItemField(
                id=f.title,
                title=f.title,
                field_type="Concealed",
                value=f.new_value,
                section_id="main",
            )
            for f in fields
        ],
        sections=[ItemSection(id="main", title="Main")],
    )

    created_item = await client.items.create(to_create)
    return created_item


async def get_vault_by_name(name: str) -> Optional[VaultOverview]:
    client = get_client()

    vaults = await client.vaults.list_all()
    async for vault in vaults:
        if vault.title == name:
            return vault

    return None


async def get_item_by_name(vault_id: str, name: str) -> Optional[ItemOverview]:
    client = get_client()
    items = await client.items.list_all(vault_id=vault_id)

    async for item in items:
        if item.title == name:
            return item

    return None


if __name__ == "__main__":

    async def main() -> None:
        await init(env_path=Path(".env"))
        await update_secret(
            "dummy_item",
            "gitlab",
            [FieldUpdate(title="secret_value", new_value="1235asdf")],
        )

    asyncio.run(main())
