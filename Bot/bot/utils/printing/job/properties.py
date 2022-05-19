from bot.utils.jobs.properties import Property, Properties, MappedValue


class CopiesProperty(Property):
    readable_name = "Copies"
    source_name = "copies"
    webapp_name = "copies"

    def __init__(self):
        self.value = "1"


class PagesProperty(Property):
    readable_name = "Pages"
    source_name = "page-ranges"
    webapp_name = "pages"

    def __init__(self):
        self.value = "1"

    def get_total_pages_number(self) -> str:
        try:
            result = 0
            for part in self.value.split(","):
                if "-" not in part:
                    int(part.strip())
                    result += 1
                    continue

                a, b = map(lambda num: int(num.strip()), part.split("-"))
                result += b - a + 1
            return str(result)
        except Exception as e:
            return "invalid"

    def get_context(self) -> str:
        return f"(total: *{self.get_total_pages_number()}*)"


class SidesProperty(Property):
    readable_name = "Print on"
    source_name = "sides"
    webapp_name = "print-on"

    values_mapped = [
        MappedValue(source="one-sided", readable="One side", webapp="print-on-one-side"),
        MappedValue(source="two-sided-long-edge", readable="Both sides", webapp="print-on-both-sides")
    ]

    def __init__(self):
        self.value = self.values_mapped[0].source


class NumberUpProperty(Property):
    readable_name = "Layout"
    source_name = "number-up"
    webapp_name = "layout"

    values_mapped = [
        MappedValue(source="1", readable="1x1", webapp="layout-1"),
        MappedValue(source="4", readable="2x2", webapp="layout-4"),
        MappedValue(source="9", readable="3x3", webapp="layout-9")
    ]

    def __init__(self):
        self.value = self.values_mapped[0].source


class PrintProperties(Properties):
    properties_types = [CopiesProperty, PagesProperty, SidesProperty, NumberUpProperty]

    def get_total_pages_number(self) -> int:
        """Get total pages for printing"""

        copies_property = self.get_property_by_type(CopiesProperty)
        pages_property = self.get_property_by_type(PagesProperty)

        # noinspection PyBroadException
        try:
            # noinspection PyUnresolvedReferences
            return int(pages_property.get_total_pages_number()) * int(copies_property.value)
        except Exception as e:
            return 0
