#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
RegScale STIG Integration
"""

import click

from regscale.integrations.commercial.stigv2.stig_integration import StigIntegration
from regscale.models.app_models.click import NotRequiredIf


@click.group(name="stigv2")
def stigv2():
    """STIG Integrations"""


@stigv2.command(name="sync_findings")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    cls=NotRequiredIf,
    not_required_if=["component_id"],
)
@click.option(
    "-c",
    "--component_id",
    type=click.INT,
    help="The ID number from RegScale of the Component",
    prompt="Enter RegScale Component ID",
    cls=NotRequiredIf,
    not_required_if=["regscale_ssp_id"],
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def sync_findings(regscale_ssp_id, component_id, stig_directory):
    """Sync GCP Findings to RegScale."""
    if component_id:
        StigIntegration.sync_findings(plan_id=component_id, path=stig_directory, is_component=True)
    else:
        StigIntegration.sync_findings(plan_id=regscale_ssp_id, path=stig_directory, is_component=False)


@stigv2.command(name="sync_assets")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan to sync assets to.",
    cls=NotRequiredIf,
    not_required_if=["component_id"],
)
@click.option(
    "-c",
    "--component_id",
    type=click.INT,
    help="The ID number from RegScale of the Component to sync assets to.",
    cls=NotRequiredIf,
    not_required_if=["regscale_ssp_id"],
    default=None,
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def sync_assets(regscale_ssp_id, component_id, stig_directory):
    """Sync GCP Assets to RegScale."""
    if component_id:
        StigIntegration.sync_assets(plan_id=component_id, path=stig_directory, is_component=True)
    elif regscale_ssp_id:
        StigIntegration.sync_assets(plan_id=regscale_ssp_id, path=stig_directory, is_component=False)
    else:
        raise click.UsageError("Either --regscale_ssp_id or --component_id must be provided.")


@stigv2.command(name="process_checklist")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
@click.option(
    "-d",
    "--stig_directory",
    type=click.Path(),
    help="The directory where STIG files are located",
    prompt="Enter STIG directory",
    required=True,
)
def process_checklist(regscale_ssp_id, stig_directory):
    """Process GCP Checklist."""
    StigIntegration.sync_assets(plan_id=regscale_ssp_id, path=stig_directory)
    StigIntegration.sync_findings(plan_id=regscale_ssp_id, path=stig_directory)


@stigv2.command(name="cci_assessment")
@click.option(
    "-p",
    "--regscale_ssp_id",
    type=click.INT,
    help="The ID number from RegScale of the System Security Plan",
    prompt="Enter RegScale System Security Plan ID",
    required=True,
)
def cci_assessment(regscale_ssp_id):
    """Run CCI Assessment."""
    StigIntegration.cci_assessment(plan_id=regscale_ssp_id)
