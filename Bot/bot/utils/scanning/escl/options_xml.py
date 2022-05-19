with open("bot/utils/scanning/escl/scan_options_template.xml") as f:
    scan_option_template = f.read()


def get_options_xml(options: dict) -> str:
    return scan_option_template.format(**options)
