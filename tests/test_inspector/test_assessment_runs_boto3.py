from __future__ import unicode_literals
import boto3
import six
import json

import datetime
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
    conn.list_assessment_runs(assessmentTemplateArns=[template['assessmentTemplateArn']])['assessmentRunArns'][0].should.match(f"{template['assessmentTemplateArn']}/run/0-")
    assessment_run['assessmentRunArn'].should.match(f"{template['assessmentTemplateArn']}/run/0-")

@mock_inspector
def test_list_assessment_runs_arns_and_filter():
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
    conn.start_assessment_run(assessmentTemplateArn=template['assessmentTemplateArn'], assessmentRunName='test')
    conn.list_assessment_runs(assessmentTemplateArns=[template['assessmentTemplateArn']], filter={'namePattern': 'test'})['assessmentRunArns'][0].should.match(f"{template['assessmentTemplateArn']}/run/0-")

@mock_inspector
def test_list_assessment_runs_all_filters():
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
    conn.start_assessment_run(assessmentTemplateArn=template['assessmentTemplateArn'], assessmentRunName='test')
    start_time = 1588604930
    end_time = datetime.datetime.utcnow()
    filters = {
            'namePattern': 'test',
            'states': ['START_DATA_COLLECTION_PENDING'],
            'durationRange': {
                'minSeconds': 800,
                'maxSeconds': 900
            },
            'rulesPackageArns': ['rule-arn'],
            'startTimeRange': {
                'beginDate': start_time,
                'endDate': end_time
            },
            'completionTimeRange': {
                'beginDate': start_time,
                'endDate': datetime.datetime.utcnow() + datetime.timedelta(0, 4000)
            },
            'stateChangeTimeRange': {
                'beginDate': start_time,
                'endDate': datetime.datetime.utcnow() + datetime.timedelta(0, 900)
            }
    }
    conn.list_assessment_runs(assessmentTemplateArns=[template['assessmentTemplateArn']], filter=filters)['assessmentRunArns'][0].should.match(f"{template['assessmentTemplateArn']}/run/0-")
