# Copyright (c) 2024 Cisco and/or its affiliates.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Allen Robel"

import inspect
import json
import logging

from ansible_collections.cisco.dcnm.plugins.module_utils.common.results import \
    Results
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.fabric_defaults import \
    FabricDefaults
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.param_info import \
    ParamInfo
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.ruleset import \
    RuleSet


class VerifyPlaybookParams:
    """
    Verify playbook parameters for a controller fabric.

    VerifyPlaybookParams() uses three sources of information in its
    verification of the user's playbook parameters:

    1. The controller fabric configuration (retrieved from the controller)
    2. The fabric template (retrieved from the controller)
    3. The playbook configuration

    The basic workflow is to retrieve each of these, pass them into
    an instance of VerifyPlaybookParams(), and then call
    VerifyPlaybookParams.commit(), which does the verification.

    Usage:

    # Instantiate the VerifyPlaybookParams class
    verify = VerifyPlaybookParams(ansible_module)

    #---------------------------------------------------------------
    # 1. Retrieve the fabric configuration from controller (here we
    #    use the FabricDetailsByName() class to retrieve the fabric
    #    configuration).  VerifyPlaybookParams() wants only the
    #    nvPairs content of the fabric configuration.
    #---------------------------------------------------------------
    fabric = FabricDetailsByName(ansible_module)
    fabric.refresh()
    fabric.filter = "MyFabric"

    # Add the fabric configuration (if any) to VerifyPlaybookParams()
    if fabric.filtered_data is None:
        # fabric does not exist
        verify.config_controller = None
    else:
        verify.config_controller = fabric.filtered_data["nvPairs"]

    #---------------------------------------------------------------
    # 2. Retrieve the appropriate fabric template (here we use the
    #    TemplateGet() class to retrieve the Easy_Fabric template)
    #---------------------------------------------------------------
    template = TemplateGet(ansible_module)
    template.template_name = "Easy_Fabric"
    template.refresh()

    # Add the template to the VerifyPlaybookParams instance
    verify.template = template.template

    #---------------------------------------------------------------
    # 3. Add the playbook config to the VerifyPlaybookParams instance
    #    typically this is retrieved with get_want() within the
    #    main task module.
    #---------------------------------------------------------------
    verify.config_playbook = playbook_config

    # Perform the verification
    verify.commit()
    """

    def __init__(self, ansible_module):
        self.class_name = self.__class__.__name__
        self.ansible_module = ansible_module

        self.log = logging.getLogger(f"dcnm.{self.class_name}")
        self._ruleset = RuleSet()
        self._fabric_defaults = FabricDefaults()
        self._param_info = ParamInfo()
        self.results = Results()
        self.params_are_valid = set()
        self.bad_params = {}
        self.parameter = None
        self.fabric_name = None

        self.state = self.ansible_module.params["state"]
        msg = "ENTERED VerifyPlaybookParams(): "
        msg += f"state: {self.state}"
        self.log.debug(msg)

        self._build_properties()

    def _build_properties(self):
        """
        self.properties holds property values for the class
        """
        self.properties = {}
        self.properties["config_playbook"] = None
        self.properties["config_controller"] = None
        self.properties["template"] = None

    @property
    def config_controller(self):
        """
        getter: return the controller fabric config to be verified
        setter: set the controller fabric config to be verified
        """
        return self.properties["config_controller"]

    @config_controller.setter
    def config_controller(self, value):
        method_name = inspect.stack()[0][3]
        if value is None:
            self.properties["config_controller"] = {}
            return
        if not isinstance(value, dict):
            msg = f"{self.class_name}.{method_name}: "
            msg += "config_controller must be a dict, or None. "
            msg += f"got {type(value).__name__} for "
            msg += f"value {value}"
            self.ansible_module.fail_json(msg)
        self.properties["config_controller"] = value

    @property
    def config_playbook(self):
        """
        getter: return the playbook config to be verified
        setter: set the playbook config to be verified
        """
        return self.properties["config_playbook"]

    @config_playbook.setter
    def config_playbook(self, value):
        method_name = inspect.stack()[0][3]
        if not isinstance(value, dict):
            msg = f"{self.class_name}.{method_name}: "
            msg += "config_playbook must be a dict. "
            msg += f"got {type(value).__name__} for "
            msg += f"value {value}"
            self.ansible_module.fail_json(msg)
        self.properties["config_playbook"] = value

    @property
    def template(self):
        """
        getter: return the template used to verify the playbook config
        setter: set the template used to verify the playbook config
        """
        return self.properties["template"]

    @template.setter
    def template(self, value):
        method_name = inspect.stack()[0][3]
        if not isinstance(value, dict):
            msg = f"{self.class_name}.{method_name}: "
            msg += "template must be a dict. "
            msg += f"got {type(value).__name__} for "
            msg += f"value {value}"
            self.ansible_module.fail_json(msg, **self.results.failed_result)
        self.properties["template"] = value

    @staticmethod
    def make_boolean(value):
        """
        Return value converted to boolean, if possible.
        Otherwise, return value.

        TODO: This method is duplicated in several other classes.
        TODO: Would be good to move this to a Utility() class.
        """
        if str(value).lower() in ["true", "yes"]:
            return True
        if str(value).lower() in ["false", "no"]:
            return False
        return value

    @staticmethod
    def make_none(value):
        """
        Return None if value is a string representation of a None type
        Otherwise, return value

        TODO: This method is duplicated in several other classes.
        TODO: Would be good to move this to a Utility() class.
        """
        if str(value).lower in ["", "none", "null"]:
            return None
        return value

    @staticmethod
    def make_int(value):
        """
        Return value converted to int, if possible.
        Otherwise, return value.
        """
        # Don't convert boolean values to integers
        if isinstance(value, bool):
            return value
        try:
            return int(value)
        except (ValueError, TypeError):
            return value

    def eval_parameter_rule(self, parameter, param_value, rule) -> bool:
        """
        Evaluate a dependent parameter value against a rule
        from the fabric template.

        Return the result of the evaluation.

        Raise ValueError if the rule does not contain expected keys.
        """
        method_name = inspect.stack()[0][3]

        rule_operator = rule.get("op", None)
        if rule_operator is None:
            msg = f"op not found in parameter {parameter} rule: {rule}"
            raise ValueError(msg)

        rule_value = rule.get("value", None)
        if rule_value is None:
            msg = f"value not found in parameter {parameter} rule: {rule}"
            raise ValueError(msg)

        # While eval() can be dangerous with unknown input, the input
        # we're feeding it is from a known source and has been pretty
        # heavily massaged before it gets here.
        eval_string = f"param_value {rule_operator} rule_value"
        result = eval(eval_string)  # pylint: disable=eval-used

        msg = f"{self.class_name}.{method_name}: "
        msg += "EVAL: "
        msg += f"{param_value} "
        msg += f"{rule_operator} "
        msg += f"{rule_value} "
        msg += f"result: {result}"
        self.log.debug(msg)

        return result

    def controller_param_is_valid(self, parameter, rule) -> bool:
        """
        If the controller fabric config contains the dependent parameter,
        return evaluated result derived from:

        eval(controller_param_value rule_operator rule_value)

        Return None otherwise to remove controller parameter result
        from consideration.

        raise ValueError if "op" or "value" keys are not found in rule
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable
        msg = f"parameter: {parameter}, "
        msg += f"rule: {rule}, "
        self.log.debug(msg)

        # Caller indicated that the fabric does not exist.
        # Return None to remove controller parameter result from consideration.
        if self.config_controller == {}:
            msg = f"Early return: {parameter} fabric does not exist. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        # The controller config does not contain the parameter.
        # Return None to remove controller parameter result from consideration.
        if parameter not in self.config_controller:
            msg = f"Early return: {parameter} not in config_controller. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        parameter_value = self.make_boolean(self.config_controller[parameter])
        return self.eval_parameter_rule(parameter, parameter_value, rule)

    def playbook_param_is_valid(self, parameter, rule) -> bool:
        """
        If the playbook config contains the dependent parameter,
        return evaluated result derived from:

        eval(playbook_param rule_operator rule_value)

        Return None otherwise to remove playbook parameter result
        from consideration.

        raise ValueError if "op" or "value" keys are not found in rule
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        # The playbook config does not contain the parameter.
        # Return None to remove playbook parameter result from consideration.
        if parameter not in self.config_playbook:
            msg = f"Early return: {parameter} not in config_playbook. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        msg = f"parameter: {parameter}, "
        msg += f"rule: {rule}, "
        msg += f"parameter_value: {self.config_playbook[parameter]}"
        self.log.debug(msg)

        parameter_value = self.make_boolean(self.config_playbook[parameter])
        return self.eval_parameter_rule(parameter, parameter_value, rule)

    def default_param_is_valid(self, parameter, rule) -> bool:
        """
        If fabric defaults (from the fabric template) contains the
        dependent parameter, return evaluated result derived from:

        eval(dependent_param_default_value rule_operator rule_value)

        Return None otherwise to remove default parameter result
        from consideration.

        raise ValueError if "op" or "value" keys are not found in rule
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        # The playbook config contains the parameter.
        # Return None to remove default_param result from consideration.
        if parameter in self.config_playbook:
            msg = f"Early return: parameter: {parameter} in config_playbook. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        # The controller config contains the parameter.
        # Return None to remove default_param result from consideration.
        if parameter in self.config_controller:
            msg = f"Early return: parameter: {parameter} in config_controller. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        default_value = None
        try:
            default_value = self._fabric_defaults.parameter(parameter)
        except KeyError:
            # A default value does not exist for parameter.
            # Return None to remove default_param result from consideration.
            msg = f"Early return: parameter: {parameter} has no default value. "
            msg += "Returning None."
            self.log.debug(msg)
            return None

        return self.eval_parameter_rule(parameter, default_value, rule)

    def update_decision_set(self, dependent_param, rule):
        """
        Update the decision set with the aggregate of results from the
        - controller fabric configuration
        - playbook configuration
        - fabric defaults (from the fabric template)
        """
        decision_set = set()
        controller_is_valid = self.controller_param_is_valid(dependent_param, rule)
        playbook_is_valid = self.playbook_param_is_valid(dependent_param, rule)
        default_is_valid = self.default_param_is_valid(dependent_param, rule)

        if controller_is_valid is not None:
            decision_set.add(controller_is_valid)
        if default_is_valid is not None:
            decision_set.add(default_is_valid)
        if playbook_is_valid is not None:
            decision_set.add(playbook_is_valid)
        # If playbook config is not valid, ignore all other results
        if not playbook_is_valid:
            decision_set = {False}

        msg = f"parameter {self.parameter}, "
        msg += f"dependent_param: {dependent_param}, "
        msg += f"rule: {rule}, "
        msg += f"controller_is_valid: {controller_is_valid}, "
        msg += f"playbook_is_valid: {playbook_is_valid}, "
        msg += f"default_is_valid: {default_is_valid}, "
        msg += f"params_are_valid: {self.params_are_valid}, "
        msg += f"decision_set: {decision_set}"
        self.log.debug(msg)

        return decision_set

    def verify_parameter_value(self) -> None:
        """
        Verify a parameter's value against valid choices (if any)
        culled from the template.

        Return if the parameter has no valid choices.

        Call fail_json() if the parameter does not match any of the
        valid choices.
        """
        try:
            param_info = self._param_info.parameter(self.parameter)
        except KeyError as error:
            msg = f"parameter: {self.parameter} not found in template. "
            msg += f"Error detail: {error}"
            self.log.debug(msg)
            return

        msg = "param_info: "
        msg += f"parameter: {self.parameter}, "
        msg += f"{json.dumps(param_info, indent=4, sort_keys=True)}"
        self.log.debug(msg)

        if param_info["choices"] is None:
            return

        playbook_value = self.config_playbook.get(self.parameter)
        # Convert string representations of integers to integers
        playbook_value = self.make_int(playbook_value)

        # If the user specifies 0/1 for False/True, NDFC fails with a 500 error
        # (at least for ADVERTISE_PIP_BGP).  Let's mandate that the user cannot
        # use 0/1 as a substitute for boolean values and fail here instead.
        # NOTE: make_int(), above, should not (and does not) convert boolean
        # values to integers.
        if param_info["type"] == "boolean" and not isinstance(playbook_value, bool):
            msg = f"Parameter: {self.parameter}, "
            msg += f"Invalid value: ({playbook_value}). "
            msg += f"Valid values: {param_info['choices']}"
            self.ansible_module.fail_json(msg, **self.results.failed_result)

        msg = f"Parameter: {self.parameter}, "
        msg += f"playbook_value: {playbook_value}, "
        msg += f"valid values: {param_info['choices']}"
        self.log.debug(msg)

        if playbook_value in param_info["choices"]:
            msg = f"Parameter: {self.parameter}, "
            msg += f"playbook_value ({playbook_value}). "
            msg += f"in valid values: {param_info['choices']}. "
            msg += "Returning."
            self.log.debug(msg)
            return

        msg = f"Parameter: {self.parameter}, "
        msg += f"Invalid value: ({playbook_value}). "
        msg += f"Valid values: {param_info['choices']}"
        self.ansible_module.fail_json(msg, **self.results.failed_result)

    def verify_parameter(self):
        """
        Verify a parameter against the template
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        # self.fabric_name is used in:
        #   - bad_params to help the user identify which
        #     fabric contains the bad parameter(s)
        #   - verify_parameter_value() fail_json message
        self.fabric_name = self.config_playbook.get("FABRIC_NAME", None)
        if self.fabric_name is None:
            msg = "FABRIC_NAME not found in playbook config."
            self.ansible_module.fail_json(msg, **self.results.failed_result)

        self.verify_parameter_value()

        if self.parameter not in self._ruleset.ruleset:
            msg = f"SKIP {self.parameter}: Not in ruleset."
            self.log.debug(msg)
            return

        msg = "self.parameter: "
        msg += f"{self.parameter}, "
        msg += "config_playbook_value: "
        msg += f"{self.config_playbook.get(self.parameter)}, "
        msg += "config_controller_value: "
        msg += f"{self.config_controller.get(self.parameter)}"
        self.log.debug(msg)

        param_rule = self._ruleset.ruleset[self.parameter]

        for dependent_param, rule in param_rule.get("mandatory", {}).items():
            decision_set = self.update_decision_set(dependent_param, rule)

            # bad_params[fabric][param] = <list of bad_param dict>
            if True not in decision_set:
                self.params_are_valid.add(False)

                if self.fabric_name not in self.bad_params:
                    self.bad_params[self.fabric_name] = {}
                if self.parameter not in self.bad_params[self.fabric_name]:
                    self.bad_params[self.fabric_name][self.parameter] = []
                bad_param = {}
                bad_param["fabric_name"] = self.fabric_name
                bad_param["config_param"] = self.parameter
                bad_param["config_value"] = self.config_playbook[self.parameter]
                bad_param["dependent_param"] = dependent_param
                bad_param["dependent_operator"] = rule.get("op")
                bad_param["dependent_value"] = rule.get("value")
                self.bad_params[self.fabric_name][self.parameter].append(bad_param)
            else:
                self.params_are_valid.add(True)

        msg = f"self.params_are_valid: {self.params_are_valid}"
        self.log.debug(msg)

    def validate_commit_parameters(self):
        """
        fail_json if required parameters are not set
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable
        if self.config_controller is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += "instance.config_controller "
            msg += "must be set prior to calling commit."
            self.ansible_module.fail_json(msg, **self.results.failed_result)

        if self.config_playbook is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += "instance.config_playbook "
            msg += "must be set prior to calling commit."
            self.ansible_module.fail_json(msg, **self.results.failed_result)

        if self.template is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += "instance.template "
            msg += "must be set prior to calling commit."
            self.ansible_module.fail_json(msg, **self.results.failed_result)

    def update_fabric_defaults(self):
        """
        Update fabric parameter default values based on
        the fabric template
        """
        try:
            self._fabric_defaults.template = self.template
        except ValueError as error:
            msg = f"{error}"
            self.log.debug(msg)
            self.ansible_module.fail_json(msg, **self.results.failed_result)
        try:
            self._fabric_defaults.refresh()
        except ValueError as error:
            msg = f"{error}"
            self.log.debug(msg)
            self.ansible_module.fail_json(msg, **self.results.failed_result)

    def update_param_info(self):
        """
        Update the fabric parameter info based on the fabric template
        """
        self._param_info.template = self.template
        self._param_info.refresh()

        msg = "ZZZ: self._param_info.info: "
        msg += f"{json.dumps(self._param_info.info, indent=4, sort_keys=True)}"
        self.log.debug(msg)

    def update_ruleset(self):
        """
        Update the fabric parameter ruleset based on the fabric template
        """
        self._ruleset.template = self.template
        self._ruleset.refresh()

        msg = "self._ruleset.ruleset: "
        msg += f"{json.dumps(self._ruleset.ruleset, indent=4, sort_keys=True)}"
        self.log.debug(msg)

    def commit(self):
        """
        verify the config against the retrieved template
        """
        method_name = inspect.stack()[0][3]  # pylint: disable=unused-variable

        self.validate_commit_parameters()
        self.update_ruleset()
        self.update_fabric_defaults()
        self.update_param_info()

        msg = "self.config_playbook: "
        msg += f"{json.dumps(self.config_playbook, indent=4, sort_keys=True)}"
        self.log.debug(msg)

        self.params_are_valid = set()
        for self.parameter in self.config_playbook:
            self.verify_parameter()
        if False not in self.params_are_valid:
            return

        msg = "The following parameter(value) combination(s) are invalid "
        msg += "and need to be reviewed: "
        # bad_params[fabric][param] = <list of bad param dict>
        for fabric_name, fabric_dict in self.bad_params.items():
            msg += f"Fabric: {fabric_name}, "
            for _, bad_param_list in fabric_dict.items():
                for bad_param in bad_param_list:
                    config_param = bad_param.get("config_param")
                    config_value = bad_param.get("config_value")
                    dependent_param = bad_param.get("dependent_param")
                    dependent_operator = bad_param.get("dependent_operator")
                    dependent_value = bad_param.get("dependent_value")
                    msg += f"{config_param}({config_value}) requires "
                    msg += f"{dependent_param} {dependent_operator} {dependent_value}, "
                    msg += f"{dependent_param} valid values: {self._param_info.info[dependent_param]['choices']}. "
            msg.rstrip(", ")
        self.log.debug(msg)
        self.ansible_module.fail_json(msg, **self.results.failed_result)
