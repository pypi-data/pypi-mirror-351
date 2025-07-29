from sqlalchemy.orm import Session
from typing import List, Tuple
from datetime import datetime, timezone

from joule.errors import ConfigurationError
from joule.models import DataStream, Element, Follower
from joule.models import data_stream, folder


# basic format of stream is just the full_path
# /file/path/stream_name
# but streams may be configured inline
# /file/path/stream_name:datatype[e1, e2, e3, ...]
#  where e1, e2, e2, ... are the element names
#


def run(pipe_config: str, db: Session) -> DataStream:
    # check for a remote stream config
    (pipe_config, node_name) = strip_remote_config(pipe_config)
    local = node_name is None
    # separate the configuration pieces
    (path, name, inline_config) = parse_pipe_config(pipe_config)
    name = data_stream.validate_name(name)
    # parse the inline configuration
    (datatype, element_names) = parse_inline_config(inline_config)
    # if the stream is local, check for it in the database
    if local:
        my_folder = folder.find(path, db, create=True)
        # check if the stream exists in the database
        existing_stream: DataStream = db.query(DataStream). \
            filter_by(folder=my_folder, name=name). \
            one_or_none()
        if existing_stream is not None:
            if len(inline_config) > 0:
                _validate_config_match(existing_stream, datatype, element_names)
            return existing_stream
    else:  # make sure the remote node is a follower
        if db.query(Follower).filter_by(name=node_name).one_or_none() is None:
            raise ConfigurationError("Remote node [%s] is not a follower" % node_name)

    # if the stream doesn't exist it or its remote, it *must* have inline configuration
    if len(inline_config) == 0:
        if local:
            msg = "add inline config or *.conf file for stream [%s]" % pipe_config
        else:
            msg = "invalid remote stream, must have inline config"
        raise ConfigurationError(msg)

    # build the stream from inline config
    my_stream = data_stream.DataStream(name=name,
                                       datatype=datatype,
                                       updated_at=datetime.now(timezone.utc))
    i = 0
    for e in element_names:
        my_stream.elements.append(Element(name=e, index=i))
        i += 1
    if local:
        my_folder.data_streams.append(my_stream)
        db.add(my_stream)
    else:
        my_stream.set_remote(node_name, path + '/' + my_stream.name)
    return my_stream


def strip_remote_config(pipe_config: str) -> Tuple[str, str]:
    try:
        # check for the remote URL return stripped config and info
        if pipe_config[0] == '/':
            return pipe_config, None
        # this is a remote stream, separate out the node name
        pieces = pipe_config.split(' ')
        node = pieces[0]
        pipe_config = pieces[1]
    except (ValueError, IndexError):
        raise ConfigurationError("invalid pipe configuration [%s]" % pipe_config)
    return pipe_config, node


def parse_pipe_config(pipe_config: str) -> Tuple[str, str, str]:
    # convert /path/name:datatype[e0,e1,e2] into (/path, name, datatype[e0,e1,e2])
    if ':' in pipe_config:
        full_path = pipe_config.split(':')[0]
        inline_config = pipe_config.split(':')[1]
    else:
        full_path = pipe_config
        inline_config = ""
    if '/' not in full_path:  
        # this is a double check, missing / will be caught earlier
        raise ConfigurationError("invalid path [%s]" % pipe_config) #pragma: no cover
    path_chunks = full_path.split('/')
    name = path_chunks.pop()
    if name == "":
        raise ConfigurationError("invalid stream name [%s]" % pipe_config)
    path = '/'.join(path_chunks)
    return path, name, inline_config


def parse_inline_config(inline_config: str) -> Tuple[DataStream.DATATYPE, List[str]]:
    if len(inline_config) == 0:
        return None, None
    try:
        config = inline_config.split('[')
        if len(config) != 2 or inline_config[-1] != ']':
            raise ConfigurationError("format is datatype[e1,e2,e3,...]")
        datatype = data_stream.validate_datatype(config[0].strip())
        element_names = [e.strip() for e in config[1].strip()[:-1].split(",")]
        return datatype, element_names
    except ConfigurationError as e:
        raise ConfigurationError("invalid inline configuration: %s" % inline_config) from e


def _validate_config_match(existing_stream: DataStream,
                           datatype: DataStream.DATATYPE,
                           elem_names: List[str]):
    # verify data_type match if specified
    if (datatype is not None and
            datatype != existing_stream.datatype):
        raise ConfigurationError("DataStream [%s] exists with data_type %s" %
                                 (existing_stream.name,
                                  existing_stream.datatype))

    # verify elem_names
    existing_names = [e.name for e in existing_stream.elements]
    if len(existing_names) != len(elem_names):
        raise ConfigurationError("DataStream exists with different elements")
    for name in elem_names:
        if name not in existing_names:
            raise ConfigurationError("DataStream exists with different elements")
