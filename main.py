import trimesh
import pyrender
import numpy as np
import copy

def load_mesh(file_path):
    """
    Loads a 3D mesh from a file and ensures it's a single Trimesh object.
    Handles Scene objects and unit conversion automatically.
    """
    try:
        mesh = trimesh.load(file_path, force='mesh')
        
        if isinstance(mesh, trimesh.Scene):
            mesh = trimesh.util.concatenate(
                [g for g in mesh.geometry.values() if isinstance(g, trimesh.Trimesh)]
            )
        
        if not isinstance(mesh, trimesh.Trimesh):
            if hasattr(mesh, 'geometry') and len(mesh.geometry) > 0:
                mesh = next(iter(mesh.geometry.values()))
        
        if not isinstance(mesh, trimesh.Trimesh):
            print(f"Error: Could not extract Trimesh from {file_path}")
            return None
            
        if np.median(mesh.extents) > 10:
            mesh.apply_scale(0.001)  
            
        return mesh
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None

def visualize_meshes(meshes, colors=None, title="Mesh Visualization"):
    """Visualizes meshes with optional colors and title."""
    if not isinstance(meshes, list):
        meshes = [meshes]
    scene = pyrender.Scene()
    for i, mesh in enumerate([m for m in meshes if m is not None]):
        scene.add(pyrender.Mesh.from_trimesh(mesh))

    pyrender.Viewer(scene, use_raymond_lighting=True)
    

def align_meshes_icp(target_mesh, source_mesh, max_iterations=100, threshold=0.01):
    """
    Aligns source mesh to target mesh using ICP.
    """
    if target_mesh is None or source_mesh is None:
        return None

    source_copy = copy.deepcopy(source_mesh)
    
    target_points = target_mesh.sample(5000)
    source_points = source_copy.sample(5000)

    try:
        result = trimesh.registration.icp(
            source_points,
            target_points,
            initial=np.eye(4),
            max_iterations=max_iterations,
            threshold=threshold,
            scale=False
        )
        
        transform = result[0] if isinstance(result, tuple) else result
        
        source_copy.apply_transform(transform)
        return source_copy
        
    except Exception as e:
        print(f"ICP Error: {e}")
        return None

def scale_mesh(mesh, scale_factors):
    """Scales mesh by given factors along x,y,z axes."""
    if mesh is None or not isinstance(scale_factors, (list, np.ndarray)) or len(scale_factors) != 3:
        return None
    
    scale_matrix = np.eye(4)
    scale_matrix[:3,:3] = np.diag(scale_factors)
    mesh.apply_transform(scale_matrix)
    return mesh

def translate_mesh(mesh, translation):
    """Translates mesh by given vector."""
    if mesh is None or not isinstance(translation, (list, np.ndarray)) or len(translation) != 3:
        return None
    
    transform = np.eye(4)
    transform[:3,3] = translation
    mesh.apply_transform(transform)
    return mesh

def fit_t_shirt(body_mesh, shirt_mesh,gender):
    """
    Main fitting pipeline:
    1. Scale shirt roughly to body size
    2. Position shirt over body
    3. Refine with ICP
    4. Adjust for collisions
    """
    if body_mesh is None or shirt_mesh is None:
        return None, None

    body_size = body_mesh.extents
    shirt_size = shirt_mesh.extents
    
    if gender=='female':
        scale_factors = body_size / shirt_size * np.array([0.71, 0.41, 1.42])
    else:
        scale_factors = body_size / shirt_size * np.array([0.79, 0.43, 1.25])

    scaled_shirt = scale_mesh(copy.deepcopy(shirt_mesh), scale_factors)
    
    translation = body_mesh.centroid - scaled_shirt.centroid
    translation[1] += body_size[1] * 0.1  # Adjust vertical position
    positioned_shirt = translate_mesh(scaled_shirt, translation)
    
    aligned_shirt = align_meshes_icp(body_mesh, positioned_shirt)
    if aligned_shirt is None:
        print("Using initial alignment (ICP failed)")
        aligned_shirt = positioned_shirt
    if gender=='female':
        final_shirt = scale_mesh(aligned_shirt, [.9, 1.04, 1.2])
    else:
        final_shirt = scale_mesh(aligned_shirt, [1, 1.04, 1.3])
    
    return final_shirt, body_mesh

def main():
    print("Starting virtual try-on")
    
    # Load meshes
    female_mesh = load_mesh('female_body.glb')
    male_mesh=load_mesh('male_body-2.glb')
    shirt = load_mesh('normal_t-shirt_animated.glb')
    
    if female_mesh is None or male_mesh is None or shirt is None:
        print("Failed to load required meshes")
        return
    meshes=[female_mesh,male_mesh]
    gender=['female', 'male']
    print("Fitting t-shirt.")
    for indx,i in enumerate(meshes):
        fitted_shirt, body = fit_t_shirt(i, shirt,gender[indx])
        if fitted_shirt is None:
            print("Fitting failed")
            return
    
        visualize_meshes([body, fitted_shirt],
                    colors=[[255, 218, 185], [100, 150, 255, 150]],
                    title="Fitting Result")
    
    print("Done")

if __name__ == "__main__":
    main()