import argparse
from pathlib import Path
from src.script import script_from_json


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description="Process mesh with voronoi")

    parser.add_argument("--source", type=Path, help="path to source file", default="./data/example.json")
    parser.add_argument("--output", type=Path, help="path to output file", default="./data/out_mesh.stl")
    args = parser.parse_args()

    json_source: Path = Path(args.source)

    out_path: Path = Path(args.output).resolve()
    script_from_json(json_path=json_source, out=out_path)




