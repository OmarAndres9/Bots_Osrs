from dataclasses import dataclass, field


@dataclass
class Obstacle:
    name: str
    template: str
    wait_time: float


@dataclass
class AgilityCourse:
    name: str
    template_dir: str
    obstacles: list


GNOME_STRONGHOLD = AgilityCourse(
    name="Gnome Stronghold",
    template_dir="gnome_stronghold",
    obstacles=[
        Obstacle("Log Balance",       "log_balance.png",     3.5),
        Obstacle("Obstacle Net 1",    "obstacle_net_1.png",  2.0),
        Obstacle("Tree Branch 1",     "tree_branch_1.png",   2.5),
        Obstacle("Balancing Rope",    "balancing_rope.png",  3.0),
        Obstacle("Tree Branch 2",     "tree_branch_2.png",   2.5),
        Obstacle("Obstacle Net 2",    "obstacle_net_2.png",  2.0),
        Obstacle("Obstacle Pipe",     "obstacle_pipe.png",   3.0),
    ],
)

DRAYNOR = AgilityCourse(
    name="Draynor Village",
    template_dir="draynor",
    obstacles=[
        Obstacle("Rough Wall",        "rough_wall.png",      2.5),
        Obstacle("Tightrope",         "tightrope.png",       3.0),
        Obstacle("Narrow Wall",       "narrow_wall.png",     2.5),
        Obstacle("Wall (up)",         "wall_up.png",         2.0),
        Obstacle("Wall (down)",       "wall_down.png",       2.0),
    ],
)

AL_KHARID = AgilityCourse(
    name="Al Kharid",
    template_dir="alkharid",
    obstacles=[
        Obstacle("Rough Wall",        "rough_wall.png",      2.5),
        Obstacle("Tightrope",         "tightrope.png",       3.5),
        Obstacle("Cable",             "cable.png",           2.5),
        Obstacle("Zip Line",          "zip_line.png",        3.0),
        Obstacle("Stepping Stones",   "stepping_stones.png", 3.0),
        Obstacle("Rope",              "rope.png",            2.0),
    ],
)

VARROCK = AgilityCourse(
    name="Varrock",
    template_dir="varrock",
    obstacles=[
        Obstacle("Rough Wall",        "rough_wall.png",      2.5),
        Obstacle("Clothes Line",      "clothes_line.png",    2.0),
        Obstacle("Leap",              "leap.png",            2.5),
        Obstacle("Balance",           "balance.png",         3.0),
        Obstacle("Leap 2",            "leap_2.png",          2.5),
        Obstacle("Leap 3",            "leap_3.png",          2.5),
    ],
)

CANIFIS = AgilityCourse(
    name="Canifis",
    template_dir="canifis",
    obstacles=[
        Obstacle("Tall Tree",         "tall_tree.png",       2.0),
        Obstacle("Gap 1",             "gap_1.png",           2.5),
        Obstacle("Gap 2",             "gap_2.png",           2.5),
        Obstacle("Gap 3",             "gap_3.png",           2.5),
        Obstacle("Gap 4",             "gap_4.png",           2.5),
        Obstacle("Pole Vault",        "pole_vault.png",      3.0),
        Obstacle("Gap 5",             "gap_5.png",           2.5),
        Obstacle("Ledge",             "ledge.png",           2.0),
        Obstacle("Wall",              "wall.png",            2.0),
    ],
)

FALADOR = AgilityCourse(
    name="Falador",
    template_dir="falador",
    obstacles=[
        Obstacle("Rough Wall",        "rough_wall.png",      3.0),
        Obstacle("Gutter",            "gutter.png",          2.5),
        Obstacle("Ledge 1",           "ledge_1.png",         2.0),
        Obstacle("Ledge 2",           "ledge_2.png",         2.0),
        Obstacle("Ledge 3",           "ledge_3.png",         2.0),
        Obstacle("Ledge 4",           "ledge_4.png",         2.0),
        Obstacle("Ledge 5",           "ledge_5.png",         2.0),
        Obstacle("Wall",              "wall.png",            2.5),
    ],
)

SEERS = AgilityCourse(
    name="Seers' Village",
    template_dir="seers",
    obstacles=[
        Obstacle("Wall",              "wall.png",            2.5),
        Obstacle("Gap 1",             "gap_1.png",           2.5),
        Obstacle("Gap 2",             "gap_2.png",           2.5),
        Obstacle("Gap 3",             "gap_3.png",           2.5),
        Obstacle("Gap 4",             "gap_4.png",           2.5),
        Obstacle("Ledge",             "ledge.png",           2.0),
        Obstacle("Edge",              "edge.png",            2.5),
    ],
)

RELLEKKA = AgilityCourse(
    name="Rellekka",
    template_dir="rellekka",
    obstacles=[
        Obstacle("Rough Wall",        "rough_wall.png",      2.5),
        Obstacle("Gap 1",             "gap_1.png",           2.5),
        Obstacle("Gap 2",             "gap_2.png",           2.5),
        Obstacle("Gap 3",             "gap_3.png",           2.5),
        Obstacle("Gap 4",             "gap_4.png",           2.5),
        Obstacle("Gap 5",             "gap_5.png",           2.5),
        Obstacle("Gap 6",             "gap_6.png",           2.5),
        Obstacle("Gap 7",             "gap_7.png",           2.5),
    ],
)

ARDOUGNE = AgilityCourse(
    name="Ardougne",
    template_dir="ardougne",
    obstacles=[
        Obstacle("Wooden Beams",      "wooden_beams.png",    2.5),
        Obstacle("Gap 1",             "gap_1.png",           2.5),
        Obstacle("Gap 2",             "gap_2.png",           2.5),
        Obstacle("Plank",             "plank.png",           2.5),
        Obstacle("Gap 3",             "gap_3.png",           2.5),
        Obstacle("Gap 4",             "gap_4.png",           2.5),
        Obstacle("Gap 5",             "gap_5.png",           2.5),
    ],
)

ALL_COURSES = {
    "gnome_stronghold": GNOME_STRONGHOLD,
    "draynor":          DRAYNOR,
    "alkharid":         AL_KHARID,
    "varrock":          VARROCK,
    "canifis":          CANIFIS,
    "falador":          FALADOR,
    "seers":            SEERS,
    "rellekka":         RELLEKKA,
    "ardougne":         ARDOUGNE,
}
