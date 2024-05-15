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
# pylint: disable=line-too-long
from __future__ import absolute_import, division, print_function

__metaclass__ = type
__author__ = "Allen Robel"

import inspect
import logging

from ansible_collections.cisco.dcnm.plugins.module_utils.common.api.v1.config_template import \
    ConfigTemplate
from ansible_collections.cisco.dcnm.plugins.module_utils.fabric.fabric_types import \
    FabricTypes


class Templates(ConfigTemplate):
    """
    ## V1 API Fabrics - ConfigTemplate().Templates()

    ### Description
    Common methods and properties for Templates() subclasses.

    ### Path
    -   ``/configtemplate/rest/config/templates``
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"dcnm.{self.class_name}")
        self.fabric_types = FabricTypes()

        self.rest_config_templates = f"{self.config_template}/rest/config/templates"
        msg = f"ENTERED api.v1.ConfigTemplate.{self.class_name}"
        self.log.debug(msg)
        self._build_properties()

    def _build_properties(self):
        """
        - Set the fabric_name property.
        """
        self.properties["template_name"] = None

    @property
    def path_template_name(self):
        """
        - Endpoint for template retrieval.
        - Raise ``ValueError`` if template_name is not set.
        """
        method_name = inspect.stack()[0][3]
        if self.template_name is None and "template_name" in self.required_properties:
            msg = f"{self.class_name}.{method_name}: "
            msg += "template_name must be set prior to accessing path."
            raise ValueError(msg)
        return f"{self.rest_config_templates}/{self.template_name}"

    @property
    def template_name(self):
        """
        - getter: Return the template_name.
        - setter: Set the template_name.
        - setter: Raise ``ValueError`` if template_name is not a string.
        """
        return self.properties["template_name"]

    @template_name.setter
    def template_name(self, value):
        method_name = inspect.stack()[0][3]
        if value not in self.fabric_types.valid_fabric_template_names:
            msg = f"{self.class_name}.{method_name}: "
            msg += f"Invalid template_name: {value}. "
            msg += "Expected one of: "
            msg += f"{', '.join(self.fabric_types.valid_fabric_template_names)}."
            raise ValueError(msg)
        self.properties["template_name"] = value


class EpTemplate(Templates):
    """
    ## V1 API - Templates().EpTemplate()

    ### Description
    Return endpoint information.

    ### Raises
    -   ``ValueError``: If template_name is not set.
    -   ``ValueError``: If template_name is not a valid fabric template name.

    ### Path
    -   ``/rest/config/templates/{template_name}``

    ### Verb
    -   GET

    ### Parameters
    - template_name: string
        - set the ``template_name`` to be used in the path
        - required
    -   path: retrieve the path for the endpoint
    -   verb: retrieve the verb for the endpoint

    ### Usage
    ```python
    instance = EpTemplate()
    instance.template_name = "Easy_Fabric"
    path = instance.path
    verb = instance.verb
    ```
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"dcnm.{self.class_name}")
        self.required_properties.add("template_name")
        self._build_properties()
        msg = f"ENTERED api.v1.ConfigTemplate.Templates.{self.class_name}"
        self.log.debug(msg)

    def _build_properties(self):
        super()._build_properties()
        self.properties["verb"] = "GET"

    @property
    def path(self):
        """
        - Endpoint for template retrieval.
        - Raise ``ValueError`` if template_name is not set.
        """
        return self.path_template_name


class EpTemplates(Templates):
    """
    ## V1 API - Templates().EpTemplates()

    ### Description
    Return endpoint information.

    ### Raises
    -   None

    ### Path
    -   ``/rest/config/templates``

    ### Verb
    -   GET

    ### Parameters
    -   path: retrieve the path for the endpoint
    -   verb: retrieve the verb for the endpoint

    ### Usage
    ```python
    instance = EpTemplates()
    path = instance.path
    verb = instance.verb
    ```
    """

    def __init__(self):
        super().__init__()
        self.class_name = self.__class__.__name__
        self.log = logging.getLogger(f"dcnm.{self.class_name}")
        self._build_properties()
        msg = f"ENTERED api.v1.ConfigTemplate.Templates.{self.class_name}"
        self.log.debug(msg)

    def _build_properties(self):
        super()._build_properties()
        self.properties["verb"] = "GET"

    @property
    def path(self):
        """
        - Endpoint for template retrieval.
        - Raise ``ValueError`` if template_name is not set.
        """
        return self.rest_config_templates
