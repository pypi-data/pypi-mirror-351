from ipaddress import ip_address
from pathlib import Path

import yaml
from pytest import approx, raises

from legion_utils import Priority
from legion_utils.princeps.princeps import ServiceRegistryEntry, now, ServiceRegistrar, ServiceRegistry, \
    InvalidServiceRegistryEntry, PrincepsConfiguration
from tests.unit import file_with

SERVICE_REGISTRY_ENTRY_JSON_BASIC = f"""
{{
    "name": "test-service-basic",
    "last_checkin": {now() - 30},
    "next_checkin_before": {now() + 30},
    "alert_ttl": 120,
    "warn_after": 60,
    "error_after": 120,
    "critical_after": 300
}}
"""

SERVICE_REGISTRY_ENTRY_JSON_WARN = f"""
{{
    "name": "test-service-warn",
    "last_checkin": {now() - 91},
    "next_checkin_before": {now() - 61},
    "alert_ttl": 120,
    "warn_after": 60,
    "error_after": 120,
    "critical_after": 300
}}
"""

SERVICE_REGISTRY_ENTRY_JSON_ERROR = f"""
{{
    "name": "test-service-error",
    "last_checkin": {now() - 151},
    "next_checkin_before": {now() - 121},
    "alert_ttl": 120,
    "warn_after": 60,
    "error_after": 120,
    "critical_after": 300
}}
"""

SERVICE_REGISTRY_ENTRY_JSON_CRITICAL = f"""
{{
    "name": "test-service-critical",
    "last_checkin": {now() - 331},
    "next_checkin_before": {now() - 301},
    "alert_ttl": 120,
    "warn_after": 60,
    "error_after": 120,
    "critical_after": 300
}}
"""

SERVICE_REGISTRY_ENTRY_JSON_DEFAULT = f"""
{{
    "name": "test-service-default",
    "last_checkin": {now() - 31},
    "next_checkin_before": {now() - 1},
    "alert_ttl": 120
}}
"""

SERVICE_REGISTRY_ENTRY_INVALID_JSON = f"""
{{
    "name": "test-service-default",
    "last_checkin": {now() - 31},
    "next_checkin_before": {now() - 1},
    "alert_ttl": 120,
}}
"""


def test_service_registry_entry_from_file(tmp_path):
    entry = ServiceRegistryEntry.of_file(file_with(tmp_path / 'test-service.json', SERVICE_REGISTRY_ENTRY_JSON_BASIC))
    assert entry.critical_after == 300
    assert int(entry.next_checkin_before - entry.last_checkin) == approx(60)


def test_service_registry_entry_to_alert_contents(tmp_path):
    entry = ServiceRegistryEntry.of_file(
        file_with(tmp_path / 'test-service-basic.json', SERVICE_REGISTRY_ENTRY_JSON_BASIC))
    assert entry.to_alert_contents()['service_name'] == 'test-service-basic'
    assert entry.to_alert_contents()['last_checkin'] == approx(now() - 30)


def test_service_registry_entry_should_warn(tmp_path):
    entry = ServiceRegistryEntry.of_file(file_with(tmp_path / 'test-service.json', SERVICE_REGISTRY_ENTRY_JSON_WARN))
    assert entry.should_alert()
    assert entry.should_warn()
    assert not entry.should_error()
    assert not entry.should_critical()


def test_service_registry_entry_should_error(tmp_path):
    entry = ServiceRegistryEntry.of_file(file_with(tmp_path / 'test-service.json', SERVICE_REGISTRY_ENTRY_JSON_ERROR))
    assert entry.should_alert()
    assert not entry.should_warn()
    assert entry.should_error()
    assert not entry.should_critical()


def test_service_registry_entry_should_error_default(tmp_path):
    entry = ServiceRegistryEntry.of_file(file_with(tmp_path / 'test-service.json', SERVICE_REGISTRY_ENTRY_JSON_DEFAULT))
    assert entry.should_alert()
    assert not entry.should_warn()
    assert entry.should_error()
    assert not entry.should_critical()


