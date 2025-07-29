import click
import asyncio
import psutil
import os
import configparser
import sqlalchemy

from joule.cli.config import pass_config
from joule import constants
WORKING_DIRECTORY = '/tmp/joule'


def abort_if_false(ctx, param, value):
    if not value:
        ctx.abort()


@click.command(name="erase")
@click.option("-c", "--config", help="main configuration file", default=constants.ConfigFiles.main_config)
@click.option("-l", "--links", is_flag=True, help="delete masters and followers as well as data")
@click.option('--yes', is_flag=True, callback=abort_if_false,
              expose_value=False,
              prompt='Are you sure you want to wipe the local node?')
def admin_erase(config, links):
    """Erase the local node."""
    from joule.services import load_config
    from joule.errors import ConfigurationError
    # make sure joule is not running
    pid_file = os.path.join(WORKING_DIRECTORY, 'pid')
    if os.path.exists(pid_file):
        with open(pid_file, 'r') as f:
            pid = int(f.readline())
            if psutil.pid_exists(pid):
                raise click.ClickException("stop joule service before running this command")

    # load the config file
    if os.path.isfile(config) is False:
        raise click.ClickException("Invalid configuration: cannot load file [%s]" % config)
    parser = configparser.ConfigParser()
    try:
        with open(config, 'r') as f:
            parser.read_file(f)
    except PermissionError:
        raise click.ClickException("insufficient permissions, run with [sudo]")
    except FileNotFoundError:
        raise click.ClickException("Joule config [%s] not found, specify with --config")

    try:
        joule_config = load_config.run(custom_values=parser)
    except ConfigurationError as e:
        raise click.ClickException("Invalid configuration: %s" % e)

    asyncio.run(run(joule_config,links))


async def run(config, delete_links):
    from sqlalchemy import create_engine, text
    from sqlalchemy.orm import Session

    from joule.models import (DataStream, Element, EventStream,
                              Master, Follower, Annotation,
                              Folder, Base, TimescaleStore)
    from joule.errors import DataError

    # erase metadata
    engine = create_engine(config.database)
    with engine.connect() as conn:
        with conn.begin():
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS data'))
            conn.execute(text('CREATE SCHEMA IF NOT EXISTS metadata'))
        Base.metadata.create_all(engine)
        db = Session(bind=engine)
        db.query(Element).delete()
        db.query(Annotation).delete()
        db.query(DataStream).delete()
        db.query(EventStream).delete()
        db.query(Folder).delete()
        if delete_links:
            db.query(Master).delete()
            db.query(Follower).delete()
        db.commit()

    # erase data
    data_store = TimescaleStore(config.database,
                                config.insert_period,
                                config.cleanup_period)
    try:
        await data_store.initialize([])
        await data_store.destroy_all()
    except DataError as e:
        click.echo("Error erasing database")
        raise click.ClickException(str(e))
