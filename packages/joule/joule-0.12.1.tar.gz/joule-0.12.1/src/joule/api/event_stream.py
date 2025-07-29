from typing import Optional, Dict, Union, List
import json
import re
import logging
log = logging.getLogger('joule')

from .session import BaseSession
from .folder_type import Folder
from .event import Event
from .event import from_json as event_from_json
from joule import errors
from joule.utilities.validators import validate_event_fields
from joule.constants import EndPoints

EVENT_READ_BLOCK_SIZE = 1000 # Read 1000 events at a time

class EventStream:
    """
        API EventStream model. See :ref:`sec-node-event-stream-actions` for details on using the API to
        manipulate event streams.

        Parameters:
            name (str): stream name, must be unique in the parent
            description (str): optional field
    """

    def __init__(self, name: str = "",
                 description: str = "",
                 chunk_duration: str = "",
                 chunk_duration_us: Optional[int] = None,
                 keep_us: int = -1,
                 event_fields: Optional[Dict[str, str]] = None):
        self._id = None
        self.name = name
        self.description = description
        if chunk_duration_us is not None:
            if chunk_duration != "":
                raise errors.ApiError("specify either chunk_duration or chunk_duration_us, not both")
            self.chunk_duration_us = chunk_duration_us
        else:
            self.chunk_duration_us = self._parse_time_duration(chunk_duration)
        if event_fields is None:
            self.event_fields = {}
        else:
            self.event_fields = validate_event_fields(event_fields)
        self.keep_us = keep_us

    @property
    def id(self) -> int:
        if self._id is None:
            raise errors.ApiError("this is a local model with no ID. See API docs")
        return self._id

    @id.setter
    def id(self, value: int):
        self._id = value

    def to_json(self) -> Dict:
        return {
            "id": self._id,
            "name": self.name,
            "description": self.description,
            "event_fields": self.event_fields,
            "chunk_duration_us": self.chunk_duration_us,
            "keep_us": self.keep_us
        }

    def __repr__(self):
        return "<joule.api.EventStream id=%r name=%r description=%r>" % (
            self._id, self.name, self.description
        )
        

    def _parse_time_duration(self, duration_str):
        # if duration is already a number interpret it as us
        try:
            return int(duration_str)
        except ValueError:
            pass
        # if it is empty use 0 (no hypertables)
        if duration_str == "":
            return 0
        #print(f"duration string: {duration_str}")
        # otherwise expect a time unit and compute accordingly
        match = re.fullmatch(r'^(\d+)([hdwmy])$', duration_str)
        if match is None:
            raise errors.ApiError("invalid duration "
                                  "use format #unit (eg 1w)")

        units = {
            'h': 60 * 60 * 1e6,  # hours
            'd': 24 * 60 * 60 * 1e6,  # days
            'w': 7 * 24 * 60 * 60 * 1e6,  # weeks
            'm': 4 * 7 * 24 * 60 * 60 * 1e6,  # months
            'y': 365 * 24 * 60 * 60 * 1e6  # years
        }
        unit = match.group(2)
        time = int(match.group(1))
        if time <= 0:
            raise errors.ApiError("invalid duration "
                                  "use format #unit (eg 1w), none or all")
        return int(time * units[unit])


def from_json(json: dict) -> EventStream:
    my_stream = EventStream()
    my_stream.id = json['id']
    my_stream.name = json['name']
    my_stream.description = json['description']
    my_stream.event_fields = json['event_fields']
    my_stream.keep_us = json['keep_us']
    # use a default of 0 for backwards compatability
    my_stream.chunk_duration_us = json.get("chunk_duration_us", 0)
    return my_stream


class EventStreamInfo:
    """
        API EventStreamInfo model. Received from :meth:`Node.event_stream_info` and should not be created directly.


        Parameters:
            start (int): timestamp in UNIX microseconds of the beginning of the first event
            end (int): timestamp in UNIX microsseconds of the end of the last data event
            event_count (int): number of events in the stream
            bytes (int): approximate size of the data on disk
            total_time (int): event stream duration in microseconds (start-end)

        """

    def __init__(self, start: Optional[int], end: Optional[int], event_count: int,
                 total_time: int = 0, bytes: int = 0):
        self.start = start
        self.end = end
        self.event_count = event_count
        self.bytes = bytes
        self.total_time = total_time

    def __repr__(self):
        return "<joule.api.EventStreamInfo start=%r end=%r event_count=%r, total_time=%r>" % (
            self.start, self.end, self.event_count, self.total_time)


