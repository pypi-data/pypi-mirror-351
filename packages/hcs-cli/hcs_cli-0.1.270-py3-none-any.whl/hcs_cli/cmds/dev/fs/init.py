"""
Copyright 2023-2023 VMware Inc.
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

import subprocess

import click
import hcs_core.sglib.cli_options as cli
from hcs_core.ctxp import profile
from hcs_core.ctxp.util import print_error

from hcs_cli.service import org_service


@click.command()
@cli.org_id
def init(org: str, **kwargs):
    """Init feature stack org, org details, and"""
    org_id = cli.get_org_id(org)
    feature_stack_url = profile.current().hcs.url

    _get_client_credential_from_secret_and_update_profile()
    _update_feature_stack(feature_stack_url)
    _init_org(org_id)
    _restart_services()


def _update_feature_stack(url):
    pass


def _get_client_credential_from_secret_and_update_profile():
    # TODO
    pass


def _init_org(org_id):
    feature_stack_url = profile.current().hcs.url
    payload1 = {
        "geoLocation": {"coordinates": [-122.143936, 37.468319], "type": "Point"},
        "name": "feature-stack-dc",
        "locations": ["EU", "JP", "GB", "IE", "US"],
        "regions": [
            "westus2",
            "westus",
            "centralus",
            "eastus2",
            "eastus",
            "westus3",
            "northeurope",
            "francecentral",
            "francesouth",
            "germanynorth",
            "germanywestcentral",
            "norwaywest",
            "norwayeast",
            "swedencentral",
            "swedensouth",
            "switzerlandnorth",
            "switzerlandwest",
            "uaecentral",
            "uaenorth",
            "uksouth",
            "ukwest",
            "westeurope",
            "japaneast",
            "australiaeast",
            "centralindia",
            "eastasia",
            "italynorth",
            "israelcentral",
            "usgovvirginia",
            "usgovarizona",
            "usgovtexas",
            "chinanorth",
            "chinanorth2",
            "brazilsouth",
            "us-central1",
            "ap-south-1",
            "us-west-1",
            "us-west-2",
            "us-east-1",
        ],
        "providerRegions": {
            "aws": ["ap-south-1", "us-west-1", "us-west-2", "us-east-1"],
            "gcp": ["us-central1"],
            "azure": [
                "westus2",
                "westus",
                "centralus",
                "eastus2",
                "eastus",
                "westus3",
                "northeurope",
                "francecentral",
                "francesouth",
                "germanynorth",
                "germanywestcentral",
                "norwaywest",
                "norwayeast",
                "swedencentral",
                "swedensouth",
                "switzerlandnorth",
                "switzerlandwest",
                "uaecentral",
                "uaenorth",
                "uksouth",
                "ukwest",
                "westeurope",
                "japaneast",
                "australiaeast",
                "centralindia",
                "eastasia",
                "italynorth",
                "israelcentral",
                "usgovvirginia",
                "usgovarizona",
                "usgovtexas",
                "chinanorth",
                "chinanorth2",
                "brazilsouth",
            ],
        },
        "url": feature_stack_url,
        "edgeHubUrl": "https://horizonv2-em.devframe.cp.horizon.omnissa.com",
        "edgeHubRegionCode": "us",
        "dnsUris": [
            "/subscriptions/bfd75b0b-ffce-4cf4-b46b-ecf18410c410/resourceGroups/horizonv2-sg-dev/providers/Microsoft.Network/dnszones/featurestack.devframe.cp.horizon.omnissa.com"
        ],
        "vmHubs": [
            {
                "name": "default",
                "url": "https://dev1b-westus2-cp103a.azcp.horizon.omnissa.com",
                "uagAasFqdn": "https://int.reverseconnect.uag.azcp.horizon.vmware.com",
                "azureRegions": [
                    "westus2",
                    "westus",
                    "centralus",
                    "eastus2",
                    "eastus",
                    "westus3",
                    "northeurope",
                    "francecentral",
                    "francesouth",
                    "germanynorth",
                    "germanywestcentral",
                    "norwaywest",
                    "norwayeast",
                    "swedencentral",
                    "swedensouth",
                    "switzerlandnorth",
                    "switzerlandwest",
                    "uaecentral",
                    "uaenorth",
                    "uksouth",
                    "ukwest",
                    "westeurope",
                    "japaneast",
                    "australiaeast",
                    "centralindia",
                    "eastasia",
                    "italynorth",
                    "israelcentral",
                    "usgovvirginia",
                    "usgovarizona",
                    "usgovtexas",
                    "chinanorth",
                    "chinanorth2",
                    "brazilsouth",
                ],
                "awsRegions": ["ap-south-1", "us-west-1", "us-east-1", "us-west-2"],
                "gcpRegions": ["us-central1"],
                "vmHubGeoPoint": {"type": "Point", "coordinates": [-119.852, 47.233]},
                "privateLinkServiceIds": [
                    "/subscriptions/f8b96ec7-cf11-4ae2-ab75-9e7755a00594/resourceGroups/dev1_westus2/providers/Microsoft.Network/privateLinkServices/dev1b-westus2-cp103a-privatelink"
                ],
                "standByVMHubDetails": {
                    "privateLinkServiceIds": [
                        "/subscriptions/f8b96ec7-cf11-4ae2-ab75-9e7755a00594/resourceGroups/dev1_westus2/providers/Microsoft.Network/privateLinkServices/dev1b-westus2-cp103a-privatelink"
                    ]
                },
                "privateLinkServiceToUse": "PRIMARY",
            }
        ],
    }

    print("--------------------------------")
    print("Create datacenter...")
    print("--------------------------------")
    try:
        ret = org_service.datacenter.create(payload1)
        print(ret)
    except Exception as e:
        print_error(e)

    print("--------------------------------")
    print("Create org details...")
    print("--------------------------------")
    payload2 = {
        "customerName": "nanw-dev",
        "customerType": "INTERNAL",
        "orgId": org_id,
        "wsOneOrgId": "pseudo-ws1-org-id",
    }
    try:
        ret = org_service.details.create(payload2)
        print(ret)
    except Exception as e:
        print_error(e)

    print("--------------------------------")
    print("Create org location mapping...")
    print("--------------------------------")
    payload3 = {"location": "US", "orgId": org_id}
    try:
        ret = org_service.orglocationmapping.create(payload3)
        print(ret)
    except Exception as e:
        print_error(e)


def exec(cmd):
    subprocess.call(cmd.split(" "))


def _restart_services():
    exec("kubectl rollout restart deployment portal-deployment")
    exec("kubectl rollout restart statefulset vmhub-statefulset")
    exec("kubectl rollout restart statefulset connection-service-statefulset")
    exec("kubectl rollout restart statefulset clouddriver-statefulset")
    exec("kubectl rollout restart deployment infra-vsphere-twin-deployment")
