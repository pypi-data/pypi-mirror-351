import json
from pathlib import Path
from typing import Optional

import click
from click import Context
from environs import Env

from legion_utils import broadcast_error, broadcast_warning, broadcast_critical, broadcast_info, broadcast_activity

ENV = Env()
ENV.read_env()

# Exit codes
REQUIRED_PARAMS_NOT_PROVIDED = 1
CONFLICTING_PARAMS_PROVIDED = 2


@click.group
@click.option('-e', '--exchange', default=None,
              help="RobotnikMQ exchange to publish to (alternatively use LEGION_EXCHANGE environment variable)")
@click.option('-r', '--route', default=None,
              help='RobotnikMQ route to publish to (alternatively use LEGION_ROUTE environment variable')
@click.option('-c', '--config', default=None, type=click.Path(exists=True, file_okay=True, dir_okay=False,
                                                              readable=True, resolve_path=True,
                                                              allow_dash=False, path_type=Path),
              help='RobotnikMQ configuration file path which defaults to /etc/robotnikmq/robotnikmq.yaml '
                   '(alternatively use ROBOTNIKMQ_CONFIG_FILE)')
@click.pass_context
def cli(ctx: Context, exchange: Optional[str], route: Optional[str], config: Optional[Path]):
    """
    Utility for publishing Legion notifications and alerts from the commandline. In particular, designed to be easy
    to integrate with other applications as a way to publish alerts when a procedure, such as a cronjob, fails.
    """
    ctx.ensure_object(dict)
    ctx.obj['LEGION_EXCHANGE'] = (exchange or ENV.str('LEGION_EXCHANGE'))
    if not ctx.obj['LEGION_EXCHANGE']:
        click.echo('No exchange provided, please use either --exchange or the LEGION_EXCHANGE environment variable.',
                   err=True)
        exit(REQUIRED_PARAMS_NOT_PROVIDED)
    ctx.obj['LEGION_ROUTE'] = (route or ENV.str('LEGION_ROUTE'))
    if not ctx.obj['LEGION_ROUTE']:
        click.echo('No route provided, please use either --route or the LEGION_ROUTE environment variable.',
                   err=True)
        exit(REQUIRED_PARAMS_NOT_PROVIDED)
    ctx.obj['ROBOTNIKMQ_CONFIG_FILE'] = (
            config or ENV.str('ROBOTNIKMQ_CONFIG_FILE') or '/etc/robotnikmq/robotnikmq.yaml')


@cli.command
@click.argument('description', type=str)
@click.option('--contents', type=str, default=None,
              help="JSON-formatted information to be included as the contents field of a RobotnikMQ message")
@click.option('--contents-file', type=click.Path(readable=True, file_okay=True, dir_okay=False,
                                                 allow_dash=True, path_type=str),
              help="JSON file (piping in works) containing information to be included as the contents field of a "
                   "RobotnikMQ message", default=None)
@click.pass_context
def info(ctx: Context, description: str, contents: Optional[str], contents_file: Optional[str], ):
    if contents_file and contents:
        click.echo('Both --contents and --contents-file were provided which are mutually exclusive, '
                   'please provide only one of the two', err=True)
        exit(CONFLICTING_PARAMS_PROVIDED)
    broadcast_info(exchange=ctx.obj['LEGION_EXCHANGE'],
                   route=ctx.obj['LEGION_ROUTE'],
                   desc=description,
                   contents=json.loads(contents or click.open_file(contents_file).read()),
                   config=ctx.obj['ROBOTNIKMQ_CONFIG_FILE'])


@cli.command
@click.argument('description', type=str)
@click.option('--contents', type=str, default=None,
              help="JSON-formatted information to be included as the contents field of a RobotnikMQ message")
@click.option('--contents-file', type=click.Path(readable=True, file_okay=True, dir_okay=False,
                                                 allow_dash=True, path_type=str),
              help="JSON file (piping in works) containing information to be included as the contents field of a "
                   "RobotnikMQ message", default=None)
@click.pass_context
def activity(ctx: Context, description: str, contents: Optional[str], contents_file: Optional[str],):
    if contents_file and contents:
        click.echo('Both --contents and --contents-file were provided which are mutually exclusive, '
                   'please provide only one of the two', err=True)
        exit(CONFLICTING_PARAMS_PROVIDED)
    broadcast_activity(exchange=ctx.obj['LEGION_EXCHANGE'],
                       route=ctx.obj['LEGION_ROUTE'],
                       desc=description,
                       contents=json.loads(contents or click.open_file(contents_file).read()),
                       config=ctx.obj['ROBOTNIKMQ_CONFIG_FILE'])


@cli.command
@click.argument('alert_key', type=str)
@click.argument('description', type=str)
@click.option('--contents', type=str, default=None,
              help="JSON-formatted information to be included as the contents field of a RobotnikMQ message")
