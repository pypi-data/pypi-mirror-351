import numpy as np
import io
from struct import pack
import datetime
import asyncpg
from typing import List, Optional, Tuple, Dict
import logging
from joule.utilities import datetime_to_timestamp as dt2ts
import psycopg2.sql

from joule.errors import DataError
from joule.models.data_stream import DataStream
from joule.models.event_stream import EventStream
import joule.utilities

log = logging.getLogger('joule')

postgres_ts_offset = 946684800000000  # January 1 2000 GMT


def data_to_bytes(data: np.ndarray) -> io.BytesIO:
    pgcopy_dtype = [("num_fields", ">i2"),
                    ("time_length", '>i4'),
                    ("time", '>i8')]
    dtype_tuple = data.dtype.descr[1]
    elem_dtype = dtype_tuple[1].replace('<', '>')
    elem_length = data['data'].dtype.alignment
    if len(dtype_tuple) == 3:
        n_elem = dtype_tuple[2][0]
    else:
        n_elem = 1
    for i in range(n_elem):
        pgcopy_dtype += [("elem%d_length" % i, '>i4'),
                         ("elem%d" % i, elem_dtype)]
    pgcopy = np.empty(data.shape, pgcopy_dtype)
    pgcopy['num_fields'] = n_elem + 1
    pgcopy['time_length'] = 8
    pgcopy['time'] = data['timestamp'] - postgres_ts_offset
    for i in range(n_elem):
        pgcopy['elem%d_length' % i] = elem_length
        pgcopy['elem%d' % i] = data['data'][:, i]
    cpy = io.BytesIO()
    # signature, flag field and and header extension (both empty)
    cpy.write(pack('!11sii', b'PGCOPY\n\377\r\n\0', 0, 0))
    cpy.write(pgcopy.tobytes())
    cpy.write(pack('!h', -1))
    cpy.seek(0)
    return cpy


def bytes_to_data(buffer: io.BytesIO, dtype: np.dtype) -> np.ndarray:
    pgcopy_dtype = [("num_fields", ">i2"),
                    ("time_length", '>i4'),
                    ("time", '>i8')]
    dtype_tuple = dtype.descr[1]
    elem_dtype = dtype_tuple[1].replace('<', '>')
    elem_length = dtype['data'].alignment
    if len(dtype_tuple) == 3:
        n_elem = dtype_tuple[2][0]
    else:
        n_elem = 1
    for i in range(n_elem):
        pgcopy_dtype += [("elem%d_length" % i, '>i4'),
                         ("elem%d" % i, elem_dtype)]
    pgcopy_dtype = np.dtype(pgcopy_dtype)
    nbytes = buffer.seek(0, io.SEEK_END)
    buffer.seek(0)
    # check the header
    header = pack('!11sii', b'PGCOPY\n\377\r\n\0', 0, 0)
    rx_header = buffer.read(len(header))
    if rx_header != header:
        raise DataError("bad pgcopy header")
    row_size = pgcopy_dtype.itemsize
    if (nbytes - 21) % row_size != 0:
        raise DataError("invalid number of data bytes")
    nrows = (nbytes - 21) // row_size
    tuple_data = np.frombuffer(buffer.read(nbytes - 21), pgcopy_dtype)
    rx_data = np.empty(nrows, dtype)
    rx_data['timestamp'] = tuple_data['time'] + postgres_ts_offset
    for i in range(n_elem):
        rx_data['data'][:, i] = tuple_data['elem%d' % i]
    # reader the footer
    footer = pack('!h', -1)
    rx_footer = buffer.read()
    if footer != rx_footer:
        raise DataError("ERROR: invalid footer")
    return rx_data


def query_time_bounds(start, end, start_col_name='time', end_col_name=None):
    # bounds are [ --- )
    limits = []
    if start is not None:
        if type(start) is not datetime.datetime:
            start = datetime.datetime.fromtimestamp(start / 1e6, tz=datetime.timezone.utc)
        if end_col_name is not None:  # interval query
            limits.append(f"{end_col_name} >= '{start}'")
        else:  # point query
            limits.append(f"{start_col_name} >= '{start}'")
    if end is not None:
        if type(end) is not datetime.datetime:
            end = datetime.datetime.fromtimestamp(end / 1e6, tz=datetime.timezone.utc)
        limits.append(f"{start_col_name} < '{end}'")
    if len(limits) > 0:
        return ' AND '.join(limits)
    else:
        return ''


EventFilter = Tuple[str, str, str]
EventFilterGroup = List[EventFilter]  # AND clauses
EventFilterGroups = List[EventFilterGroup]  # OR between groups


