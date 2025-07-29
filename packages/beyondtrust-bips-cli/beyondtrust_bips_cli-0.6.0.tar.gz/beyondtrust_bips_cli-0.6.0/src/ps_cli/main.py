"""
Password Safe CLI Entrypoint
"""

from ps_cli.controllers.address_groups import AddressGroup
from ps_cli.controllers.assets import Asset
from ps_cli.controllers.databases import Database
from ps_cli.controllers.folders import Folder
from ps_cli.controllers.managed_accounts import ManagedAccount
from ps_cli.controllers.managed_systems import ManagedSystem
from ps_cli.controllers.organizations import Organization
from ps_cli.controllers.safes import Safe
from ps_cli.controllers.secrets import Secret
from ps_cli.controllers.settings import Settings
from ps_cli.controllers.workgroups import Workgroup
from ps_cli.core.app import App


def main() -> None:
    controllers = [
        AddressGroup,
        Safe,
        Folder,
        Secret,
        ManagedAccount,
        ManagedSystem,
        Workgroup,
        Database,
        Organization,
        Settings,
        Asset,
    ]

    app = App(controllers=controllers)
    app.run()


if __name__ == "__main__":
    main()
