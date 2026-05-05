from dataclasses import dataclass
from math import pi
import matplotlib.pyplot as plt
from typing import Iterable, Sequence


RPM_AVG = 90
RPM_MIN = 85
RPM_MAX = 95
DEFAULT_SPAN = 0.7
DEFAULT_AVOID_CROSSOVER = 1


# Cassette sprockets are listed smallest to largest.
CASSETTES = {
    "11s 11-34 105 (CS-HG700)": [11, 13, 15, 17, 19, 21, 23, 25, 27, 30, 34],
    "12s 11-36 105 (CS-HG710)": [11, 12, 13, 14, 15, 17, 19, 21, 24, 28, 32, 36],
    "11s 11-40 SLX (CS-M7000)": [11, 13, 15, 17, 19, 21, 24, 27, 31, 35, 40],
    "11s 11-42 SLX (CS-M7000)": [11, 13, 15, 17, 19, 21, 24, 28, 32, 37, 42],
    "12s 10-51 SLX (CS-M7100)": [10, 12, 14, 16, 18, 21, 24, 28, 33, 39, 45, 51],
    "12s 10-50 Eagle GX":       [10, 12, 14, 16, 18, 21, 24, 28, 32, 36, 42, 50],
    "12s 10-52 Eagle GX":       [10, 12, 14, 16, 18, 21, 24, 28, 32, 36, 42, 52],
}


CHAINRINGS_1X = {
    "MTB": [30, 32, 34],
    "Gravel": [38, 40, 42, 44],
}

CHAINRINGS_2X = {
    "26/36T": [26, 36],
    "28/38T": [28, 38],
    "30/46T": [30, 46],
    "31/48T": [31, 48],
    "34/50T": [34, 50],
    "36/52T": [36, 52],
}


# rim_diameter_mm, width_mm
TIRE_SPECS = {
    # Road/ Gravel sizes
    "700c x 28mm": (622, 28),
    "700c x 35mm": (622, 35),
    "700c x 40mm": (622, 40),
    "700c x 45mm": (622, 45),
    "650b x 40mm": (584, 40),
    "650b x 45mm": (584, 45),
    # MTB sizes
    "27.5\" x 2.25\"": (584, 57.15),
    "29\" x 2.25\"":   (622, 57.15),
    "29\" x 2.35\"":   (622, 59.69),
    "29\" x 2.4\"":    (622, 60.96),
}


@dataclass(frozen=True)
class BikeSpec:
    name: str
    color: str
    chainrings: Sequence[int]
    cassette: Sequence[int]
    tire: str


DEFAULT_BIKES = [
    BikeSpec(
        name="Road 105 2x11",
        color="#22dd22",
        chainrings=CHAINRINGS_2X["34/50T"],
        cassette=CASSETTES["11s 11-34 105 (CS-HG700)"],
        tire="700c x 35mm",
    ),
    BikeSpec(
        name="GRX 820 2x12",
        color="#666688",
        chainrings=CHAINRINGS_2X["31/48T"],
        cassette=CASSETTES["12s 11-36 105 (CS-HG710)"],
        tire="700c x 45mm",
    ),
    BikeSpec(
        name="Custom GRX 2x11",
        color="#5588ff",
        chainrings=CHAINRINGS_2X["30/46T"],
        cassette=CASSETTES["11s 11-42 SLX (CS-M7000)"],
        tire="700c x 40mm",
    ),
    BikeSpec(
        name="MTB Eagle 1x12",
        color="#ff8800",
        chainrings=[34],
        cassette=CASSETTES["12s 10-52 Eagle GX"],
        tire='29" x 2.35"',
    ),
    BikeSpec(
        name="MTB SLX 1x12",
        color="#aa2222",
        chainrings=[30],
        cassette=CASSETTES["12s 10-51 SLX (CS-M7100)"],
        tire='29" x 2.4"',
    ),
]


def tire_circumference_m(tire_name: str) -> float:
    rim_mm, width_mm = TIRE_SPECS[tire_name]
    diameter_mm = rim_mm + (2 * width_mm)
    return (diameter_mm / 1000.0) * pi


def gear_ratio(chainring: int, sprocket: int) -> float:
    return chainring / sprocket


def speed_kmh(cadence_rpm: float, ratio: float, circumference_m: float) -> float:
    meters_per_min = cadence_rpm * ratio * circumference_m
    return (meters_per_min * 60.0) / 1000.0