def query_event_json(filter_groups: EventFilter) -> str:
    groups = []
    for group in filter_groups:
        clauses = []
        for clause in group:
            if len(clause) != 3:
                raise ValueError("invalid clause, must be [key,comparison,value]")
            key, comparison, value = clause
            key_safe = key.replace("'", "''")
            if comparison in ['is', 'not', 'like', 'unlike']:
                value_safe = value.replace("'", "''")
                if comparison == 'is':
                    clauses.append(f"(content->>'{key_safe}'='{value_safe}')")
                elif comparison == 'not':
                    clauses.append(f"(NOT (content->>'{key_safe}'='{value_safe}'))")
                elif comparison == 'like':
                    clauses.append(f"(content->>'{key_safe}' like '{value_safe}')")
                elif comparison == 'unlike':
                    clauses.append(f"(content->>'{key_safe}' not like '{value_safe}')")
            elif comparison == 'gt':
                clauses.append(f"(CAST (content->>'{key_safe}' AS FLOAT)>{float(value)})")
            elif comparison == 'gte':
                clauses.append(f"(CAST (content->>'{key_safe}' AS FLOAT)>={float(value)})")
            elif comparison == 'lt':
                clauses.append(f"(CAST (content->>'{key_safe}' AS FLOAT)<{float(value)})")
            elif comparison == 'lte':
                clauses.append(f"(CAST (content->>'{key_safe}' AS FLOAT)<={float(value)})")
            elif comparison == 'eq':
                clauses.append(f"(CAST (content->>'{key_safe}' AS FLOAT)={float(value)})")
            elif comparison == 'neq':
                clauses.append(f"(NOT CAST (content->>'{key_safe}' AS FLOAT)={float(value)})")
            else:
                raise ValueError(f"Invalid comparison {comparison}, must be [gt|gte|lt|lte|eq|neq|is|not|like|unlike]")
        groups.append(' AND '.join(clauses))
    sql_query = " OR ".join(groups)
    return f"({sql_query})"


async def create_event_table(conn: asyncpg.Connection, stream: 'EventStream'):
    # first check if the table exists
    table_name = f"data.event{stream.id}"
    sql = f"SELECT to_regclass('{table_name }');"
    result = await conn.fetchval(sql)
    if result is not None:
        return  # nothing to do, table exists

    sql = f"""CREATE TABLE {table_name } (
    id SERIAL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    content JSONB
    )"""
    await conn.execute(sql)
    if stream.chunk_duration_us > 0:
        sql = f"""SELECT create_hypertable('{table_name }', 'start_time')"""
        await conn.execute(sql)
        await update_chunk_interval(conn, table_name, stream.chunk_duration_us)
    sql = f"""CREATE INDEX ON {table_name} (start_time, end_time)"""
    await conn.execute(sql)
    sql = f"""GRANT SELECT ON {table_name} TO joule_module"""
    await conn.execute(sql)


async def create_stream_table(conn: asyncpg.Connection, stream: DataStream):
    n_elems = len(stream.elements)
    # create the main table
    col_type = get_psql_type(stream.datatype)
    cols = ["elem%d %s NOT NULL" % (x, col_type) for x in range(n_elems)]
    sql = "CREATE TABLE IF NOT EXISTS data.stream%d (" % stream.id + \
          "time TIMESTAMP NOT NULL," + \
          ', '.join(cols) + \
          ", PRIMARY KEY(time));"
    await conn.execute(sql)
    sql = f"SELECT create_hypertable('data.stream{stream.id}', 'time', if_not_exists=>true);"
    await conn.execute(sql)
    sql = f"GRANT SELECT ON data.stream{stream.id} TO joule_module;"
    await conn.execute(sql)
    # create interval table
    sql = f"CREATE TABLE IF NOT EXISTS data.stream{stream.id}_intervals (time TIMESTAMP NOT NULL);"
    await conn.execute(sql)


async def create_decimation_table(conn: asyncpg.Connection, stream: DataStream, level: int):
    n_elems = len(stream.elements)
    table_name = 'data.stream%d_%d' % (stream.id, level)
    # create decimation table (just a template)
    mean_cols = ["elem%d REAL NOT NULL" % x for x in range(n_elems)]
    min_cols = ["elem%d_min REAL NOT NULL" % x for x in range(n_elems)]
    max_cols = ["elem%d_max REAL NOT NULL" % x for x in range(n_elems)]
    cols = mean_cols + min_cols + max_cols
    sql = "CREATE TABLE IF NOT EXISTS %s (" % table_name + \
          "time TIMESTAMP NOT NULL," + \
          ', '.join(cols) + \
          ", PRIMARY KEY(time));"
    await conn.execute(sql)
    # use the default chunk interval, this will be updated by the decimator process
    sql = f"""
        SELECT create_hypertable('{table_name}', 'time',
        if_not_exists=>true);
    """
    # print(f"SQL: {sql}")
    await conn.execute(sql)


