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

# See the following regarding *_fixture imports
# https://pylint.pycqa.org/en/latest/user_guide/messages/warning/redefined-outer-name.html
# Due to the above, we also need to disable unused-import
# pylint: disable=unused-import
# Some fixtures need to use *args to match the signature of the function they are mocking
# pylint: disable=protected-access

from __future__ import absolute_import, division, print_function

__metaclass__ = type

__copyright__ = "Copyright (c) 2024 Cisco and/or its affiliates."
__author__ = "Allen Robel"

import copy
import inspect

import pytest
from ansible_collections.cisco.dcnm.plugins.module_utils.common.response_handler import \
    ResponseHandler
from ansible_collections.cisco.dcnm.plugins.module_utils.common.rest_send_v2 import \
    RestSend
from ansible_collections.cisco.dcnm.plugins.module_utils.common.sender_file import \
    Sender
from ansible_collections.cisco.dcnm.tests.unit.module_utils.common.common_utils import (
    ResponseGenerator, does_not_raise)

PARAMS = {"state": "merged", "check_mode": False}


def responses():
    """
    Dummy coroutine for ResponseGenerator()

    See e.g. test_rest_send_v2_00800
    """
    yield {}


def test_rest_send_v2_00000() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   __init__()

    ### Summary
    -   Verify class properties are initialized to expected values
    """
    #  pylint: disable=use-implicit-booleaness-not-comparison
    with does_not_raise():
        instance = RestSend(PARAMS)
    assert instance.params == PARAMS
    assert instance._check_mode is False
    assert instance._path is None
    assert instance._payload is None
    assert instance._response == []
    assert instance._response_current == {}
    assert instance._response_handler is None
    assert instance._result == []
    assert instance._result_current == {}
    assert instance._send_interval == 5
    assert instance._sender is None
    assert instance._timeout == 300
    assert instance._unit_test is False
    assert instance._verb is None

    assert instance.saved_check_mode is None
    assert instance.saved_timeout is None
    assert instance._valid_verbs == {"GET", "POST", "PUT", "DELETE"}
    assert instance.check_mode == PARAMS.get("check_mode", None)
    assert instance.state == PARAMS.get("state", None)


def test_rest_send_v2_00100() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   _verify_commit_parameters()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``_verify_commit_parameters()`` raises ``ValueError``
    due to ``path`` not being set.

    ### Setup - Code
    -   RestSend() is initialized.
    -   RestSend().path is NOT set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   RestSend()._verify_commit_parameters() raises ``ValueError``.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)
        instance.sender = Sender()
        instance.response_handler = ResponseHandler()
        instance.verb = "GET"

    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details:\s+"
    match += r"RestSend\._verify_commit_parameters:\s+"
    match += r"path must be set before calling commit\(\)."
    with pytest.raises(ValueError, match=match):
        instance.commit()


def test_rest_send_v2_00110() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   _verify_commit_parameters()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``_verify_commit_parameters()`` raises ``ValueError``
    due to ``response_handler`` not being set.

    ### Setup - Code
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is NOT set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   RestSend()._verify_commit_parameters() raises ``ValueError``.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)
        instance.path = "/foo/path"
        instance.sender = Sender()
        instance.verb = "GET"

    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details:\s+"
    match += r"RestSend\._verify_commit_parameters:\s+"
    match += r"response_handler must be set before calling commit\(\)."
    with pytest.raises(ValueError, match=match):
        instance.commit()


def test_rest_send_v2_00120() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   _verify_commit_parameters()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``_verify_commit_parameters()`` raises ``ValueError``
    due to ``sender`` not being set.

    ### Setup - Code
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is NOT set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   RestSend()._verify_commit_parameters() raises ``ValueError``.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.verb = "GET"

    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details:\s+"
    match += r"RestSend\._verify_commit_parameters:\s+"
    match += r"sender must be set before calling commit\(\)."
    with pytest.raises(ValueError, match=match):
        instance.commit()


def test_rest_send_v2_00130() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   _verify_commit_parameters()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``_verify_commit_parameters()`` raises ``ValueError``
    due to ``verb`` not being set.

    ### Setup - Code
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is NOT set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   RestSend()._verify_commit_parameters() raises ``ValueError``.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = Sender()

    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details:\s+"
    match = r"RestSend\._verify_commit_parameters:\s+"
    match += r"verb must be set before calling commit\(\)\."
    with pytest.raises(ValueError, match=match):
        instance.commit()


def test_rest_send_v2_00200() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   commit_check_mode()
            -   commit()

    ### Summary
    Verify ``commit_check_mode()`` happy path when
    ``verb`` is "GET".

    ### Setup - Code
    -   PARAMS["check_mode"] is set to True
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   The following are updated to expected values:
            -   ``response``
            -   ``response_current``
            -   ``result``
            -   ``result_current``
    -   result_current["found"] is True
    """
    params = copy.copy(PARAMS)
    params["check_mode"] = True

    with does_not_raise():
        instance = RestSend(params)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = Sender()
        instance.verb = "GET"
        instance.commit()
    assert instance.response_current["CHECK_MODE"] == instance.check_mode
    assert (
        instance.response_current["DATA"] == "[simulated-check-mode-response:Success]"
    )
    assert instance.response_current["MESSAGE"] == "OK"
    assert instance.response_current["METHOD"] == instance.verb
    assert instance.response_current["REQUEST_PATH"] == instance.path
    assert instance.response_current["RETURN_CODE"] == 200
    assert instance.result_current["success"] is True
    assert instance.result_current["found"] is True
    assert instance.response == [instance.response_current]
    assert instance.result == [instance.result_current]


