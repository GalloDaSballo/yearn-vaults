from pathlib import Path
from brownie import Strategy, accounts, config, network, project, web3, run
from eth_utils import is_checksum_address
import click

import os
import sys


API_VERSION = config["dependencies"][0].split("@")[-1]
Vault = project.load(
    Path.home() / ".brownie" / "packages" / config["dependencies"][0]
).Vault


def get_address(msg: str, default: str = None) -> str:
    val = click.prompt(msg, default=default)

    # Keep asking user for click.prompt until it passes
    while True:

        if is_checksum_address(val):
            return val
        elif addr := web3.ens.address(val):
            click.echo(f"Found ENS '{val}' [{addr}]")
            return addr

        click.echo(
            f"I'm sorry, but '{val}' is not a checksummed address or valid ENS record"
        )
        # NOTE: Only display default once
        val = click.prompt(msg)

def deploy_vault():
    prev_home = os.getcwd()
    path_for_project = Path.home() / ".brownie" / "packages" / config["dependencies"][0] / "scripts"
    path_to_script = Path.home() / ".brownie" / "packages" / config["dependencies"][0] / "scripts" / "deploy.py"

    sys.path.append(path_for_project.as_posix())
    print("sys.path")
    print(sys.path)

    ## Cd into it
    os.chdir(path_for_project.as_posix())

    ## Run with brownie there
    x = run(path_to_script.as_posix())
    ## Save var
    os.chdir(prev_home)

    ## Return here
    return x

def main():
    print(f"You are using the '{network.show_active()}' network")
    dev = accounts.load(click.prompt("Account", type=click.Choice(accounts.load())))
    print(f"You are using: 'dev' [{dev.address}]")

    if input("Is there a Vault for this strategy already? y/[N]: ").lower() == "y":
        vault = Vault.at(get_address("Deployed Vault: "))
        assert vault.apiVersion() == API_VERSION
    else:
        print("Deploying Vaults by Running Script from Yearn-Vaults")
        vault = deploy_vault()

    print(
        f"""
    Strategy Parameters

       api: {API_VERSION}
     token: {vault.token()}
      name: '{vault.name()}'
    symbol: '{vault.symbol()}'
    """
    )
    publish_source = click.confirm("Verify source on etherscan?")
    if input("Deploy Strategy? y/[N]: ").lower() != "y":
        return

    strategy = Strategy.deploy(vault, {"from": dev}, publish_source=publish_source)
