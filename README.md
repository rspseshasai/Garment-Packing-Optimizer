# Garment-Packing-Optimizer
Six Atomic Case Study - Efficient 2D garment packing algorithms implemented in Python using bounding-box and polygon-aware heuristics. Includes First-Fit, Shelf-Fit, and MaxRects strategies with visualizations and performance summaries.

This project implements efficient 2D packing algorithms for arranging irregular garment pieces onto fixed-width fabric with minimal material waste. It is designed as a modular and extensible system suitable for automated clothing production pipelines and optimization research.

## ✨ Features

- **First-Fit Row-Wise Packing**: Places pieces in horizontal rows with margin spacing.
- **Shelf-Fit Packing**: Stacks rows (shelves) based on piece height, optimizing horizontal usage.
- **MaxRects Packing (Best Short Side Fit)**: Uses `rectpack` for offline bin packing with optional rotation.
- **Geometry-Aware Placement**: Normalized vertices for each piece are preserved and rendered.
- **Fabric Utilization Reports**: Outputs detailed statistics on used area, waste, and placement count.
- **Matplotlib Visualization**: Clear side-by-side layout renderings for algorithm comparison.

## 📊 Input Format Example

```json
{
  "fabric_width_cm": 150,
  "fabric_length_cm": 500,
  "fabric_margin_cm": 1,
  "pieces": [
    {
      "id": "sleeve_A",
      "vertices_cm": [[0, 0], [0, 25], [15, 25], [15, 0]]
    },
    {
      "id": "front_B",
      "vertices_cm": [[0, 0], [0, 40], [20, 40], [20, 0]]
    }
  ]
}
```

## 📈 Output Metrics

Each algorithm provides:

* Number of pieces placed
* Area used vs. total available
* Waste area in cm²
* Utilization efficiency in %

## 📌 Use Case

This code was developed as part of a technical interview case study to demonstrate algorithmic thinking, software modularity, and optimization problem-solving in the fashion automation domain.