@click.option('--contents-file', type=click.Path(readable=True, file_okay=True, dir_okay=False,
                                                 allow_dash=True, path_type=str),
              help="JSON file (piping in works) containing information to be included as the contents field of a "
                   "RobotnikMQ message", default=None)
@click.option('-t', '--ttl', type=int, default=30, help='A time-to-live (TTL) for the alert, in seconds.'
                                                        ' Defaults to 30-seconds.')
@click.pass_context
def warning(ctx: Context, alert_key: str, description: str, contents: Optional[str], contents_file: Optional[str],
            ttl: int):
    """
    Publishes a RobotnikMQ message with the priority of "warning". This makes it an alert, which in turn means that it
    requires an alert key (for disambiguation) and a description of what is actually wrong.

    Example:
        ALERT_KEY: [bender][/etc/tls/server.crt][expiry]
        DESCRIPTION: Certificate at bender:/etc/tls/server.crt expires in 26 days
    """
    if contents_file and contents:
        click.echo('Both --contents and --contents-file were provided which are mutually exclusive, '
                   'please provide only one of the two', err=True)
        exit(CONFLICTING_PARAMS_PROVIDED)

    broadcast_warning(exchange=ctx.obj['LEGION_EXCHANGE'],
                      route=ctx.obj['LEGION_ROUTE'],
                      desc=description,
                      alert_key=alert_key,
                      contents=json.loads(contents or click.open_file(contents_file).read()),
                      ttl=ttl,
                      config=ctx.obj['ROBOTNIKMQ_CONFIG_FILE'])


@cli.command
@click.argument('alert_key', type=str)
@click.argument('description', type=str)
@click.option('--contents', type=str, default=None,
              help="JSON-formatted information to be included as the contents field of a RobotnikMQ message")
@click.option('--contents-file', type=click.Path(readable=True, file_okay=True, dir_okay=False,
                                                 allow_dash=True, path_type=str),
              help="JSON file (piping in works) containing information to be included as the contents field of a "
                   "RobotnikMQ message", default=None)
@click.option('-t', '--ttl', type=int, default=30, help='A time-to-live (TTL) for the alert, in seconds.'
                                                        ' Defaults to 30-seconds.')
@click.pass_context
def error(ctx: Context, alert_key: str, description: str, contents: Optional[str], contents_file: Optional[str],
          ttl: int):
    """
    Publishes a RobotnikMQ message with the priority of "error". This makes it an alert, which in turn means that it
    requires an alert key (for disambiguation) and a description of what is actually wrong.

    Example:
        ALERT_KEY: [bender][/etc/tls/server.crt][expiry]
        DESCRIPTION: Certificate at bender:/etc/tls/server.crt expires in 18 days
    """
    if contents_file and contents:
        click.echo('Both --contents and --contents-file were provided which are mutually exclusive, '
                   'please provide only one of the two', err=True)
        exit(CONFLICTING_PARAMS_PROVIDED)

    broadcast_error(exchange=ctx.obj['LEGION_EXCHANGE'],
                    route=ctx.obj['LEGION_ROUTE'],
                    desc=description,
                    alert_key=alert_key,
                    contents=json.loads(contents or click.open_file(contents_file).read()),
                    ttl=ttl,
                    config=ctx.obj['ROBOTNIKMQ_CONFIG_FILE'])


@cli.command
@click.argument('alert_key', type=str)
@click.argument('description', type=str)
@click.option('--contents', type=str, default=None,
              help="JSON-formatted information to be included as the contents field of a RobotnikMQ message")
@click.option('--contents-file', type=click.Path(readable=True, file_okay=True, dir_okay=False,
                                                 allow_dash=True, path_type=str),
              help="JSON file (piping in works) containing information to be included as the contents field of a "
                   "RobotnikMQ message", default=None)
@click.option('-t', '--ttl', type=int, default=30, help='A time-to-live (TTL) for the alert, in seconds.'
                                                        ' Defaults to 30-seconds.')
@click.pass_context
def critical(ctx: Context, alert_key: str, description: str, contents: Optional[str], contents_file: Optional[str],
             ttl: int):
    """
    Publishes a RobotnikMQ message with the priority of "critical". This makes it an alert, which in turn means that it
    requires an alert key (for disambiguation) and a description of what is actually wrong.

    Example:
        ALERT_KEY: [bender][/etc/tls/server.crt][expiry]
        DESCRIPTION: Certificate at bender:/etc/tls/server.crt expires in 2 days
    """
    if contents_file and contents:
        click.echo('Both --contents and --contents-file were provided which are mutually exclusive, '
                   'please provide only one of the two', err=True)
        exit(CONFLICTING_PARAMS_PROVIDED)

    broadcast_critical(exchange=ctx.obj['LEGION_EXCHANGE'],
                       route=ctx.obj['LEGION_ROUTE'],
                       desc=description,
                       alert_key=alert_key,
                       contents=json.loads(contents or click.open_file(contents_file).read()),
                       ttl=ttl,
                       config=ctx.obj['ROBOTNIKMQ_CONFIG_FILE'])
