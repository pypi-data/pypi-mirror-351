from ipaddress import ip_address, ip_network

import yaml

from legion_utils.princeps.config import PingableConfiguration


def test_basic_pingable_config_loading():
    YAML = """at: 192.168.86.123
source: [192.168.86.0/24, 10.0.0.0/24]
    """
    config = PingableConfiguration(**yaml.safe_load(YAML))
    assert config.at == ip_address('192.168.86.123')
    assert len(config.source) == 2
    assert config.source == [ip_network('192.168.86.0/24'), ip_network('10.0.0.0/24')]