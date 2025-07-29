#!/usr/bin/env python3

import joule.client
import asyncio

import joule.errors


class Adder(joule.client.FilterModule):
    """ Add DC offset to input """
    
    def custom_args(self, parser):
        parser.add_argument("offset", type=int, default=0,
                            help="apply an offset")
        
    async def run(self, parsed_args, inputs, outputs):
        stream_in: joule = inputs["input"]
        stream_out = outputs["output"]
        while not self.stop_requested and await stream_in.not_empty():
            sarray = await stream_in.read()
            sarray["data"] += parsed_args.offset
            await asyncio.sleep(0.25)
            await stream_out.write(sarray)
            stream_in.consume(len(sarray))
            if stream_in.end_of_interval:
                print("closing interval")
                await stream_out.close_interval()
            

if __name__ == "__main__":
    r = Adder()
    r.start()
