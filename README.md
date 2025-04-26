# Virtual-Try-On-Integration-for-3D-Body-Mesh
Implementing a prototype virtual try-on system that fits a t-shirt on 3-D body mesh.
A Python-based prototype system for fitting 3D clothing onto 3D body meshes, designed to extend an existing 3D body mesh pipeline.

## Features

- Loads and processes 3D body meshes and clothing assets
- Implements mesh alignment using Iterative Closest Point (ICP) algorithm
- Provides gender-specific fitting adjustments
- Visualizes the final fitted result
- Supports common 3D mesh formats (.obj, .glb)

## Requirements

- Python 3.7+
- Required packages:
  - trimesh
  - pyrender
  - numpy

## Implementation Details
Approach
The fitting process follows these steps:

Initial Scaling: The t-shirt is roughly scaled to match the body dimensions

Positioning: The scaled t-shirt is positioned over the body mesh

ICP Refinement: Iterative Closest Point algorithm aligns the t-shirt to the body

Final Adjustments: Gender-specific scaling adjustments are applied
## Key Functions
load_mesh(): Handles mesh loading and preprocessing

align_meshes_icp(): Implements ICP-based alignment

fit_t_shirt(): Main fitting pipeline with gender-specific parameters

visualize_meshes(): Displays the final result