async def drop_decimation_tables(conn: asyncpg.Connection, stream: DataStream):
    tables = await get_decimation_table_names(conn, stream, with_schema=True)
    for table in tables:
        try:
            await conn.execute(f"DROP TABLE {table}")
        except asyncpg.UndefinedTableError:
            pass


def get_psql_type(x: DataStream.DATATYPE):
    if x == DataStream.DATATYPE.FLOAT32:
        return 'real'
    elif x == DataStream.DATATYPE.FLOAT64:
        return 'double precision'
    elif x == DataStream.DATATYPE.INT16:
        return 'smallint'
    elif x == DataStream.DATATYPE.INT32:
        return 'integer'
    elif x == DataStream.DATATYPE.INT64:
        return 'bigint'
    else:
        # NOTE: All other datatypes have been removed from DATATYPE
        # so this code is unreachable, but it is left here to catch
        # errors from any future changes to DATATYPE
        raise DataError("Invalid type [%r] for timescale backend" % x)


async def get_row_count(conn: asyncpg.Connection, stream: DataStream,
                        start=None, end=None):
    # hyper table approximate row count is not sensitive to data removal
    # always use the custom function
    try:
        bounds = await convert_time_bounds(conn, stream, start, end)
    except asyncpg.UndefinedTableError:
        return 0  # no data tables for this stream
    if bounds is None:
        return 0  # no data
    start, end = bounds
    query = "SELECT stream_row_count(%d, '%s', '%s')" % (stream.id, start, end)
    try:
        nrows = await conn.fetchval(query)
    except asyncpg.UndefinedTableError:
        return 0  # no data tables for this stream
    return nrows


async def get_closest_ts(conn: asyncpg.Connection, stream: DataStream, ts: int) -> Optional[datetime.datetime]:
    base_table = "data.stream%d" % stream.id
    dt = datetime.datetime.fromtimestamp(int(ts) / 1e6, tz=datetime.timezone.utc)
    query = f"SELECT time FROM {base_table} WHERE time < '{dt}' ORDER BY time DESC LIMIT 1"
    #print(f"stream: {stream.id} ts: {ts}: query: {query}")

    try:
        last_dt = await conn.fetchval(query)
    except asyncpg.UndefinedTableError:
        # no data tables so no previous timestamp
        return None
    if last_dt is None:
        # no data exists before ts so no previous timestamp
        return None
    # convert the datetime.datetime to a timestamp
    return dt2ts(last_dt)
    
async def remove_interval_breaks(conn: asyncpg.Connection, stream: DataStream, start: int, end: int):
    # remove interval breaks that are no longer needed
    interval_table = "data.stream%d_intervals" % stream.id
    start = datetime.datetime.fromtimestamp(start / 1e6, tz=datetime.timezone.utc)
    end = datetime.datetime.fromtimestamp(end / 1e6, tz=datetime.timezone.utc)
    query = f"DELETE FROM {interval_table} WHERE time >= '{start}' AND time <= '{end}'"
    try:
        await conn.fetch(query)
    except asyncpg.UndefinedTableError:
        return  # no interval table so no breaks to remove

async def close_interval(conn: asyncpg.Connection, stream: DataStream, ts: int):
    # place a boundary 1us *after* ts
    base_table = "data.stream%d" % stream.id
    interval_table = "data.stream%d_intervals" % stream.id
    ts = datetime.datetime.fromtimestamp(ts / 1e6, tz=datetime.timezone.utc)
    # find the most recent data before this boundary (ts)
    query = "SELECT time FROM %s WHERE time <= '%s' ORDER BY time DESC LIMIT 1" % (base_table, ts)
    try:
        last_ts = await conn.fetchval(query)
    except asyncpg.UndefinedTableError:
        # no data tables so no need for an interval boundary
        return
    if last_ts is None:
        # no data exists before ts so no need for an interval boundary
        return
    # check if this interval is necessary
    query = "SELECT time FROM %s WHERE time <= '%s' ORDER BY time DESC LIMIT 1" % (interval_table, ts)
    last_interval = await conn.fetchval(query)
    if last_interval is None or last_ts > last_interval:
        query = "INSERT INTO %s(time) VALUES ($1)" % interval_table
        await conn.execute(query, last_ts + datetime.timedelta(microseconds=1))


