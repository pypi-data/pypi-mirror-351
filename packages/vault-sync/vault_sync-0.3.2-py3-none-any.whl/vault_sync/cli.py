import sys
import time

import click
import schedule
from hvac.exceptions import InvalidPath
from loguru import logger

from vault_sync import __version__, constants
from vault_sync.exceptions import ConfigException, VaultLoginException
from vault_sync.vault_sync import VaultSync

logger.remove()


def loop():
    """
    Returns:
        bool: The function consistently returns the boolean value True.
    """
    return True


def job(vault_sync: VaultSync):
    logger.info("syncing vault k/v stores...")
    vault_sync.authenticate_clients()
    vault_sync.sync_all()


def schedule_job(vault_sync: VaultSync):
    """
    Schedule a periodic job using a VaultSync instance.

    This function sets up a periodic scheduling of a job based on the `VaultSync`
    instance configuration. It runs the scheduled jobs in a continuous loop and
    handles interruptions, authentication failures, and exit signals.

    Parameters:
        vault_sync (VaultSync): An instance of VaultSync that provides configuration
            details for scheduling and job execution behavior.

    Raises:
        KeyboardInterrupt: When the user interrupts the loop manually.
        SystemExit: When the process is signaled to exit.
        VaultLoginException: If the authentication process to Vault fails.

    """
    schedule.every(vault_sync.config.schedule.every).seconds.do(job, vault_sync=vault_sync)

    logger.debug("starting loop...")
    while loop():
        try:
            schedule.run_pending()
            time.sleep(0.5)
        except (KeyboardInterrupt, SystemExit):
            logger.info("exiting...")
            break
        except VaultLoginException:
            logger.error("authentication failed, retrying in 15 seconds...")
            time.sleep(15)
            continue


@click.command()
@click.version_option(__version__)
@click.option(
    "--config",
    default="config.json",
    type=click.Path(exists=True, file_okay=True, dir_okay=False, readable=True),
    help="Path to the configuration file",
)
@click.option("--list-keys", is_flag=True, help="Only list the secret keys in the source")
@click.option("--debug", is_flag=True, help="Enable debug logging")
def main(config, list_keys, debug):
    """
    Main command-line interface function for the Vault synchronization tool. This function
    allows the user to run the Vault synchronization, provide configuration options, list
    secret keys, and enable debug logging.

    Args:
        config (str): Path to the configuration file. Defaults to "config.json".
        list_keys (bool): Flag to list the secret keys in the source. Does not perform the
            synchronization when this is enabled.
        debug (bool): Flag to enable debug logging. Default level is INFO.

    Raises:
        ConfigException: Raised when there is an issue with the provided configuration.
        VaultLoginException: Raised if there is a failure during login and authentication
            with the Vault.
    """
    logger.add(sys.stderr, format=constants.LOG_FORMAT, level="DEBUG" if debug else "INFO")

    try:
        vault_sync = VaultSync(config_file=config)
        vault_sync.authenticate_clients()
        if list_keys:
            keys = "\n".join(
                vault_sync.list_all_keys(vault_sync.source_client, mount_point=vault_sync.config.source.kv_store)
            )
            click.echo(f"Secret keys in source:\n{keys}")
            return

        if vault_sync.config.schedule.every > 0:
            schedule_job(vault_sync)
            return

        # sync once
        vault_sync.sync_all()
        return

    except (ConfigException, VaultLoginException) as err:
        click.secho(f"Error: {err}", fg="red")
        sys.exit(1)
    except InvalidPath as err:
        if "source" in str(err):
            click.secho("Error: source path not found", fg="red")
        else:
            click.secho("Error: destination path not found", fg="red")


if __name__ == "__main__":
    main()
