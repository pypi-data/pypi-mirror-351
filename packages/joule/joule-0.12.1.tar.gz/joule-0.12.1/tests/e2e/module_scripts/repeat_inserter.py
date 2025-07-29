#!/usr/bin/env python3

import joule.client
import joule.utilities
import numpy as np
import asyncio
import sys

rows = 100
freq = 40  # Hz


class RepeatInserter(joule.client.ReaderModule):

    async def run(self, parsed_args, output):
        data = 100 * np.sin(np.arange(0, 2 * np.pi, 2 * np.pi / rows))
        data.shape = (rows, 1)

        # 1540239607500500
        data_ts = joule.utilities.time_now()
        orig_ts = data_ts
        count = 0
        ts_inc = 1 / rows * (1 / freq) * 1e6  # microseconds
        while not self.stop_requested:
            top_ts = data_ts + 100 * ts_inc
            count += 1
            ts = np.array(np.linspace(data_ts, top_ts, rows,
                                      endpoint=False), dtype=np.int64)
            ts.shape = (rows, 1)
            ts_data = np.hstack((ts, data))
            await output.write(ts_data)
            data_ts = top_ts
            await asyncio.sleep(1 / freq)
            if count==freq*10 and False:
                # cause overlapping timestamp
                data_ts = orig_ts
                print("resetting", file=sys.stderr)
                count = 0

if __name__ == "__main__":
    r = RepeatInserter()
    r.start()