async def get_decimation_table_names(conn: asyncpg.Connection, stream: DataStream, with_schema=True) -> List[str]:
    query = r'''select table_name from information_schema.tables 
                  where table_schema='data' 
                  and table_type='BASE TABLE' 
                  and table_name like 'stream%d\_%%';''' % stream.id
    records = await conn.fetch(query)
    all_tables = [r['table_name'] for r in records]
    # omit the interval table
    data_tables = [name for name in all_tables if not name.endswith('intervals')]
    # print(f"data tables: {data_tables}")
    if with_schema:
        return [f'data.{name}' for name in data_tables]
    else:
        return data_tables


async def get_table_names(conn: asyncpg.Connection, stream: DataStream, with_schema=True) -> List[str]:
    tables = await get_decimation_table_names(conn, stream, with_schema)
    if with_schema:
        return tables + [f'data.stream{stream.id}', f'data.stream{stream.id}_intervals']
    else:
        return tables + [f'stream{stream.id}', f'stream{stream.id}_intervals']


async def get_all_table_names(conn: asyncpg.Connection, with_schema=True) -> List[str]:
    """Return a list of all data tables, used when dropping all data from the node"""
    query = r'''select table_name from information_schema.tables 
               where table_schema='data' 
               and table_type='BASE TABLE' 
               and table_name like 'stream%';'''
    records = await conn.fetch(query)
    if with_schema:
        return ['data.' + r['table_name'] for r in records]
    else:
        return [r['table_name'] for r in records]


async def get_boundaries(conn: asyncpg.Connection, stream: DataStream,
                         start: Optional[int], end: Optional[int]) -> List[datetime.datetime]:
    """
    Return a list of data boundaries including the start and end of the data
    """
    bounds = await convert_time_bounds(conn, stream, start, end)
    if bounds is None:
        return []  # no data so no boundaries
    start, end = bounds
    query = "SELECT time FROM data.stream%d_intervals " % stream.id
    where_clause = query_time_bounds(start, end)
    if len(where_clause)>0:
        query += " WHERE " + where_clause
    query += " ORDER BY time ASC"
    try:
        records = await conn.fetch(query)
    except asyncpg.UndefinedTableError:
        return []  # no data tables so no boundaries
    ts = [start] + [r['time'] for r in records] + [end]
    return [x.replace(tzinfo=datetime.timezone.utc) for x in ts]


async def convert_time_bounds(conn: asyncpg.Connection,
                              stream: DataStream,
                              start: Optional[int], end: Optional[int]) -> Optional[
    Tuple[datetime.datetime, datetime.datetime]]:
    """
    Convert Unix us timestamps to datetime objects and populate [None] values with the
    start or end of the data respectively
    """
    if start is None:
        query = "SELECT time FROM data.stream%d ORDER BY time ASC LIMIT 1" % stream.id
        try:
            start = await conn.fetchval(query)
        except asyncpg.UndefinedTableError:
            return None  # no data tables so no valid time bounds
        if start is None:
            # remove intervals?
            return None  # no data so no valid time bounds
        start = start.replace(tzinfo=datetime.timezone.utc)

    else:
        start = datetime.datetime.fromtimestamp(start / 1e6, tz=datetime.timezone.utc)
    if end is None:
        query = "SELECT time FROM data.stream%d ORDER BY time DESC LIMIT 1" % stream.id
        try:
            end = await conn.fetchval(query) + datetime.timedelta(microseconds=1)
        except asyncpg.UndefinedTableError:
            return None  # no data tables so no valid time bounds
        if end is None:
            # remove intervals?
            return None  # no data so no valid time bounds
        end = end.replace(tzinfo=datetime.timezone.utc)
    else:
        end = datetime.datetime.fromtimestamp(end / 1e6, tz=datetime.timezone.utc)
    return start, end


async def limit_time_bounds(conn: asyncpg.Connection,
                            stream: DataStream,
                            start: Optional[int], end: Optional[int]) -> Tuple[Optional[int], Optional[int]]:
    data_bounds = await convert_time_bounds(conn, stream, None, None)
    if data_bounds is None:
        return None, None
    data_start = joule.utilities.datetime_to_timestamp(data_bounds[0])
    data_end = joule.utilities.datetime_to_timestamp(data_bounds[1])
    if start is None:
        start = data_start
    else:
        start = max(start, data_start)
    if end is None:
        end = data_end
    else:
        end = min(end, data_end)
    return start, end


async def update_chunk_interval(conn: asyncpg.Connection, table: str,
                                chunk_interval_us: int):
    if chunk_interval_us == 0:
        return  # invalid chunk interval setting, ignore
    query = f"SELECT set_chunk_time_interval('{table}', {round(chunk_interval_us)})"
    # print(f"QUERY: <{query}>, {round(chunk_interval_ms/(1000*60*60))}") # show in hours
    await conn.execute(query)
