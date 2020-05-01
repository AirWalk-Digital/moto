from __future__ import unicode_literals

import re
import json
import datetime

from boto3 import Session
from moto.compat import OrderedDict
from moto.iam.models import ACCOUNT_ID
from .utils import get_random_id
from moto.core import BaseBackend, BaseModel

from .exceptions import (
    InvalidFilterKey,
    InvalidFilterValue
)

class AssessmentTarget(BaseModel):
    def __init__(self, region, assessment_target_name, resource_group_arn, random_id):
        self.region = region
        self.assessment_target_name = assessment_target_name
        self.resource_group_arn = resource_group_arn
        self.random_id = random_id

    @property
    def arn(self):
        return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:target/0-{self.random_id}'

class AssessmentTemplate(BaseModel):
    def __init__(self, region, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings, random_id):
        self.region = region
        self.assessment_target_arn = assessment_target_arn
        self.assessment_template_name = assessment_template_name
        self.duration_in_seconds = duration_in_seconds
        self.rules_package_arns = rules_package_arns
        self.user_attributes_for_findings = user_attributes_for_findings
        self.random_id = random_id
    @property
    def arn(self):
        # return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:target/0-{self.id_generator}/template/0-{self.id_generator}'
        return f'{self.assessment_target_arn}/template/0-{self.random_id}'

class ResourceGroup(BaseModel):
    def __init__(self, region, resource_group_tags, random_id):
        self.region = region
        self.resource_group_tags = resource_group_tags
        self.random_id = random_id

    @property
    def arn(self):
        return f'arn:aws:inspector:{self.region}:{ACCOUNT_ID}:resourcegroup/0-{self.random_id}'

class AssessmentRun(BaseModel):
    def __init__(self, region, assessment_template_arn, assessment_run_name, random_id):
        self.region = region
        self.assessment_template_arn = assessment_template_arn
        self.assessment_run_name = assessment_run_name
        self.random_id = random_id

    @property
    def arn(self):
        return f'{self.assessment_template_arn}/run/0-{self.random_id}'
class InspectorBackend(BaseBackend):
    def __init__(self, region_name):
        super(InspectorBackend, self).__init__()
        self.region_name = region_name
        self.assessment_targets = OrderedDict()
        self.assessment_templates = OrderedDict()
        self.assessment_runs = OrderedDict()
        self.resource_groups = OrderedDict()

    def reset(self):
        region_name = self.region_name
        self.__dict__ = {}
        self.__init__(region_name)

    def create_assessment_target(self, assessment_target_name, resource_group_arn=None):
        target = AssessmentTarget(self.region_name, assessment_target_name, resource_group_arn, get_random_id())
        self.assessment_targets[target.arn] = target
        return target

    def create_assessment_template(self, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings):
        template = AssessmentTemplate(self.region_name, assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings, get_random_id())
        self.assessment_templates[template.arn] = template
        return template

    def create_resource_group(self, resource_group_tags):
        for resource_group_tag in resource_group_tags:
            if 'key' not in resource_group_tag or 'value' not in resource_group_tag:
                raise InvalidFilterKey(
                    'Key and Value required.'
                )
    
        resource_group = ResourceGroup(self.region_name, resource_group_tags, get_random_id())
        self.resource_groups[resource_group.arn] = resource_group
        return resource_group

    def list_assessment_templates(self, assessment_target_arns, filter):
        template_arns = []
        if assessment_target_arns == None and filter == None:
            return self.assessment_templates

        if assessment_target_arns != None:
            for template in self.assessment_templates.items():
                if template.arn in assessment_target_arns:
                    template_arns.append(template.arn)
                
        if filter != None:
            named_templates = []
            duration_template = []
            rules_templates = []
            for arn, template in self.assessment_templates.items():
                for unique_filter in filter.keys():
                    if unique_filter == 'namePattern' and filter[unique_filter] in template.assessment_template_name:
                        named_templates.append(arn)
                    elif unique_filter == 'durationRange' and filter[unique_filter]['minSeconds'] >= template.duration_in_seconds and filter[unique_filter]['maxSeconds'] <= template.duration_in_seconds:
                        duration_template.append(arn)
                    elif unique_filter == 'rulesPackageArns' and all(rule_arns in filter[unique_filter] for rule_arns in template.rules_package_arns):
                        rules_templates.append(arn)
        
            filtered_arns = list(set(named_templates + rules_templates + duration_template))
        
        return list(set(filtered_arns + template_arns))

    def list_assessment_targets(self, filter):

        if filter != None:
            if 'assessmentTargetNamePattern' not in filter or len(filter.values()) > 1:
                raise InvalidFilterValue('Only assessmentTargetNamePattern allowed as filter.')
            targets = []
            for target in self.assessment_targets.items():
                if filter['assessmentTargetNamePattern'] in target.assessment_target_name:
                    targets.append(target)
            return targets

        return [target for target in self.assessment_targets]

    def list_assessment_runs(self, assessment_template_arns, filter):
        run_arns = []
        if assessment_template_arns == None and filter == None:
            return self.assessment_templates

        if assessment_template_arns != None:
            for _, template in self.assessment_templates.items():
                if template.arn in assessment_template_arns:
                    run_arns.append(template.arn)

        return run_arns
        

    def start_assessment_run(self, assessment_template_arn, assessment_run_name):
        assessment_run = AssessmentRun(self.region_name, assessment_template_arn, assessment_run_name, get_random_id())
        self.assessment_runs[assessment_run.arn] = assessment_run
        return assessment_run

inspector_backends = {}

for region in Session().get_available_regions('inspector'):
    inspector_backends[region] = InspectorBackend(region)