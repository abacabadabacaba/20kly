#
# 20,000 Light Years Into Space
# This game is licensed under GPL v2, and copyright (C) Jack Whitham 2006-21.
#

import random
import tempfile
import struct
import bz2
import math

from . import map_items
from . import steam_model
from . import game
from . import ui
from .primitives import *
from .game_types import *

READ_HEADER_NUMBER = 20210307
WRITE_HEADER_NUMBER = 20210307

NamePayloadType = Tuple[str, bytes]

class Game_Random:
    def __init__(self, seed: Optional[int] = None) -> None:
        self.rng: Optional[random.Random] = random.Random(seed)

    def random(self) -> float:
        assert self.rng is not None
        return self.rng.random()

    def randint(self, a: int, b: int) -> int:
        assert self.rng is not None
        return self.rng.randint(a, b)

    def shuffle(self, l: List[typing.Any]) -> None:
        for i in range(1, len(l)):
            j = self.randint(0, i)
            (l[i], l[j]) = (l[j], l[i])

    def hypot(self, dy: float, dx: float) -> float:
        return math.hypot(dy, dx)

    def timestamp(self, g: "game.Game_Data") -> None:
        pass

    def do_user_actions(self, ui: "ui.User_Interface", game: "game.Game") -> None:
        pass

    def Special_Action(self, name: str, game: "game.Game") -> None:       # NO-COV
        pass

    def Action(self, name, *objects) -> None:       # NO-COV
        pass

    def Steam(self, neighbour_list: "List[Tuple[steam_model.Steam_Model, float]]",
              voltage: float, charge: float, capacitance: float,
              currents: List[float]) -> None:
        pass

    def Pre_Save(self) -> None:
        self.rng = None

    def Post_Load(self) -> None:
        self.rng = random.Random()


