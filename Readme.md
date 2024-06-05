# Project for Computational Fabrication
Project for the course "Computational Fabrication", This project create a voronoi
structure from an input mesh

# Requirements:
- python 3.10.*

Blender seem to require python 3.10 as right now (blender 4.0)

## set-up
```shell
python3.10 -m venv .venv
```

```shell
 source .venv/bin/activate  
```

```shell
pip install -r requirements.txt
```

## Usage
Running with the example:
```shell
python3.10 main.py
```
This will run the example.json file, it can be found inside the "data" folder.
In the folder other than the json there are different stl files
- dino_body.stl, dino_head.stl and dino_neck.stl are the sliced files
- edited_original.stl is the original file with reduced geometry
- out5.stl is the result of the run
- edited_result.stl is a manual edited version I made as test

The program can be used with a custom json file
```shell
python3.10 main.py --source <path to json file> --output <path to stl file>
```
The only requirement is that the structure is preserved following the example, 
any number of sliced meshes can be included.
The parameter "density" is the number of points per blender unit cube, so 
the number should be adapted to the size of the mesh.
The performance is not very good as the blender api is sequential, so I suggest
to start with small numbers.