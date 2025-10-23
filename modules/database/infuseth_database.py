"""Azure PostgreSQL Flexible Server module for backend database."""

from typing import Literal

import pulumi
from pulumi_azure_native import dbforpostgresql

# Define valid PostgreSQL SKUs for Flexible Server
PostgreSQLSku = Literal["Standard_B1ms", "Standard_B2s", "Standard_D2s_v3"]


class InfusethDatabaseServer:
    """Azure PostgreSQL Flexible Server factory for shared database server."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        location: pulumi.Input[str],
        server_name: str,
        admin_username: str,
        admin_password: pulumi.Input[str],
        sku_name: PostgreSQLSku = "Standard_B1ms",
        storage_size_gb: int = 32,
        postgresql_version: str = "17",
        tags: dict[str, str] | None = None,
    ) -> dbforpostgresql.Server:
        """Create a shared PostgreSQL Flexible Server.

        This server should be created once and shared across all environments.
        Each environment will create its own database within this server.

        Args:
            name: Resource identifier
            resource_group_name: Azure resource group name
            location: Azure region
            server_name: PostgreSQL server name
            admin_username: Administrator username
            admin_password: Administrator password (should be a secret)
            sku_name: Server SKU (Standard_B1ms is cheapest burstable tier)
            storage_size_gb: Storage size in GB (minimum 32GB)
            postgresql_version: PostgreSQL version (17 is latest stable)
            tags: Additional resource tags

        Returns:
            PostgreSQL Server instance
        """
        # Create PostgreSQL Flexible Server
        server = dbforpostgresql.Server(
            f"psql-{server_name}",
            resource_group_name=resource_group_name,
            location=location,
            server_name=f"psql-{server_name}",
            version=postgresql_version,
            administrator_login=admin_username,
            administrator_login_password=admin_password,
            sku=dbforpostgresql.SkuArgs(
                name=sku_name,
                tier="Burstable"
                if sku_name.startswith("Standard_B")
                else "GeneralPurpose",
            ),
            storage=dbforpostgresql.StorageArgs(
                storage_size_gb=storage_size_gb,
            ),
            backup=dbforpostgresql.BackupArgs(
                backup_retention_days=7,
                geo_redundant_backup="Disabled",
            ),
            high_availability=dbforpostgresql.HighAvailabilityArgs(
                mode="Disabled",
            ),
            tags=tags or {},
        )

        # Configure firewall to allow Azure services
        dbforpostgresql.FirewallRule(
            f"psql-{server_name}-allow-azure",
            resource_group_name=resource_group_name,
            server_name=server.name,
            firewall_rule_name="AllowAllAzureServicesAndResourcesWithinAzureIps",
            start_ip_address="0.0.0.0",
            end_ip_address="0.0.0.0",
        )

        # Allow all IPs for development (hobby project with dynamic residential IP)
        # Note: Still requires username/password + SSL/TLS encryption
        dbforpostgresql.FirewallRule(
            f"psql-{server_name}-allow-all",
            resource_group_name=resource_group_name,
            server_name=server.name,
            firewall_rule_name="AllowAllIPs",
            start_ip_address="0.0.0.0",
            end_ip_address="255.255.255.255",
        )

        return server


class InfusethDatabase:
    """Azure PostgreSQL Flexible Server factory."""

    @classmethod
    def sync(
        cls,
        name: str,
        resource_group_name: pulumi.Input[str],
        server_name: pulumi.Input[str],
        server_fqdn: pulumi.Input[str],
        database_name: str,
        admin_username: str,
        admin_password: pulumi.Input[str],
        tags: dict[str, str] | None = None,
    ) -> tuple[dbforpostgresql.Database, pulumi.Output[str]]:
        """Create a database within an existing PostgreSQL Flexible Server.

        This is used per-environment to create separate databases on a shared server.

        Args:
            name: Resource identifier
            resource_group_name: Azure resource group name
            server_name: Existing PostgreSQL server name (from shared stack)
            server_fqdn: Server FQDN (from shared stack)
            database_name: Database name to create
            admin_username: Administrator username
            admin_password: Administrator password (should be a secret)
            tags: Additional resource tags

        Returns:
            Tuple of (database, connection_string_secret)
        """
        # Create database on the existing server
        database = dbforpostgresql.Database(
            f"psqldb-{database_name}",
            resource_group_name=resource_group_name,
            server_name=server_name,
            database_name=database_name,
            charset="UTF8",
            collation="en_US.utf8",
        )

        # Build connection string as a Pulumi secret
        # Format: postgresql+psycopg://username:password@hostname:port/database?sslmode=require
        # The +psycopg driver specifier is required for SQLAlchemy/SQLModel with psycopg3
        connection_string = pulumi.Output.all(
            server_fqdn,
            admin_username,
            admin_password,
            database_name,
        ).apply(
            lambda args: pulumi.Output.secret(
                f"postgresql+psycopg://{args[1]}:{args[2]}@{args[0]}:5432/{args[3]}?sslmode=require"
            )
        )

        return database, connection_string