class Play_and_Record(Game_Random):
    def __init__(self, seed: Optional[int] = None) -> None:
        Game_Random.__init__(self, seed)
        self.record: Optional[bz2.BZ2File] = None
        self.play: Optional[bz2.BZ2File] = None
        self.peek_buffer: Optional[NamePayloadType] = None

    def random(self) -> float:
        x = Game_Random.random(self)
        if self.play:
            (x, ) = self.read_specific("RANDOM", "<d")

        if self.record: # NO-COV
            self.write_specific("RANDOM", "<d", x)

        return x

    def randint(self, a: int, b: int) -> int:
        x = Game_Random.randint(self, a, b)
        assert a <= x <= b
        assert abs(a) <= (1 << 31)
        assert abs(b) <= (1 << 31)

        if self.play:
            (ra, rb, x) = self.read_specific("RANDINT", "<iii")
            assert a == ra
            assert b == rb
            assert a <= x <= b

        if self.record:
            self.write_specific("RANDINT", "<iii", a, b, x)

        return x

    def shuffle(self, l: List[typing.Any]) -> None:
        self.read_and_write("SHUFFLE", "<I", len(l))
        Game_Random.shuffle(self, l)

    def begin_write(self, recording_file: str, challenge: MenuCommand) -> None:
        self.record = bz2.BZ2File(recording_file, "wb")
        seed = random.randint(1, 1 << 31)
        self.write_specific("GAME", "<I", WRITE_HEADER_NUMBER)
        self.write_specific("SEED", "<II", seed, challenge.value)
        self.rng = random.Random(seed)

    def begin_read(self, recording_file: str) -> MenuCommand:
        self.play = bz2.BZ2File(recording_file, "rb")
        (header, ) = self.read_specific("GAME", "<I")
        assert header == READ_HEADER_NUMBER
        (seed, challenge) = self.read_specific("SEED", "<II")
        self.rng = random.Random(seed)
        return MenuCommand(challenge)

    def do_user_actions(self, ui: "ui.User_Interface", game: "game.Game") -> None:
        if not self.play:
            return

        (name, payload) = self.peek_any()
        while name.startswith("ACTION_"):
            if self.record: # NO-COV
                self.read_and_write(name,
                            "<" + str(len(payload)) + "s", payload)
            else:
                self.read_any()

            name = name[7:]
            object_data = struct.unpack("<" + str(len(payload)) + "B", payload)
            if name.startswith("SPECIAL_"):
                name = name[8:]
                game.Special_Action(name)
            else:
                ui.Playback_Action(name, *object_data)
            (name, payload) = self.peek_any()

    def timestamp(self, g: "game.Game_Data") -> None:
        supply = g.net.hub.Get_Steam_Supply()
        demand = g.net.hub.Get_Steam_Demand()

        self.read_and_write("TS", "<dddIII", g.game_time.time(), supply, demand,
                             len(g.net.well_list), len(g.net.node_list), len(g.net.pipe_list))

        for well in sorted(g.net.well_list, key=lambda well: well.pos):
            assert isinstance(well, map_items.Well)
            (x2, y2) = well.pos
            self.read_and_write("W", "<BB", x2, y2)

        for node in sorted(g.net.node_list, key=lambda node: node.pos):
            if isinstance(node, map_items.Well_Node):
                node_code = 1
            else:
                assert isinstance(node, map_items.Node)
                node_code = 2
            (x2, y2) = node.pos
            self.read_and_write("N", "<BBBid", x2, y2, node_code, node.health, node.steam.charge)

        for pipe in sorted(g.net.pipe_list, key=lambda pipe: (pipe.n1.pos, pipe.n2.pos)):
            (x1, y1) = pipe.n1.pos
            (x3, y3) = pipe.n2.pos
            self.read_and_write("P", "<BBBBd", x1, y1, x3, y3, pipe.current_n1_to_n2)

    def Special_Action(self, name: str, game: "game.Game") -> None:       # NO-COV
        self.Action("SPECIAL_" + name)
        game.Special_Action(name)

    def Action(self, name, *objects) -> None:       # NO-COV
        object_data = []
        for obj in objects:
            if isinstance(obj, map_items.Pipe):
                (x, y) = obj.n1.pos
                object_data.append(x)
                object_data.append(y)
                (x, y) = obj.n2.pos
                object_data.append(x)
                object_data.append(y)
            elif isinstance(obj, map_items.Building):
                (x, y) = obj.pos
                object_data.append(x)
                object_data.append(y)
            else:
                assert False, repr(obj)

        self.read_and_write("ACTION_" + name, "<" + str(len(object_data)) + "B", *object_data)

    def Steam(self, neighbour_list: "List[Tuple[steam_model.Steam_Model, float]]",
              voltage: float, charge: float, capacitance: float,
              currents: List[float]) -> None:
        assert len(neighbour_list) == len(currents)
        self.read_and_write("ST", "<Iddd",
                    len(neighbour_list),
                    voltage, charge, capacitance)
        for i in range(len(neighbour_list)):
            (neighbour, resist) = neighbour_list[i]
            self.read_and_write("n", "<dd", resist, currents[i])

    def Pre_Save(self) -> None: # NO-COV
        Game_Random.Pre_Save(self)
        self.record = None
        self.play = None

    def hypot(self, dy: float, dx: float) -> float:
        result = Game_Random.hypot(self, dy, dx)

        if self.play:
            (readback_dy, readback_dx, readback_result) = self.read_specific("HYP", "<ddd")
            assert abs(readback_dy - dy) < 1e-12
            assert abs(readback_dx - dx) < 1e-12
            assert abs(readback_result - result) < 1e-12
            result = readback_result

        if self.record:
            self.write_specific("HYP", "<ddd", dy, dx, result)

        return result

    def read_and_write(self, name: str, fmt: str, *data) -> None:
        if self.play:
            readback = self.read_specific(name, fmt)
            if readback != data:        # NO-COV
                loc = self.play.tell()
                raise PlaybackError("When reading packet before 0x%x, name '%s' matched, "
                                    "but data did not:\n"
                                    "expected data %s\n"
                                    "actually read %s\n" % (loc, name, repr(data), repr(readback)))

        if self.record:
            self.write_specific(name, fmt, *data)

    def write_specific(self, name: str, fmt: str, *data) -> None:
        assert self.record
        name_bytes = name.encode("utf-8")
        payload = struct.pack(fmt, *data)
        header = struct.pack("<BB", len(name_bytes), len(payload))
        self.record.write(header)
        self.record.write(name_bytes)
        self.record.write(payload)

    def peek_any(self) -> NamePayloadType:
        assert self.play
        if self.peek_buffer is None: # NO-COV
            self.peek_buffer = self.read_any()

        return self.peek_buffer

    def read_any(self) -> NamePayloadType:
        assert self.play

        if self.peek_buffer is not None:
            (name, payload) = self.peek_buffer
            self.peek_buffer = None
            return (name, payload)

        header = self.play.read(2)
        if len(header) == 0:
            raise PlaybackEOF()
        if len(header) != 2: # NO-COV
            loc = self.play.tell()
            raise PlaybackError("When reading packet header before 0x%x - unexpected EOF" % loc)

        (len_name, len_payload) = struct.unpack("<BB", header)
        name = self.play.read(len_name).decode("utf-8")
        payload = self.play.read(len_payload)
        if len(payload) != len_payload: # NO-COV
            loc = self.play.tell()
            raise PlaybackError("When reading packet payload before 0x%x - unexpected EOF" % loc)

        return (name, payload)

    def read_specific(self, name: str, fmt: str) -> typing.Sequence[int]:
        (read_name, read_payload) = self.read_any()

        if read_name != name: # NO-COV
            assert self.play
            loc = self.play.tell()
            raise PlaybackError("When reading packet before 0x%x, name did not match:\n"
                                "expected name '%s'\n"
                                "actually read '%s'\n" % (loc, name, read_name))

        try:
            return struct.unpack(fmt, read_payload)
        except Exception: # NO-COV
            raise PlaybackError("When reading packet at 0x%x, name '%s' matched, but "
                                "payload was not decoded" % (loc, name))


class PlaybackError(Exception):
    pass

class PlaybackEOF(Exception):
    pass
