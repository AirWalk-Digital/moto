from __future__ import unicode_literals
import boto3
import six
import json

import sure  # noqa

from botocore.exceptions import ClientError
from moto import mock_inspector
from moto.core import ACCOUNT_ID

@mock_inspector
def test_create_resource_group():
    conn = boto3.client("inspector", region_name="us-east-1")
    resource_group_tags = {
        'resourceGroupTags': [
                {
                    'key':'test',
                    'value': 'True'
                }
            ]
    }
    resource_group = conn.create_resource_group(**resource_group_tags)
    resource_group.should.look_like(f'arn:aws:inspector:us-east-1:{ACCOUNT_ID}:resourcegroup/0-')