def test_service_registry_entry_should_critical(tmp_path):
    entry = ServiceRegistryEntry.of_file(
        file_with(tmp_path / 'test-service.json', SERVICE_REGISTRY_ENTRY_JSON_CRITICAL))
    assert entry.should_alert()
    assert not entry.should_warn()
    assert not entry.should_error()
    assert entry.should_critical()


def test_service_registrar_basics(tmp_path):
    registrar = ServiceRegistrar(name='test-service',
                                 checkin_interval=30,
                                 alert_ttl=120,
                                 directory=tmp_path,
                                 warn_after=60)
    registrar.check_in()
    entry = ServiceRegistryEntry.of_file(
        file_with(tmp_path / 'test-service-critical.json', SERVICE_REGISTRY_ENTRY_JSON_CRITICAL))
    assert entry.name == 'test-service-critical'
    assert entry.last_checkin == approx(now())
    assert entry.next_checkin_before == approx(now() + 30)


def test_service_registry_basics(tmp_path):
    file_with(tmp_path / 'test-service-basic.json', SERVICE_REGISTRY_ENTRY_JSON_BASIC)
    file_with(tmp_path / 'test-service-warn.json', SERVICE_REGISTRY_ENTRY_JSON_WARN)
    file_with(tmp_path / 'test-service-error.json', SERVICE_REGISTRY_ENTRY_JSON_ERROR)
    file_with(tmp_path / 'test-service-critical.json', SERVICE_REGISTRY_ENTRY_JSON_CRITICAL)
    registry = ServiceRegistry(tmp_path)
    for entry in registry.delinquent_services():
        assert isinstance(entry, ServiceRegistryEntry)
        assert entry.should_alert()
        if entry.name == 'test-service-warn':
            assert entry.should_alert()
            assert entry.should_warn()
            assert not entry.should_error()
            assert not entry.should_critical()
        elif entry.name == 'test-service-error':
            assert entry.should_alert()
            assert not entry.should_warn()
            assert entry.should_error()
            assert not entry.should_critical()
        elif entry.name == 'test-service-critical':
            assert entry.should_alert()
            assert not entry.should_warn()
            assert not entry.should_error()
            assert entry.should_critical()
        else:
            assert False  # no other entries should've been output


def test_creating_invalid_entry(tmp_path):
    file_with(tmp_path / 'test-service-invalid.json', SERVICE_REGISTRY_ENTRY_INVALID_JSON)
    entry = InvalidServiceRegistryEntry.of_file(tmp_path / 'test-service-invalid.json')
    assert entry.to_alert_contents() == {"from_file": str(tmp_path / 'test-service-invalid.json'),
                                         "file_contents": SERVICE_REGISTRY_ENTRY_INVALID_JSON}


def test_service_registry_invalid_entry(tmp_path):
    file_with(tmp_path / 'test-service-invalid.json', SERVICE_REGISTRY_ENTRY_INVALID_JSON)
    registry = ServiceRegistry(tmp_path)
    for entry in registry.delinquent_services():
        assert isinstance(entry, InvalidServiceRegistryEntry)
        assert not entry.should_critical()
        assert entry.should_error()
        assert not entry.should_warn()


PRINCEPS_CONFIG_BASIC = """
exchange: test_exchange
services:
  directory: /var/run/legion/princeps/service_registry
  reporting_period: 1
system:
  paths:
    /:
      warning_threshold_percentage: 90
  restart_required:
    path: /var/run/reboot-required
    severity: warning
  reporting_period: 69
"""


def test_princeps_configuration_loading(tmp_path):
    file_with(tmp_path / 'config.yaml', PRINCEPS_CONFIG_BASIC)
    config = PrincepsConfiguration.of(tmp_path / 'config.yaml')
    assert config.exchange == 'test_exchange'
    assert config.system.paths[Path('/')].error_threshold_percentage is None
    assert config.system.paths[Path('/')].alert_priority(100) == Priority.WARNING
    assert config.system.paths[Path('/')].alert_priority(50) is None
    assert config.system.reporting_period == 69
    assert config.system.restart_required.priority() is None
    assert not config.system.restart_required.restart_required()
    assert config.system.pingable is None