def test_rest_send_v2_00210() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   commit_check_mode()
            -   commit()

    ### Summary
    Verify ``commit_check_mode()`` happy path when
    ``verb`` is "POST".

    ### Setup - Code
    -   PARAMS["check_mode"] is set to True
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   The following are updated to expected values:
            -   ``response``
            -   ``response_current``
            -   ``result``
            -   ``result_current``
    -   result_current["changed"] is True
    """
    params = copy.copy(PARAMS)
    params["check_mode"] = True

    with does_not_raise():
        instance = RestSend(params)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = Sender()
        instance.verb = "POST"
        instance.commit()
    assert instance.response_current["CHECK_MODE"] == instance.check_mode
    assert (
        instance.response_current["DATA"] == "[simulated-check-mode-response:Success]"
    )
    assert instance.response_current["MESSAGE"] == "OK"
    assert instance.response_current["METHOD"] == instance.verb
    assert instance.response_current["REQUEST_PATH"] == instance.path
    assert instance.response_current["RETURN_CODE"] == 200
    assert instance.result_current["success"] is True
    assert instance.result_current["changed"] is True
    assert instance.response == [instance.response_current]
    assert instance.result == [instance.result_current]


def test_rest_send_v2_00220(monkeypatch) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   commit_check_mode()
            -   commit()

    ### Summary
    Verify ``commit_check_mode()`` sad path when
    ``response_handler.commit()`` raises ``ValueError``.

    ### Setup - Code
    -   PARAMS["check_mode"] is set to True
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.
    -   ResponseHandler().commit() is patched to raise ``ValueError``.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   response_handler.commit() raises ``ValueError``
    -   commit_check_mode() re-raises ``ValueError``
    -   commit() re-raises ``ValueError``
    """
    params = copy.copy(PARAMS)
    params["check_mode"] = True

    class MockResponseHandler:
        """
        Mock ``ResponseHandler().commit()`` to raise ``ValueError``.
        """

        def __init__(self):
            self._verb = "GET"

        def commit(self):
            """
            Raise ``ValueError``.
            """
            raise ValueError("Error in ResponseHandler.")

        @property
        def implements(self):
            """
            Return expected interface string.
            """
            return "response_handler_v1"

        @property
        def verb(self):
            """
            get/set verb.
            """
            return self._verb

        @verb.setter
        def verb(self, value):
            self._verb = value

    with does_not_raise():
        instance = RestSend(params)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = Sender()
        instance.verb = "POST"

    monkeypatch.setattr(instance, "response_handler", MockResponseHandler())
    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details: Error in ResponseHandler\."
    with pytest.raises(ValueError, match=match):
        instance.commit()


