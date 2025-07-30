"""
Copyright 2025 Omnissa Inc.
SPDX-License-Identifier: Apache-2.0

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import logging

import click
import hcs_core.ctxp.data_util as data_util
import hcs_core.sglib.cli_options as cli
import httpx
from hcs_core.ctxp import recent

from hcs_cli.service import admin, diagnostics

log = logging.getLogger(__name__)


@click.command("edge-getpods", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_getpods(id: str, org: str, verbose: bool):
    """Get edge connection string"""
    org_id = cli.get_org_id(org)
    id = recent.require(id, "edge")
    ret = diagnostics.edge.diagnose_get_pods(id, org_id=org_id, verbose=verbose)
    if ret:
        return ret
    return "", 1


@click.command("edge-url-reachability", hidden=True)
@click.argument("id", type=str, required=True)
@click.option("--namespace", "-n", type=str, required=True, default="edge-namespace")
@click.option("--podname", "-p", type=str, required=True, default="mqtt-server-0")
@click.option("--url", "-u", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_url_reachability(id: str, org: str, namespace: str, podname: str, url: str, verbose: bool):
    """Get edge connection string"""
    org_id = cli.get_org_id(org)
    id = recent.require(id, "edge")
    ret = diagnostics.edge.diagnose_url_accessibility(
        id, org_id=org_id, namespace=namespace, podname=podname, url2check=url, verbose=verbose
    )
    if ret:
        return ret
    return "", 1


@click.command("copy-privatelink-dns-records", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def edge_copy_privatelink_dns_records(id: str, org: str, verbose: bool):
    """Copy privatelink edge dns records"""
    org_id = cli.get_org_id(org)
    id = recent.require(id, "edge")
    ret = admin.edge.copy_private_endpoint_dns_records(id, org_id=org_id, verbose=verbose)
    if ret:
        return ret
    return "", 1


@click.command("check-omnissa-privatelink-reachability", hidden=True)
@click.argument("id", type=str, required=True)
@cli.org_id
@cli.verbose
def check_omnissa_privatelink_dns_records(id: str, org: str, verbose: bool):
    """Check omnissa privatelink edge dns records"""
    org_id = cli.get_org_id(org)
    id = recent.require(id, "edge")

    log.info(f"Check Omnissa regional mqtt url reachability for org: {org_id}, edge: {id}")
    podname = "mqtt-server-0"

    # 1. Get privatelink url
    myEdge = admin.edge.get(id=id, org_id=org_id)
    regional_mqtt_url = data_util.deep_get_attr(myEdge, "privateEndpointDetails.dnsRecord", raise_on_not_found=False)
    omnissa_regional_mqtt_url = "https://" + regional_mqtt_url.replace("vmware", "omnissa")
    log.info(f"regional mqtt: {regional_mqtt_url}, url to verify: {omnissa_regional_mqtt_url}")

    # 2. Copy the privatelink endpoint dns records
    ret = admin.edge.copy_private_endpoint_dns_records(id, org_id=org_id, verbose=verbose)
    if not ret:
        return "Failed to copy dns records in omnissa privatelink domain", 1

    # 3. Get pods and namespaces
    ret = diagnostics.edge.diagnose_get_pods(id, org_id=org_id, verbose=verbose)
    if not ret:
        return f"Failed to get pods in edge {id}", 1
    lines = ret.get("diagnosticData").split("\n")

    namespace = "edge-namespace"
    for line in lines:
        if "mqtt-server-0" in line:
            namespace = line.split(" ")[0].strip()

    # 4. Finally verify url reachability
    log.info("Verify url:")
    log.info(f" edgeId: {id}")
    log.info(f" org_id: {org_id}")
    log.info(f" namespace: {namespace}")
    log.info(f" pod: mqtt-server-0")
    log.info(f" url: {omnissa_regional_mqtt_url}")

    try:
        exitcode60Found = False
        ret = diagnostics.edge.diagnose_url_accessibility(
            id,
            org_id=org_id,
            namespace=namespace,
            podname=podname,
            url2check=omnissa_regional_mqtt_url,
            verbose=verbose,
        )
        if ret:
            log.info(ret)
            if ret.get("diagnosticData").find("command terminated with exit code 60") > 0:
                exitcode60Found = True

    except httpx.HTTPStatusError as e:
        log.error(str(e))
        log.error(e.__cause__)
        log.error(e.response.content)

        if str(e.response.content).find("command terminated with exit code 60") > 0:
            exitcode60Found = True

    if exitcode60Found:
        log.info(f"url {omnissa_regional_mqtt_url} is reachable on edge: {id}.")
        return 0

    log.info(f"url {omnissa_regional_mqtt_url} is not reachable on edge: {id}.")
    return "", 1
