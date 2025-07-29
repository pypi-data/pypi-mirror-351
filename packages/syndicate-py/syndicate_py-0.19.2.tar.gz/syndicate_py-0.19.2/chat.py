import sys
import argparse
import asyncio
import random
import syndicate
from syndicate import patterns as P, actor, dataspace, turn

from syndicate.schema import sturdy

from preserves.schema import load_schema_file
simpleChatProtocol = load_schema_file('./chat.bin').chat

parser = argparse.ArgumentParser(description='Simple dataspace-server-mediated text chat.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--address', metavar='\'<tcp "HOST" PORT>\'',
                    help='transport address of the server',
                    default='<ws "ws://localhost:9001/">')
parser.add_argument('--cap', metavar='\'<ref ...>\'',
                    help='capability for the dataspace on the server',
                    default='<ref {oid: "syndicate" sig: #[acowDB2/oI+6aSEC3YIxGg==]}>')
args = parser.parse_args()

Present = simpleChatProtocol.Present
Says = simpleChatProtocol.Says

@actor.run_system(name = 'chat', debug = False)
def main():
    root_facet = turn.active_facet()

    @syndicate.relay.connect(args.address, sturdy.SturdyRef.decode(syndicate.parse(args.cap)))
    def on_connected(ds):
        turn.on_stop(lambda: turn.stop(root_facet))

        me = 'user_' + str(random.randint(10, 1000))

        turn.publish(ds, Present(me))

        @dataspace.during(ds, P.rec('Present', P.CAPTURE), inert_ok=True)
        def on_presence(who):
            print('%s joined' % (who,))
            turn.on_stop(lambda: print('%s left' % (who,)))

        @dataspace.on_message(ds, P.rec('Says', P.CAPTURE, P.CAPTURE))
        def on_says(who, what):
            print('%s says %r' % (who, what))

        @turn.linked_task()
        async def accept_input(f):
            reader = asyncio.StreamReader()
            await f.loop.connect_read_pipe(lambda: asyncio.StreamReaderProtocol(reader), sys.stdin)
            while line := (await reader.readline()).decode('utf-8'):
                turn.external(f, lambda: turn.send(ds, Says(me, line.strip())))
