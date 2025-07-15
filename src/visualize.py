from typing import Dict, List, Tuple, Any

import matplotlib.colors as mcolors
import matplotlib.patches as patches
import matplotlib.pyplot as plt
from tabulate import tabulate


def desaturate_color(color_name: str, blend_ratio: float = 0.7) -> Tuple[float, float, float]:
    base = mcolors.to_rgb(color_name)
    white = (1.0, 1.0, 1.0)
    return tuple(blend_ratio * c + (1 - blend_ratio) * w for c, w in zip(base, white))


# a palette of distinct colors
DISTINCT_COLORS = [
    "red", "green", "blue", "orange", "purple", "cyan", "magenta",
    "gold", "lime", "brown", "navy", "darkgreen", "crimson", "darkorange",
    "teal", "darkviolet", "deeppink", "indigo", "chocolate", "darkcyan"
]

# desaturate for polygons
SUBTLE_COLORS = [desaturate_color(c, blend_ratio=0.8) for c in DISTINCT_COLORS]


def plot_packing_results(results: List[Dict]) -> None:
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 6))
    if n == 1:
        axes = [axes]

    all_ids = sorted({pl["id"] for r in results for pl in r["placements"]})
    if len(all_ids) > len(SUBTLE_COLORS):
        raise ValueError(
            f"Too many unique piece IDs ({len(all_ids)}); max is {len(SUBTLE_COLORS)}"
        )
    id_to_color = {pid: SUBTLE_COLORS[i] for i, pid in enumerate(all_ids)}

    for ax, res in zip(axes, results):
        version = res["version"]
        W, L = res["fabric_width_cm"], res["fabric_length_cm"]

        ax.set_title(version)
        ax.set_xlim(0, W)
        ax.set_ylim(0, L)
        ax.set_xlabel("Width (cm)")
        ax.set_ylabel("Length (cm)")
        ax.set_aspect("equal")

        ids_in_plot = set()
        for plc in res["placements"]:
            pid = plc["id"]
            ids_in_plot.add(pid)
            color = id_to_color[pid]

            x0, y0 = plc["x_cm"], plc["y_cm"]
            verts = plc["normalized_vertices_cm"]
            shifted = [(x + x0, y + y0) for x, y in verts]

            bbox_w = max(x for x, _ in verts)
            bbox_h = max(y for _, y in verts)

            # bounding box
            ax.add_patch(patches.Rectangle(
                (x0, y0), bbox_w, bbox_h,
                edgecolor=color, facecolor="none",
                linestyle="dotted", linewidth=1.0, zorder=1
            ))
            # polygon
            ax.add_patch(patches.Polygon(
                shifted, closed=True, fill=False,
                edgecolor=color, linewidth=1.5, zorder=2
            ))

        # legend
        handles = [
            patches.Patch(color=id_to_color[pid], label=pid)
            for pid in sorted(ids_in_plot)
        ]
        ax.legend(
            handles, [h.get_label() for h in handles],
            bbox_to_anchor=(1.05, 1), loc="upper left", fontsize="small"
        )

    plt.tight_layout()
    plt.show()


def print_summary_table(results: List[Dict[str, Any]]) -> None:
    summary_rows = []
    for result in results:
        fabric_area = (result["fabric_width_cm"] / 100) * (result["fabric_length_cm"] / 100)
        used_area = result["placed_area_cm2"] / 10000
        waste_area = result["waste_area_cm2"] / 10000
        utilization = used_area / fabric_area * 100

        summary_rows.append([
            result["version"],
            f"{result['placed_count']}/{result['total_count']}",
            f"{fabric_area:.2f} m²",
            f"{used_area:.3f} m²",
            f"{waste_area:.3f} m²",
            f"{utilization:.1f}%",
        ])

    headers = ["Algorithm", "Placed", "Fabric Area", "Used Area", "Waste", "Utilization"]
    print("\n" + tabulate(summary_rows, headers=headers, tablefmt="fancy_grid"))