def test_rest_send_v2_00300() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``commit_normal_mode()`` happy path when
    ``verb`` is "POST" and ``payload`` is set.

    ### Setup - Code
    -   PARAMS["check_mode"] is set to False
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   RestSend().sender is set.
    -   RestSend().verb is set.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   The following are updated to expected values:
            -   ``response``
            -   ``response_current``
            -   ``result``
            -   ``result_current``
    -   result_current["changed"] is True
    """
    params = copy.copy(PARAMS)
    params["check_mode"] = False

    def responses_00300():
        yield {
            "METHOD": "POST",
            "MESSAGE": "OK",
            "REQUEST_PATH": "/foo/path",
            "RETURN_CODE": 200,
            "DATA": "simulated_data",
            "CHECK_MODE": False,
        }

    sender = Sender()
    sender.gen = ResponseGenerator(responses_00300())
    with does_not_raise():
        instance = RestSend(params)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = sender
        instance.verb = "POST"
        instance.payload = {}
        instance.commit()
    assert instance.response_current["CHECK_MODE"] == instance.check_mode
    assert instance.response_current["DATA"] == "simulated_data"
    assert instance.response_current["MESSAGE"] == "OK"
    assert instance.response_current["METHOD"] == instance.verb
    assert instance.response_current["REQUEST_PATH"] == instance.path
    assert instance.response_current["RETURN_CODE"] == 200
    assert instance.result_current["success"] is True
    assert instance.result_current["changed"] is True
    assert instance.response == [instance.response_current]
    assert instance.result == [instance.result_current]


def test_rest_send_v2_00310() -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   commit_normal_mode()
            -   commit()

    ### Summary
    Verify ``commit_normal_mode()`` sad path when
    ``Sender().commit()`` raises ``ValueError``.

    ### Setup - Code
    -   PARAMS["check_mode"] is set to False
    -   RestSend() is initialized.
    -   RestSend().path is set.
    -   RestSend().response_handler is set.
    -   Sender().raise_method is set to "commit".
    -   Sender().raise_exception is set to ValueError.
    -   RestSend().sender is set.
    -   RestSend().verb is set.


    ### Setup - Data
    None

    ### Trigger
    -   RestSend().commit() is called.

    ### Expected Result
    -   Sender().commit() raises ``ValueError``
    -   commit_normal_mode() re-raises ``ValueError``
    -   commit() re-raises ``ValueError``
    """
    params = copy.copy(PARAMS)
    params["check_mode"] = False

    def responses_00300():
        yield {
            "METHOD": "POST",
            "MESSAGE": "OK",
            "REQUEST_PATH": "/foo/path",
            "RETURN_CODE": 200,
            "DATA": "simulated_data",
            "CHECK_MODE": False,
        }

    sender = Sender()
    sender.gen = ResponseGenerator(responses_00300())
    sender.raise_method = "commit"
    sender.raise_exception = ValueError

    with does_not_raise():
        instance = RestSend(params)
        instance.path = "/foo/path"
        instance.response_handler = ResponseHandler()
        instance.sender = sender
        instance.verb = "POST"
        instance.payload = {}
    match = r"RestSend\.commit:\s+"
    match += r"Error during commit\.\s+"
    match += r"Error details: Sender\.commit: Simulated ValueError\."
    with pytest.raises(ValueError, match=match):
        instance.commit()


