from typing import Dict, List, Any

import matplotlib.patches as patches
import matplotlib.pyplot as plt
from tabulate import tabulate

from src.utils.config_loader import load_yaml_config

PASTEL_COLORS = [
    "#aec6cf", "#ffb347", "#77dd77", "#f49ac2",
    "#cfcfc4", "#836953", "#b39eb5", "#fdfd96"
]
config = load_yaml_config()


def plot_packing_results(results: List[Dict[str, Any]]) -> None:
    n = len(results)
    fig, axes = plt.subplots(1, n, figsize=(6 * n, 6))
    if n == 1:
        axes = [axes]

    # assign a pastel color to each piece ID
    all_ids = sorted({pl["id"] for r in results for pl in r["placements"]})
    id_color = {pid: PASTEL_COLORS[i % len(PASTEL_COLORS)]
                for i, pid in enumerate(all_ids)}

    for ax, res in zip(axes, results):
        version = res["version"]
        W, L = res["fabric_width_cm"], res["fabric_length_cm"]

        ax.set_title(version)
        ax.set_xlim(0, W)
        ax.set_ylim(0, L)
        ax.set_xlabel("Width (cm)")
        ax.set_ylabel("Length (cm)")
        ax.set_aspect("equal")

        # draw shelves if present
        for shelf in res.get("shelves", []):
            y0 = shelf["y_cm"]
            y1 = y0 + shelf["height_cm"]
            ax.hlines([y0, y1], xmin=0, xmax=W, color="black", linewidth=1)

        seen = set()
        handles, labels = [], []

        # draw each piece
        for plc in res["placements"]:
            pid = plc["id"]
            color = id_color[pid]
            x0, y0 = plc["x_cm"], plc["y_cm"]
            verts = plc["normalized_vertices_cm"]
            shifted = [(x + x0, y + y0) for x, y in verts]

            # bounding box
            w = max(x for x, _ in verts)
            h = max(y for _, y in verts)
            ax.add_patch(patches.Rectangle(
                (x0, y0), w, h,
                facecolor=color, alpha=0.3, edgecolor=color
            ))

            # garment polygon
            ax.add_patch(patches.Polygon(
                shifted,
                facecolor=color, alpha=0.6, edgecolor=color
            ))
            # show placement order
            if bool(config.get("show_placement_order")):
                ax.text(x0 + w / 2, y0 + h / 2, str(plc["placement_order"]),
                        ha="center", va="center", fontsize=8, color="black")

            if pid not in seen:
                handles.append(patches.Patch(facecolor=color, edgecolor=color))
                labels.append(pid)
                seen.add(pid)

        # legend outside
        ax.legend(handles, labels,
                  bbox_to_anchor=(1.02, 1),
                  loc="upper left",
                  fontsize="small")

    plt.tight_layout()
    plt.show()


def print_summary_table(results: List[Dict[str, Any]]) -> None:
    rows = []
    for r in results:
        area_m2 = (r["fabric_width_cm"] / 100) * (r["fabric_length_cm"] / 100)
        used = r["placed_area_cm2"] / 10000
        waste = r["waste_area_cm2"] / 10000
        util = used / area_m2 * 100
        rows.append([
            r["version"],
            f"{r['placed_count']}/{r['total_count']}",
            f"{area_m2:.2f} m²",
            f"{used:.3f} m²",
            f"{waste:.3f} m²",
            f"{util:.1f}%",
        ])

    print("\n" + tabulate(
        rows,
        headers=["Algorithm", "Placed", "Fabric Area", "Used Area", "Waste", "Utilization"],
        tablefmt="fancy_grid",
    ))
