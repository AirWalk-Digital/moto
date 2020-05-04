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
        self.state = 'START_DATA_COLLECTION_PENDING'
        self.completion_time = datetime.datetime.utcnow()
        self.start_time = int(self.completion_time.strftime('%s'))
        self.state_change_time = int(datetime.datetime.utcnow().strftime('%s'))

    @property
    def arn(self):
        return f'{self.assessment_template_arn}/run/0-{self.random_id}'

    def filter_assessment_runs(self, filter, template):
        filter_arns_dict = {}
        arn = self.arn
        for unique_filter in filter.keys():
            filter_arns_dict[unique_filter] = []

            if unique_filter == 'namePattern' and filter[unique_filter] in self.assessment_run_name:
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'states' and self.state in filter[unique_filter]:
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'durationRange' and filter[unique_filter]['minSeconds'] <= template.duration_in_seconds and filter[unique_filter]['maxSeconds'] >= template.duration_in_seconds:
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'rulesPackageArns' and all(rule_arns in filter[unique_filter] for rule_arns in template.rules_package_arns):
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'startTimeRange' and filter[unique_filter]['beginDate'] <= self.start_time: #and filter[unique_filter]['endDate'] >= self.start_time:
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'completionTimeRange' and filter[unique_filter]['beginDate'] <= int((self.completion_time + datetime.timedelta(0,template.duration_in_seconds)).timestamp()) and filter[unique_filter]['endDate'] >= int((self.completion_time + datetime.timedelta(0,template.duration_in_seconds)).timestamp()):
                filter_arns_dict[unique_filter].append(arn)
            elif unique_filter == 'stateChangeTimeRange' and filter[unique_filter]['beginDate'] <= self.state_change_time  and filter[unique_filter]['endDate'] >= self.state_change_time:
                filter_arns_dict[unique_filter].append(arn)
        
        return list(set.intersection(*(set(val) for val in filter_arns_dict.values())))
        
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
        filtered_arns = []
        if assessment_target_arns == None and filter == None:
            return self.assessment_templates

        if assessment_target_arns != None:
            for arn, template in self.assessment_templates.items():
                if template.assessment_target_arn in assessment_target_arns:
                    template_arns.append(template.arn)
            if filter == None:
                return template_arns

        if filter != None:
            filter_arns_dict = {}
            for arn, template in self.assessment_templates.items():
                for unique_filter in filter.keys():
                    if unique_filter not in filter_arns_dict:
                        filter_arns_dict[unique_filter] = []
                    if unique_filter == 'namePattern' and filter[unique_filter] in template.assessment_template_name:
                        filter_arns_dict[unique_filter].append(arn)
                    elif unique_filter == 'durationRange' and filter[unique_filter]['minSeconds'] <= template.duration_in_seconds and filter[unique_filter]['maxSeconds'] >= template.duration_in_seconds:
                        filter_arns_dict[unique_filter].append(arn)
                    elif unique_filter == 'rulesPackageArns' and all(rule_arns in filter[unique_filter] for rule_arns in template.rules_package_arns):
                        filter_arns_dict[unique_filter].append(arn)

            filtered_arns = list(set.intersection(*(set(val) for val in filter_arns_dict.values())))
            if assessment_target_arns == None:
                return filtered_arns
        
        return list(set(filtered_arns).intersection(set(template_arns)))

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
        filtered_arns = []
        print(filter)
        if assessment_template_arns == None and filter == None:
            return self.assessment_templates

        if assessment_template_arns != None:
            for _, run in self.assessment_runs.items():
                if run.assessment_template_arn in assessment_template_arns:
                    run_arns.append(run.arn)
            if filter == None:
                return run_arns

        if filter != None:
            for _, run in self.assessment_runs.items():
                filtered_arns = run.filter_assessment_runs(filter, self.assessment_templates[run.assessment_template_arn])
            if assessment_template_arns == None:
                return filtered_arns

        return list(set(filtered_arns).intersection(set(run_arns)))

    def start_assessment_run(self, assessment_template_arn, assessment_run_name):
        assessment_run = AssessmentRun(self.region_name, assessment_template_arn, assessment_run_name, get_random_id())
        self.assessment_runs[assessment_run.arn] = assessment_run
        return assessment_run

inspector_backends = {}

for region in Session().get_available_regions('inspector'):
    inspector_backends[region] = InspectorBackend(region)