MATCH_00500 = r"RestSend\.check_mode:\s+"
MATCH_00500 += r"check_mode must be a boolean\.\s+"
MATCH_00500 += r"Got.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_00500)),
        ([10], True, pytest.raises(TypeError, match=MATCH_00500)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_00500)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_00500)),
        (None, True, pytest.raises(TypeError, match=MATCH_00500)),
        (False, False, does_not_raise()),
        (True, False, does_not_raise()),
    ],
)
def test_rest_send_v2_00500(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   check_mode.setter

    ### Summary
    Verify ``check_mode.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to boolean.

    ### Setup - Code
    -   PARAMS["check_mode"] is set to True
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().check_mode is reset using various types.

    ### Expected Result
    -   ``check_mode`` raises TypeError for non-boolean inputs.
    -   ``check_mode`` accepts boolean values.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.check_mode = value
    if does_raise is False:
        assert instance.check_mode == value


MATCH_00600 = r"RestSend\.response_current:\s+"
MATCH_00600 += r"response_current must be a dict\.\s+"
MATCH_00600 += r"Got.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_00600)),
        ([10], True, pytest.raises(TypeError, match=MATCH_00600)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_00600)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_00600)),
        (None, True, pytest.raises(TypeError, match=MATCH_00600)),
        (False, True, pytest.raises(TypeError, match=MATCH_00600)),
        (True, True, pytest.raises(TypeError, match=MATCH_00600)),
        ({"RESULT_CODE": 200}, False, does_not_raise()),
    ],
)
def test_rest_send_v2_00600(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   response_current.setter

    ### Summary
    Verify ``response_current.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to dict.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().response_current is reset using various types.

    ### Expected Result
    -   ``response_current`` raises TypeError for non-dict inputs.
    -   ``response_current`` accepts dict values.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.response_current = value
    if does_raise is False:
        assert instance.response_current == value


MATCH_00700 = r"RestSend\.response:\s+"
MATCH_00700 += r"response must be a dict\.\s+"
MATCH_00700 += r"Got type.*,\s+"
MATCH_00700 += r"Value:\s+.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_00700)),
        ([10], True, pytest.raises(TypeError, match=MATCH_00700)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_00700)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_00700)),
        (None, True, pytest.raises(TypeError, match=MATCH_00700)),
        (False, True, pytest.raises(TypeError, match=MATCH_00700)),
        (True, True, pytest.raises(TypeError, match=MATCH_00700)),
        ({"RESULT_CODE": 200}, False, does_not_raise()),
    ],
)
def test_rest_send_v2_00700(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   response.setter

    ### Summary
    Verify ``response.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to dict.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().response is reset using various types.

    ### Expected Result
    -   ``response`` raises TypeError for non-dict inputs.
    -   ``response`` accepts dict values.
    -   ``response`` returns a list of dict in the happy path.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.response = value
    if does_raise is False:
        assert instance.response == [value]


MATCH_00800 = r"RestSend\.response_handler:\s+"
MATCH_00800 += r"response_handler must implement response_handler_v1\.\s+"
MATCH_00800 += r"Got type\s+.*,\s+"
MATCH_00800 += r"implementing\s+.*\."
MATCH_00800_A = rf"{MATCH_00800} Error detail:\s+.*"
MATCH_00800_B = MATCH_00800


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_00800_A)),
        ([10], True, pytest.raises(TypeError, match=MATCH_00800_A)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_00800_A)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_00800_A)),
        (None, True, pytest.raises(TypeError, match=MATCH_00800_A)),
        (False, True, pytest.raises(TypeError, match=MATCH_00800_A)),
        (True, True, pytest.raises(TypeError, match=MATCH_00800_A)),
        (
            ResponseGenerator(responses()),
            True,
            pytest.raises(TypeError, match=MATCH_00800_B),
        ),
        (ResponseHandler(), False, does_not_raise()),
    ],
)
def test_rest_send_v2_00800(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   response_handler.setter

    ### Summary
    Verify ``response_handler.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to a class that implements the response_handler_v1
    interface.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().response_handler is reset using various types.

    ### Expected Result
    -   ``response_handler`` raises TypeError for inappropriate inputs.
    -   ``response_handler`` accepts appropriate inputs.
    -   ``response_handler`` happy path returns a class that implements the
        response_handler_v1 interface.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.response_handler = value
    if does_raise is False:
        assert isinstance(instance.response_handler, ResponseHandler)


MATCH_00900 = r"RestSend\.result_current:\s+"
MATCH_00900 += r"result_current must be a dict\.\s+"
MATCH_00900 += r"Got.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_00900)),
        ([10], True, pytest.raises(TypeError, match=MATCH_00900)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_00900)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_00900)),
        (None, True, pytest.raises(TypeError, match=MATCH_00900)),
        (False, True, pytest.raises(TypeError, match=MATCH_00900)),
        (True, True, pytest.raises(TypeError, match=MATCH_00900)),
        ({"failed": False}, False, does_not_raise()),
    ],
)
def test_rest_send_v2_00900(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   result_current.setter

    ### Summary
    Verify ``result_current.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to dict.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().result_current is reset using various types.

    ### Expected Result
    -   ``result_current`` raises TypeError for non-dict inputs.
    -   ``result_current`` accepts dict values.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.result_current = value
    if does_raise is False:
        assert instance.result_current == value


MATCH_01000 = r"RestSend\.result:\s+"
MATCH_01000 += r"result must be a dict\.\s+"
MATCH_01000 += r"Got type.*,\s+"
MATCH_01000 += r"Value:\s+.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (10, True, pytest.raises(TypeError, match=MATCH_01000)),
        ([10], True, pytest.raises(TypeError, match=MATCH_01000)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_01000)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_01000)),
        (None, True, pytest.raises(TypeError, match=MATCH_01000)),
        (False, True, pytest.raises(TypeError, match=MATCH_01000)),
        (True, True, pytest.raises(TypeError, match=MATCH_01000)),
        ({"RESULT_CODE": 200}, False, does_not_raise()),
    ],
)
def test_rest_send_v2_01000(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   result.setter

    ### Summary
    Verify ``result.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to dict.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().result is reset using various types.

    ### Expected Result
    -   ``result`` raises TypeError for non-dict inputs.
    -   ``result`` accepts dict values.
    -   ``result`` returns a list of dict in the happy path.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.result = value
    if does_raise is False:
        assert instance.result == [value]


MATCH_01100 = r"RestSend\.send_interval:\s+"
MATCH_01100 += r"send_interval must be an integer\.\s+"
MATCH_01100 += r"Got type.*,\s+"
MATCH_01100 += r"value\s+.*\."


@pytest.mark.parametrize(
    "value, does_raise, expected",
    [
        (200, False, does_not_raise()),
        ([10], True, pytest.raises(TypeError, match=MATCH_01100)),
        ({10}, True, pytest.raises(TypeError, match=MATCH_01100)),
        ("FOO", True, pytest.raises(TypeError, match=MATCH_01100)),
        (None, True, pytest.raises(TypeError, match=MATCH_01100)),
        (False, True, pytest.raises(TypeError, match=MATCH_01100)),
        (True, True, pytest.raises(TypeError, match=MATCH_01100)),
    ],
)
def test_rest_send_v2_01100(value, does_raise, expected) -> None:
    """
    ### Classes and Methods
    -   RestSend()
            -   send_interval.setter

    ### Summary
    Verify ``send_interval.setter`` raises ``TypeError``
    when set to inappropriate types, and does not raise
    when set to integer.

    ### Setup - Code
    -   RestSend() is initialized.

    ### Setup - Data
    None

    ### Trigger
    -   RestSend().send_interval is reset using various types.

    ### Expected Result
    -   ``send_interval`` raises TypeError for non-integer inputs.
    -   ``send_interval`` accepts integer inputs.
    -   ``send_interval`` returns an integer in the happy path.
    """
    with does_not_raise():
        instance = RestSend(PARAMS)

    with expected:
        instance.send_interval = value
    if does_raise is False:
        assert isinstance(instance.send_interval, int)
        assert instance.send_interval == value
