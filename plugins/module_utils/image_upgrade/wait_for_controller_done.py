import copy
import inspect
import logging
from time import sleep

from ansible_collections.cisco.dcnm.plugins.module_utils.image_upgrade.switch_issu_details import \
    SwitchIssuDetailsBySerialNumber, SwitchIssuDetailsByIpAddress, SwitchIssuDetailsByDeviceName
from ansible_collections.cisco.dcnm.plugins.module_utils.common.properties import \
    Properties
from ansible_collections.cisco.dcnm.plugins.module_utils.common.results import \
    Results

@Properties.add_rest_send
class WaitForControllerDone:
    def __init__(self):
        self.class_name = self.__class__.__name__
        method_name = inspect.stack()[0][3]
        self.action = "wait_for_controller"
        self.done = set()
        self.todo = set()

        self.log = logging.getLogger(f"dcnm.{self.class_name}")

        self._check_interval = 10  # seconds
        self._check_timeout = 1800  # seconds
        self._items = None
        self._item_type = None
        self._rest_send = None
        self._valid_item_types = ["device_name", "ipv4_address", "serial_number"]

        msg = f"ENTERED {self.class_name}().{method_name}"
        self.log.debug(msg)

    def get_filter_class(self) -> None:
        """
        ### Summary
        Set the appropriate ''SwitchIssuDetails'' subclass based on
        ``item_type``.

        The subclass is used to filter the issu_details controller data
        by item_type.

        ### Raises
        None
        """
        _select = {}
        _select["device_name"] = SwitchIssuDetailsByDeviceName
        _select["ipv4_address"] = SwitchIssuDetailsByIpAddress
        _select["serial_number"] = SwitchIssuDetailsBySerialNumber
        self.issu_details = _select[self.item_type]()
        self.issu_details.rest_send = self.rest_send
        self.issu_details.results = Results()
        self.issu_details.results.action = self.action

    def verify_commit_parameters(self):
        method_name = inspect.stack()[0][3]
        msg = f"{self.class_name}.{method_name}: "

        if self.items is None:
            msg += "items must be set before calling commit()."
            raise ValueError(msg)

        if self.item_type is None:
            msg += "item_type must be set before calling commit()."
            raise ValueError(msg)

        if self.rest_send is None:
            msg = f"{self.class_name}.{method_name}: "
            msg += "rest_send must be set before calling commit()."
            raise ValueError(msg)

        
    def commit(self):
        """
        ### Summary
        The controller will not proceed with certain operations if there
        are any actions in progress.  Wait for all actions to complete
        and then return.

        Actions include image staging, image upgrade, and image validation.

        ### Raises
        -   ``ValueError`` if the actions do not complete within the timeout.
        """
        method_name = inspect.stack()[0][3]

        self.verify_commit_parameters()

        if len(self.items) == 0:
            return
        self.get_filter_class()
        self.todo = copy.copy(self.items)
        timeout = self.check_timeout

        while self.done != self.todo and timeout > 0:
            if self.rest_send.unit_test is False:
                sleep(self.check_interval)
            timeout -= self.check_interval

            self.issu_details.refresh()

            for item in self.todo:
                if item in self.done:
                    continue
                self.issu_details.filter = item
                if self.issu_details.actions_in_progress is False:
                    self.done.add(item)

        if self.done != self.todo:
            msg = f"{self.class_name}.{method_name}: "
            msg += "Timed out waiting for controller actions to complete. "
            msg += "done: "
            msg += f"{','.join(sorted(self.done))}, "
            msg += "todo: "
            msg += f"{','.join(sorted(self.todo))}"
            raise ValueError(msg)

    @property
    def check_interval(self):
        """
        ### Summary
        The validate check interval, in seconds.
        Default is 10 seconds.

        ### Raises
        -   ``TypeError`` if the value is not an integer.
        -   ``ValueError`` if the value is less than zero.

        ### Example
        ```python
        instance.check_interval = 10
        ```
        """
        return self._check_interval

    @check_interval.setter
    def check_interval(self, value):
        method_name = inspect.stack()[0][3]
        msg = f"{self.class_name}.{method_name}: "
        msg += "must be a positive integer or zero. "
        msg += f"Got value {value} of type {type(value)}."
        # isinstance(True, int) is True so we need to check for bool first
        if isinstance(value, bool):
            raise TypeError(msg)
        if not isinstance(value, int):
            raise TypeError(msg)
        if value < 0:
            raise ValueError(msg)
        self._check_interval = value

    @property
    def check_timeout(self):
        """
        ### Summary
        The validate check timeout, in seconds.
        Default is 1800 seconds.

        ### Raises
        -   ``TypeError`` if the value is not an integer.
        -   ``ValueError`` if the value is less than zero.

        ### Example
        ```python
        instance.check_timeout = 1800
        ```
        """
        return self._check_timeout

    @check_timeout.setter
    def check_timeout(self, value):
        method_name = inspect.stack()[0][3]
        msg = f"{self.class_name}.{method_name}: "
        msg += "must be a positive integer or zero. "
        msg += f"Got value {value} of type {type(value)}."
        # isinstance(True, int) is True so we need to check for bool first
        if isinstance(value, bool):
            raise TypeError(msg)
        if not isinstance(value, int):
            raise TypeError(msg)
        if value < 0:
            raise ValueError(msg)
        self._check_timeout = value

    @property
    def items(self):
        """
        ### Summary
        A set of serial_number, ipv4_address, or device_name to wait for.

        ### Raises
        ValueError: If ``items`` is not a set.

        ### Example
        ```python
        instance.items = {"192.168.1.1", "192.168.1.2"}
        ```
        """
        return self._items
    @items.setter
    def items(self, value):
        if not isinstance(value, set):
            raise ValueError("items must be a set")
        self._items = value

    @property
    def item_type(self):
        """
        ### Summary
        The type of items to wait for.

        ### Raises
        ValueError: If ``item_type`` is not one of the valid values.

        ### Valid Values
        -   ``serial_number``
        -   ``ipv4_address``
        -   ``device_name``

        ### Example
        ```python
        instance.item_type = "ipv4_address"
        ```
        """
        return self._item_type
    @item_type.setter
    def item_type(self, value):
        if value not in self._valid_item_types:
            msg = f"{self.class_name}.item_type: "
            msg = "item_type must be one of "
            msg += f"{','.join(self._valid_item_types)}."
            raise ValueError(msg)
        self._item_type = value