from abc import ABC

from typing import List, Type, NamedTuple


class MappedValue(NamedTuple):
    """Property mapped value"""
    source: str  # for providing to service (e.g. CUPS)
    readable: str  # for displaying to user (used in __str__)
    webapp: str  # for communicating with Telegram Web App


class Property(ABC):
    """Abstract class for property"""

    readable_name: str = "Readable name for user (used in __str__)"
    source_name: str = "Name for Source"
    webapp_name: str = "Name for WebApp parameter"

    value: str = "Current source value"

    # List of mapped values, it will be used only if it is not empty
    values_mapped: List[MappedValue] = []

    # noinspection PyMethodMayBeStatic
    def get_context(self) -> str:
        """Additional information for displaying to user (used in __str__)"""

        return ""

    def get_readable_value(self) -> str:
        """Readable value for displaying to user"""

        if not self.values_mapped:
            return str(self.value)

        for mapped_value in self.values_mapped:
            if mapped_value.source == self.value:
                return mapped_value.readable

    def get_webapp_value(self) -> str:
        """URL parameter for parsing in page for Telegram Web App"""

        if not self.values_mapped:
            return str(self.value)

        for mapped_value in self.values_mapped:
            if mapped_value.source == self.value:
                return mapped_value.webapp

    def get_source_value(self) -> str:

        return str(self.value)

    # noinspection PyMethodMayBeStatic,PyUnusedLocal
    def value_check(self, new_value: str) -> bool:
        """Validation of new property value"""

        return True

    def set_value(self, value: str) -> None:
        """Validate CUPS value and set it"""

        if self.value_check(value):
            self.value = value

    def set_value_from_webapp(self, value: str) -> None:
        """Set value got from Web App"""

        if not self.values_mapped:
            self.set_value(value)

        for mapped_value in self.values_mapped:
            if mapped_value.webapp == value:
                self.set_value(mapped_value.source)

    def __str__(self):
        """Property representation for user with Markdown formatting"""
        return f"{self.readable_name}: *{self.get_readable_value()}* {self.get_context()}"


class Properties(ABC):
    """Abstract class for combining all properties"""

    properties_types: List[Type[Property]] = []
    _properties_initialized: List[Property] = []

    def __init__(self):
        self._properties_initialized = []
        for prop in self.properties_types:
            self._properties_initialized.append(prop())

    def get_source_properties(self) -> dict:
        """Dictionary of source names and values of all properties"""

        result = {prop.source_name: prop.value for prop in self._properties_initialized}
        return result

    def get_webapp_url_params(self, job_id: str = None) -> str:
        """Get parameters for Telegram Web App (URL)"""

        parameters = [f"{prop.webapp_name}={prop.get_webapp_value()}" for prop in self._properties_initialized]
        if job_id:
            parameters.append(f"job-id={job_id}")
        return "&".join(parameters)

    def get_logger_text(self) -> str:
        """Properties text for logging"""

        return "; ".join(
            [f"{prop.readable_name}: {prop.get_readable_value()}"
             for prop in self._properties_initialized]
        )

    def get_readable_text(self) -> str:
        """Properties text for displaying to user with Markdown formatting"""

        return "\n".join(
            ["• " + str(prop) for prop in self._properties_initialized]
        )

    def update_webapp_values(self, values: dict) -> None:
        """Update values got from Telegram Web App"""

        for prop in self._properties_initialized:
            value = values.get(prop.webapp_name, None)
            if value is not None:
                prop.set_value_from_webapp(value)

    def get_property_by_type(self, property_type: Type[Property]) -> Property:
        """Get property by its type"""

        for prop in self._properties_initialized:
            if type(prop) is property_type:
                return prop