def info_from_json(json) -> EventStreamInfo:
    if json is not None:

        return EventStreamInfo(json['start'],
                               json['end'],
                               json['event_count'],
                               json['total_time'],
                               json['bytes'])
    else:
        return EventStreamInfo(None,
                               None,
                               0,
                               0,
                               0)


async def event_stream_delete(session: BaseSession,
                              stream: EventStream | str | int) -> None:
    data = {}
    if type(stream) is EventStream:
        data["id"] = stream.id
    elif type(stream) is int:
        data["id"] = stream
    elif type(stream) is str:
        data["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()

    await session.delete(EndPoints.event, data)


async def event_stream_create(session: BaseSession,
                              stream: EventStream, folder: Folder | str | int) -> EventStream:
    data = {"stream": stream.to_json()}

    if type(folder) is Folder:
        data["dest_id"] = folder.id  # raises error if id is None
    elif type(folder) is int:
        data["dest_id"] = folder
    elif type(folder) is str:
        data["dest_path"] = folder
    else:
        raise errors.ApiError("Invalid folder datatype. Must be Folder, Path, or ID")

    resp = await session.post(EndPoints.event, json=data)
    return from_json(resp)


async def event_stream_info(session: BaseSession,
                            stream: EventStream | str | int) -> EventStreamInfo:
    data = {}

    if type(stream) is EventStream:
        data["id"] = stream.id  # raises error if id is None
    elif type(stream) is int:
        data["id"] = stream
    elif type(stream) is str:
        data["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()

    resp = await session.get(EndPoints.event, data)
    return info_from_json(resp['data_info'])


async def event_stream_get(session: BaseSession,
                           stream: EventStream | str | int,
                           create: bool = False,
                           description: str = "",
                           chunk_duration: str = "",
                           chunk_duration_us: Optional[int] = None,
                           event_fields=None) -> EventStream:
    data = {}

    if type(stream) is EventStream:
        data["id"] = stream.id
    elif type(stream) is int:
        data["id"] = stream
    elif type(stream) is str:
        data["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()

    try:
        resp = await session.get(EndPoints.event, data)
    except errors.ApiError as e:
        # pass the error if the stream should not or cannot be created
        if not create or type(stream) is not str:
            raise e
        name = stream.split('/')[-1]
        path = '/'.join(stream.split('/')[:-1])
        event_stream = EventStream(name, description,
                                   chunk_duration=chunk_duration,
                                   chunk_duration_us=chunk_duration_us,
                                   event_fields=event_fields)
        return await event_stream_create(session, event_stream, path)
    return from_json(resp)


async def event_stream_update(session: BaseSession,
                              stream: EventStream) -> None:
    # validate the event fields before sending
    validate_event_fields(stream.event_fields)
    await session.put(EndPoints.event, {"id": stream.id,
                                      "stream": stream.to_json()})


async def event_stream_move(session: BaseSession,
                            source: EventStream | str | int,
                            destination: Folder | str | int) -> None:
    data = {}

    if type(source) is EventStream:
        data["src_id"] = source.id
    elif type(source) is int:
        data["src_id"] = source
    elif type(source) is str:
        data["src_path"] = source
    else:
        raise errors.ApiError("Invalid source datatype. Must be EventStream, Path, or ID")

    if type(destination) is Folder:
        data["dest_id"] = destination.id
    elif type(destination) is int:
        data["dest_id"] = destination
    elif type(destination) is str:
        data["dest_path"] = destination
    else:
        raise errors.ApiError("Invalid destination datatype. Must be Folder, Path, or ID")
    await session.put(EndPoints.event_move, data)


async def event_stream_write(session: BaseSession,
                             stream: EventStream | str | int,
                             events: List[Event]) -> List[Event]:
    data = {}
    if type(stream) is EventStream:
        data["id"] = stream.id
    elif type(stream) is int:
        data["id"] = stream
    elif type(stream) is str:
        data["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()
    # get the node UUID to make sure events can be associated with the correct node during copy operations
    resp = await session.get(EndPoints.version_json)
    node_uuid = resp['uuid']
    # post events in blocks
    rx_events = []
    for idx in range(0, len(events), 500):
        chunk = events[idx:idx + 500]
        data['events'] = [e.to_json(destination_node_uuid=node_uuid) for e in events[idx:idx + 500]]
        resp = await session.post(EndPoints.event_data, data)
        rx_events += [event_from_json(e, node_uuid=node_uuid) for e in resp["events"]]
        # copy the ids over
        for i in range(len(chunk)):
            chunk[i].id = rx_events[i].id
    return events


async def event_stream_count(session: BaseSession,
                             stream: EventStream | str | int,
                             start_time: Optional[int],
                             end_time: Optional[int],
                             json_filter,
                             include_on_going_events) -> List[Event]:
    params = {}
    if type(stream) is EventStream:
        params["id"] = stream.id
    elif type(stream) is int:
        params["id"] = stream
    elif type(stream) is str:
        params["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()
    if start_time is not None:
        params['start'] = int(start_time)
    if end_time is not None:
        params['end'] = int(end_time)
    if json_filter is not None:
        params['filter'] = json_filter
    if include_on_going_events:
        params['include-ongoing-events'] = 1
    resp = await session.get(EndPoints.event_data_count, params)
    return resp["count"]

async def event_stream_read_list(session: BaseSession,
                                stream: EventStream | str | int,
                                start_time: Optional[int],
                                end_time: Optional[int],
                                json_filter,
                                include_on_going_events,
                                limit)-> List[Event]:
    if limit <= 0:
        raise errors.ApiError("limit must be an integer > 0")
    all_events = []
    async for events in event_stream_read(session=session, stream=stream, start_time=start_time, end_time=end_time, json_filter=json_filter,
                                         include_on_going_events=include_on_going_events, block_size=EVENT_READ_BLOCK_SIZE):
        all_events += events
        if len(all_events) >= limit:
            log.warning(f"Read limit of {limit} events reached before end of stream")
            break
    return all_events[:limit]
        
async def event_stream_read(session: BaseSession,
                            stream: EventStream | str | int,
                            start_time: Optional[int],
                            end_time: Optional[int],
                            json_filter,
                            include_on_going_events,
                            block_size: Optional[int]):
    params = {}
    if type(stream) is EventStream:
        params["id"] = stream.id
    elif type(stream) is int:
        params["id"] = stream
    elif type(stream) is str:
        params["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()
    if start_time is not None:
        params['start'] = int(start_time)
    if end_time is not None:
        params['end'] = int(end_time)
    if block_size is None:
        params['limit'] = EVENT_READ_BLOCK_SIZE
    else:
        params['limit'] = block_size
    params['return-subset'] = 1
    if json_filter is not None:
        params['filter'] = json_filter
    if include_on_going_events:
        params['include-ongoing-events'] = 1

    # get the node UUID to make sure events can be associated with the correct node during copy operations
    resp = await session.get(EndPoints.version_json)
    node_uuid = resp['uuid']
    
    # read events in blocks and provide to client as a generator
    while True:
        resp = await session.get(EndPoints.event_data, params)
        events_json = resp["events"]
        events = [event_from_json(e, node_uuid=node_uuid) for e in events_json]
        # if no events are returned, we are done
        if len(events)==0:
            break
        #print(f"Retrieved {len(events)} from {ts2h(events[0].start_time)} to {ts2h(events[-1].start_time)}")
        if block_size is not None:
            yield events
        else:
            for event in events:
                yield event
        # update the start time to get the next block
        params['start'] = events[-1].start_time+1
        if end_time is not None and params['start'] >= end_time:
            break
        params['include-ongoing-events'] = 0 # should always be set false after the first pass

async def event_stream_remove(session: BaseSession,
                              stream: EventStream | str | int,
                              start_time: Optional[int] = None,
                              end_time: Optional[int] = None,
                              json_filter=None) -> None:
    params = {}
    if type(stream) is EventStream:
        params["id"] = stream.id
    elif type(stream) is int:
        params["id"] = stream
    elif type(stream) is str:
        params["path"] = stream
    else:
        raise errors.InvalidEventStreamParameter()
    if start_time is not None:
        params['start'] = int(start_time)
    if end_time is not None:
        params['end'] = int(end_time)
    if json_filter is not None:
        params['filter'] = json_filter
    await session.delete(EndPoints.event_data, params)
