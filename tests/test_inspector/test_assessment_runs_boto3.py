from __future__ import unicode_literals
import boto3
import six
import json

import sure  # noqa

from botocore.exceptions import ClientError
from moto import mock_inspector
from moto.core import ACCOUNT_ID

@mock_inspector
def test_start_assessment_run():
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

    template = conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    assessment_run = conn.start_assessment_run(assessmentTemplateArn=template['assessmentTemplateArn'], assessmentRunName='test')
    conn.list_assessment_runs(assessmentTemplateArns=[template['assessmentTemplateArn']])
    assessment_run['assessmentRunArn'].should.match(f"{template['assessmentTemplateArn']}/run/0-")