def _filter_crossover_gears(
    chainrings: Sequence[int],
    cassette: Sequence[int],
    avoid_crossover: int,
) -> list[tuple[int, int]]:
    if len(chainrings) < 2 or avoid_crossover <= 0:
        return [(ring, cog) for ring in chainrings for cog in cassette]

    chainrings_sorted = sorted(chainrings)
    smallest_ring = chainrings_sorted[0]
    largest_ring = chainrings_sorted[-1]

    smallest_cogs = cassette[:avoid_crossover]
    largest_cogs = cassette[-avoid_crossover:]

    gears = []
    for ring in chainrings_sorted:
        for cog in cassette:
            if ring == smallest_ring and cog in smallest_cogs:
                continue
            if ring == largest_ring and cog in largest_cogs:
                continue
            gears.append((ring, cog))
    return gears


def build_gear_rows(
    bike: BikeSpec,
    avoid_crossover: int = DEFAULT_AVOID_CROSSOVER,
) -> list[tuple[int, int, float, float, float, float]]:
    circumference = tire_circumference_m(bike.tire)
    gear_pairs = _filter_crossover_gears(bike.chainrings, bike.cassette, avoid_crossover)
    gear_rows = []
    for ring, cog in gear_pairs:
        ratio = gear_ratio(ring, cog)
        speed_avg = speed_kmh(RPM_AVG, ratio, circumference)
        speed_min = speed_kmh(RPM_MIN, ratio, circumference)
        speed_max = speed_kmh(RPM_MAX, ratio, circumference)
        gear_rows.append((ring, cog, ratio, speed_avg, speed_min, speed_max))

    gear_rows.sort(key=lambda item: item[2])
    return gear_rows


def _y_positions(index: int, count: int, span: float) -> list[float]:
    if count == 1:
        return [float(index)]

    start = index - span
    end = index + span
    step = (end - start) / (count - 1)
    return [start + (step * i) for i in range(count)]

def extended_labels(bikes: Sequence[BikeSpec]) -> list[str]:
    labels = []
    for bike in bikes:
        # Mathtext collapses plain spaces; escape them so the visible name stays unchanged.
        bike_name = bike.name.replace(" ", r"\ ")
        label = f"$\\bf{{{bike_name}}}$"
        if len(bike.chainrings) == 1:
            label += f"\n$\\bf{{CR:}}$ {bike.chainrings[0]}T" # chainring size
        else:
            label += f"\n$\\bf{{CR:}}$ {'/'.join(str(r) for r in bike.chainrings)}T" # multiple chainring sizes
        label += f"\n$\\bf{{CS:}}$ {bike.cassette[0]}-{bike.cassette[-1]}T" # sprocket range
        label += f"\n$\\bf{{Tire:}}$ {bike.tire}" # tire width
        labels.append(label)
    return labels

def plot_gear_scatter(
    bikes: Iterable[BikeSpec],
    span: float = DEFAULT_SPAN,
    avoid_crossover: int = DEFAULT_AVOID_CROSSOVER,
):

    fig, ax = plt.subplots(figsize=(10, 16))

    bikes_list = list(bikes)
    for idx, bike in enumerate(bikes_list, start=1):
        gear_rows = build_gear_rows(bike, avoid_crossover=avoid_crossover)
        y_values = _y_positions(idx, len(gear_rows), span)

        for (ring, cog, ratio, avg, minimum, maximum), y in zip(gear_rows, y_values):
            xerr = [[avg - minimum], [maximum - avg]]
            ax.errorbar(
                avg,
                y,
                xerr=xerr,
                fmt="o",
                color=bike.color,
                ecolor=bike.color,
                elinewidth=1.2,
                capsize=2,
                markersize=5,
            )
            label = f"F{ring}-R{cog}"
            ax.text(
                avg,
                y + 0.02,
                label,
                color=bike.color,
                fontsize=7,
                ha="center",
                va="bottom",
            )
            
    # x labels
    ax.set_xlabel("Speed (km/h)")
    # y labels
    ax.set_yticks(list(range(1, len(bikes_list) + 1)))
    bike_labels = extended_labels(bikes_list)
    # Align label boxes to the axis while keeping multiline text left-aligned.
    ax.set_yticklabels(bike_labels, horizontalalignment="right")
    ax.tick_params(axis="y", pad=0)
    for label in ax.get_yticklabels():
        label.set_multialignment("left")
    # grid lines
    ax.grid(axis="x", linestyle="--", alpha=0.9, which="major")
    ax.minorticks_on()
    ax.grid(axis="x", linestyle=":", alpha=0.7, which="minor")
    
    ax.title.set_text(f"Speeds at RPMs {RPM_MIN}-{RPM_MAX} (avg {RPM_AVG})")

    fig.tight_layout()
    return fig, ax

if __name__ == "__main__":
    plot_gear_scatter(DEFAULT_BIKES)
    plt.savefig("gear_ratios.png", dpi=150)