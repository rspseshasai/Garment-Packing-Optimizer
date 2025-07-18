import json
import random
import math

def generate_random_polygon(w: float, h: float, num_vertices: int) -> list:
    """Generate a simple polygon with given bounding box dimensions."""
    angles = sorted([random.uniform(0, 2 * math.pi) for _ in range(num_vertices)])
    radius_w = w / 2
    radius_h = h / 2
    cx, cy = radius_w, radius_h
    points = []
    for angle in angles:
        rx = cx + radius_w * math.cos(angle) * random.uniform(0.5, 1.0)
        ry = cy + radius_h * math.sin(angle) * random.uniform(0.5, 1.0)
        points.append([rx, ry])

    # Normalize to (0,0)
    min_x = min(x for x, y in points)
    min_y = min(y for x, y in points)
    return [[round(x - min_x, 2), round(y - min_y, 2)] for x, y in points]

def generate_big_polygon_input(
    filename: str = "../../input/big_polygon_input_400.json",
    num_pieces: int = 400,
    fabric_width: int = 500,
    fabric_length: int = 700,
    margin: int = 0
):
    data = {
        "fabric_length_cm": fabric_length,
        "fabric_width_cm": fabric_width,
        "fabric_margin_cm": margin,
        "pieces": []
    }

    for i in range(1, num_pieces + 1):
        w = random.uniform(5, 50)
        h = random.uniform(5, 100)
        num_vertices = random.randint(3, 6)
        polygon = generate_random_polygon(w, h, num_vertices)
        piece = {
            "id": f"piece_{i:04d}",
            "vertices_cm": polygon
        }
        data["pieces"].append(piece)

    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"✅ Wrote {num_pieces} random polygons to {filename}")

if __name__ == "__main__":
    generate_big_polygon_input()
