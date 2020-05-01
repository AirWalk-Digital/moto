from __future__ import unicode_literals
import json
import re
from collections import defaultdict

from moto.core.responses import BaseResponse
from moto.core.utils import camelcase_to_underscores
from .models import inspector_backends
# from .exceptions import SNSNotFoundError, InvalidParameterValue
# from .utils import is_e164


class InspectorResponse(BaseResponse):

    @property
    def backend(self):
        return inspector_backends[self.region]

    def create_assessment_target(self):
        name = self._get_param('assessmentTargetName')
        resource_group_arn = self._get_param('resourceGroupArn')
        target = self.backend.create_assessment_target(name, resource_group_arn)

        return json.dumps({'assessmentTargetArn': target.arn})

    def list_assessment_targets(self):
        filter = self._get_param('Filter')
        targets = self.backend.list_assessment_targets(filter=filter)

        return json.dumps({'assessmentTargetArns': targets})

    def create_assessment_template(self):
        assessment_target_arn = self._get_param('assessmentTargetArn')
        assessment_template_name = self._get_param('assessmentTemplateName')
        duration_in_seconds = self._get_param('durationInSeconds')
        rules_package_arns = self._get_param('rulesPackageArns')
        user_attributes_for_findings = self._get_param('userAttributesForFindings')
        template = self.backend.create_assessment_template(assessment_target_arn, assessment_template_name, duration_in_seconds, rules_package_arns, user_attributes_for_findings)
        
        return json.dumps({'assessmentTemplateArn': template.arn})

    def list_assessment_templates(self):
        assessment_target_arns = self._get_param('assessmentTargetArns')
        filter = self._get_param('filter')
        templates = self.backend.list_assessment_templates(assessment_target_arns, filter)

        return json.dumps({'assessmentTemplateArns': [template for template in templates]})

    def create_resource_group(self):
        resource_group_tags = self._get_param('resourceGroupTags')
        resource_group = self.backend.create_resource_group(resource_group_tags)

        return json.dumps({'resourceGroupArn': resource_group.arn})

    def start_assessment_run(self):
        assessment_template_run_arn = self._get_param('assessmentTemplateArn')
        assessment_run_name = self._get_param('assessmentRunName')
        assessment_run = self.backend.start_assessment_run(assessment_template_run_arn, assessment_run_name)
        
        return json.dumps({'assessmentRunArn': assessment_run.arn})

    def list_assessment_runs(self):
        assessment_template_arns = self._get_param('assessmentTemplateArns')
        filter = self._get_param('filter')
        assessment_runs = self.backend.list_assessment_runs(assessment_template_arns, filter)

        return json.dumps({'assessmentRunArns': assessment_runs})