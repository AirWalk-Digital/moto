from __future__ import unicode_literals
import boto3
import six
import json

import sure  # noqa

from botocore.exceptions import ClientError
from moto import mock_inspector
from moto.core import ACCOUNT_ID

@mock_inspector
def test_create_assessment_template():
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

    template = conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    print(conn.list_assessment_templates(assessmentTargetArns=[target['assessmentTargetArn']], filter={'namePattern': 'test', 'durationRange': {'minSeconds': 800, 'maxSeconds': 1000}}))
    template['assessmentTemplateArn'].should.match(f"{target['assessmentTargetArn']}/template/0-")

@mock_inspector
def test_list_assessment_template_with_name_pattern_filter():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(filter={'namePattern': 'test'})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_duration_filter():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(filter={'durationRange': {'minSeconds': 800, 'maxSeconds': 1000}})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_rules_filter():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(filter={'rulesPackageArns': ['rule-arn']})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_multiple_filters():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(filter={'rulesPackageArns': ['rule-arn'], 'durationRange': {'minSeconds': 800, 'maxSeconds': 1000}})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_assessment_target_arns():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(assessmentTargetArns=[target['assessmentTargetArn']])
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_assessment_target_and_filter():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(assessmentTargetArns=[target['assessmentTargetArn']], filter={'rulesPackageArns': ['rule-arn'], 'durationRange': {'minSeconds': 800, 'maxSeconds': 1000}})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_with_multiple_matches():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test2', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates(assessmentTargetArns=[target['assessmentTargetArn']], filter={'rulesPackageArns': ['rule-arn'], 'durationRange': {'minSeconds': 800, 'maxSeconds': 1000}})
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(2)

@mock_inspector
def test_subscribe_to_event():
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
    conn.subscribe_to_event(resourceArn=template['assessmentTemplateArn'], event='ASSESSMENT_RUN_STARTED', topicArn='topic-arn')

@mock_inspector
def test_list_assessment_template_no_filter():
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
    conn.create_assessment_template(assessmentTargetArn=target['assessmentTargetArn'], assessmentTemplateName='test', durationInSeconds=900, rulesPackageArns=['rule-arn'])
    template_results = conn.list_assessment_templates()
    template_results['assessmentTemplateArns'][0].should.match(f"{target['assessmentTargetArn']}/template/0-")
    template_results['assessmentTemplateArns'].should.have.length_of(1)

@mock_inspector
def test_list_assessment_template_no_template():
    conn = boto3.client("inspector", region_name="us-east-1")
    template_results = conn.list_assessment_templates()
    template_results['assessmentTemplateArns'].should.have.length_of(0)
