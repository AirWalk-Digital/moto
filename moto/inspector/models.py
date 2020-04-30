from __future__ import unicode_literals

import re
import json
import datetime
import string
import random

from boto3 import Session
from moto.compat import OrderedDict
from moto.iam.models import ACCOUNT_ID

from moto.core import BaseBackend, BaseModel

from .exceptions import (
    InvalidFilterKey,
    InvalidFilterValue
)

class AssessmentTarget(BaseModel):
    def __init__(self, region, assessment_target_name, resource_group_arn):
        self.region = region
        self.assessment_target_name = assessment_target_name
        self.resource_group_arn = resource_group_arn

    @property
    def arn(self):
        return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:target/0-{id_generator}'

class AssessmentTemplate(BaseModel):
    def __init__(self, region, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings):
        self.region = region
        self.assessment_target_arn = assessment_target_arn
        self.assessment_template_name = assessment_template_name
        self.duration_in_seconds = duration_in_seconds
        self.rules_package_arns = rules_package_arns
        self.user_attributes_for_findings = user_attributes_for_findings

    @property
    def arn(self):
        # return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:target/0-{self.id_generator}/template/0-{self.id_generator}'
        return f'{self.assessment_target_arn}/template/0-{id_generator}'

class ResourceGroup(BaseModel):
    def __init__(self, region, resource_group_tags):
        self.region = region
        self.resource_group_tags = resource_group_tags

    @property
    def arn(self):
        return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:resourcegroup/0-{id_generator}'
        

class InspectorBackend(BaseBackend):
    def __init__(self, region_name):
        self.region_name = region_name
        self.assessment_targets = OrderedDict()
        self.assessment_templates = OrderedDict()
        self.resource_groups = OrderedDict()

    def create_assessment_target(self, assessment_target_name, resource_group_arn=None):
        target = AssessmentTarget(self.region_name, assessment_target_name, resource_group_arn)
        self.assessment_targets[target.arn] = target
        return target

    def create_assessment_template(self, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings):
        template = AssessmentTemplate(self.region_name, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings)
        self.assessment_templates[template.arn] = template
        return template

    def create_resource_group(self, resource_group_tags):
        for resource_group_tag in resource_group_tags:
            if 'key' not in resource_group_tag or 'value' not in resource_group_tag:
                raise InvalidFilterKey(
                    'Key and Value required.'
                )
    
        resource_group = ResourceGroup(self.region_name, resource_group_tags)
        self.resource_groups[resource_group.arn] = resource_group
        return resource_group

    def list_assessment_templates(self, assessment_target_arns, filter):
        template_arns = []
        if assessment_target_arns != None:
            for template in self.assessment_templates.items():
                if template.arn in assessment_target_arns:
                    template_arns.append(template.arn)

        # if filter != None:
        #     for template in self.assessment_templates.items():
        #         try:
        #             if filter['namePattern'] in template.assessment_template_name:
        #                 template_arns.append(template.arn)
                    
        #             if 

        return template_arns

    def list_assessment_targets(self, filter=None):
        if 'assessmentTargetNamePattern' not in filter or len(filter.values()) > 1:
            raise InvalidFilterValue(
                    'Only assessmentTargetNamePattern allowed as filter.'
                )

        if filter != None:
            targets = []
            for target in self.assessment_targets.items():
                if filter['assessmentTargetNamePattern'] in target.assessment_target_name:
                    targets.append(target)
            return {'assessmentTargetArns': targets}
        return [target.arn for target in self.assessment_targets.items()]

inspector_backends = {}

def id_generator(self, size=8, chars=string.ascii_letters + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))

for region in Session.get_available_regions('inspector'):
    inspector_backends[region] = InspectorBackend(region)