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

import traceback
from datetime import datetime
from time import sleep

import click
from hcs_core.ctxp.extension import ensure_extension


@click.group(hidden=True)
def test():
    """Test."""


@test.command()
def demo():
    ensure_extension("hcs-ext-demo")
    import hcs_ext_demo.main as demo

    print(demo.description())


@test.command()
def auth_refresh():
    import json

    import hcs_core.sglib.cli_options as cli

    from hcs_cli.service.org_service import details

    org_id = cli.get_org_id()
    try:
        while True:
            org_details = details.get(org_id)
            print(datetime.now())
            print(json.dumps(org_details))
            sleep(10)
    except Exception as e:
        traceback.print_exc()


@test.command()
def env():
    import os

    return os.environ.get("HCS_TIMEOUT")
