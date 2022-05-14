from bot.utils.jobs.properties import Property, Properties, MappedValue


class SidesProperty(Property):
    readable_name = "Scan from"
    source_name = "sides"
    webapp_name = "scan-from"

    values_mapped = [
        MappedValue(source="false", readable="One side", webapp="scan-from-one-side"),
        MappedValue(source="true", readable="Both sides", webapp="scan-from-both-sides")
    ]

    def __init__(self):
        self.value = self.values_mapped[0].source


class QualityProperty(Property):
    readable_name = "Quality"
    source_name = "quality"
    webapp_name = "quality"

    values_mapped = [
        MappedValue(source="200", readable="200", webapp="quality-200"),
        MappedValue(source="300", readable="300", webapp="quality-300"),
        MappedValue(source="400", readable="400", webapp="quality-400"),
        MappedValue(source="600", readable="600", webapp="quality-600"),
    ]

    def __init__(self):
        self.value = self.values_mapped[1].source


class ScanProperties(Properties):
    properties_types = [SidesProperty, QualityProperty]
