from __future__ import unicode_literals
import boto3
import six
import json

import sure  # noqa

from botocore.exceptions import ClientError
from moto import mock_inspector
from moto.core import ACCOUNT_ID

@mock_inspector
def test_create_assessment_target():
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
    target = conn.create_assessment_target(assessmentTargetName='test', resourceGroupArn=resource_group['resourceGroupArn'])
    target['assessmentTargetArn'].should.match(f'arn:aws:inspector:us-east-1:{ACCOUNT_ID}:target/0-')

    targets = conn.list_assessment_targets()
    targets['assessmentTargetArns'].should.have.length_of(1)

