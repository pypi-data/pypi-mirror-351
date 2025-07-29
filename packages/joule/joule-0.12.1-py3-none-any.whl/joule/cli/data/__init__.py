import click
from joule.cli.lazy_group import LazyGroup

@click.group(name="data",
             cls=LazyGroup,
             lazy_subcommands={"copy": "joule.cli.data.copy.data_copy",
                               "read": "joule.cli.data.read.cmd",
                               "delete": "joule.cli.data.delete.data_delete",
                               "intervals": "joule.cli.data.intervals.intervals",
                               "consolidate": "joule.cli.data.consolidate.consolidate",
                               "merge": "joule.cli.data.merge.merge",
                               "ingest": "joule.cli.data.ingest.ingest"})
def data():
    """Interact with data streams."""
    pass  

@click.group(name="filter",
             cls=LazyGroup,
             lazy_subcommands={"mean": "joule.cli.data.mean.mean",
                               "median": "joule.cli.data.median.median"})
def filter():
    """Filter stream data."""
    pass  

data.add_command(filter)