def test_princeps_configuration_reporting(tmp_path):
    file_with(tmp_path / 'config.yaml', PRINCEPS_CONFIG_BASIC)
    config = PrincepsConfiguration.of(tmp_path / 'config.yaml')
    assert config.exchange == 'test_exchange'
    report = config.system.cpu_ram_disk_network_report()
    assert report['/'] is not None
    assert report['/']['free'] > 0.0
    assert report['/']['percent'] > 0.0
    assert report['/']['total'] > 0.0
    assert report['/']['used'] > 0.0
    assert report['CPU_load'] >= 0.0
    assert 'network_accessibility' not in report


PRINCEPS_CONFIG_PINGABLE = """
exchange: test_exchange
services:
  directory: /var/run/legion/princeps/service_registry
  reporting_period: 1
system:
  paths:
    /:
      warning_threshold_percentage: 90
  restart_required:
    path: /var/run/reboot-required
    severity: warning
  reporting_period: 69
  pingable:
  - at: 192.168.86.123
    source: [192.168.86.0/24, 10.0.0.0/24]
  - at: example.com
    source: [global]
"""


def test_princeps_configuration_loading_with_pingability_info(tmp_path):
    file_with(tmp_path / 'config.yaml', PRINCEPS_CONFIG_PINGABLE)
    config = PrincepsConfiguration.of(tmp_path / 'config.yaml')
    assert config.exchange == 'test_exchange'
    assert config.system.paths[Path('/')].error_threshold_percentage is None
    assert config.system.paths[Path('/')].alert_priority(100) == Priority.WARNING
    assert config.system.paths[Path('/')].alert_priority(50) is None
    assert config.system.reporting_period == 69
    assert config.system.restart_required.priority() is None
    assert not config.system.restart_required.restart_required()
    assert config.system.pingable[0].at == ip_address('192.168.86.123')
    assert config.system.pingable[1].at == 'example.com'


def test_princeps_configuration_reporting_with_pingability_info(tmp_path):
    file_with(tmp_path / 'config.yaml', PRINCEPS_CONFIG_PINGABLE)
    config = PrincepsConfiguration.of(tmp_path / 'config.yaml')
    assert config.exchange == 'test_exchange'
    report = config.system.cpu_ram_disk_network_report()
    assert report['/'] is not None
    assert report['/']['free'] > 0.0
    assert report['/']['percent'] > 0.0
    assert report['/']['total'] > 0.0
    assert report['/']['used'] > 0.0
    assert report['CPU_load'] >= 0.0
    assert report['network_accessibility'] == [{'at': '192.168.86.123',
                                                'source': ['192.168.86.0/24', '10.0.0.0/24']},
                                               {'at': 'example.com',
                                                'source': ['global']}]


def test_invalid_ping_dest():
    princeps_config = """
    exchange: test_exchange
    services:
      directory: /var/run/legion/princeps/service_registry
      reporting_period: 1
    system:
      paths:
        /:
          warning_threshold_percentage: 90
      restart_required:
        path: /var/run/reboot-required
        severity: warning
      reporting_period: 69
      pingable:
      - at: 192.168.86.123
        source: [192.168.86.0/24, 10.0.0.0/24]
      - at: not a hostname
        source: [global]
    """
    with raises(ValueError, match="'not a hostname' is neither a valid IP address, nor a hostname"):
        PrincepsConfiguration(**yaml.safe_load(princeps_config))


def test_invalid_ping_source():
    princeps_config = """
    exchange: test_exchange
    services:
      directory: /var/run/legion/princeps/service_registry
      reporting_period: 1
    system:
      paths:
        /:
          warning_threshold_percentage: 90
      restart_required:
        path: /var/run/reboot-required
        severity: warning
      reporting_period: 69
      pingable:
      - at: 192.168.86.123
        source: [192.168.86.0/24, 10.0.0.0/24]
      - at: example.com
        source: [5]
    """
    with raises(ValueError, match="The source value: '5' is neither an IP address nor 'global'."):
        PrincepsConfiguration(**yaml.safe_load(princeps_config))
