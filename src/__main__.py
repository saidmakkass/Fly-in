from argparse import ArgumentParser

from .map_parser import load_map, LexingError, ParsingError, ValidationError
from .simulation import Simulation
from .visualizer import Converter, Visualizer


def main():
    parser = ArgumentParser(
        prog="Fly-in",
        usage="uv run python -m src <map_file>",
        description="Drone routing system simulator",
        epilog="This project has been created as part of the 42 curriculum by "
        "smakkass",
    )
    parser.add_argument(
        "map_file",
        help="Path to map file",
        metavar="<map_file>",
    )
    args = parser.parse_args()
    map_file = args.map_file

    try:
        world = load_map(map_file)
    except (LexingError, ParsingError, ValidationError, ValueError) as e:
        print(e)
        exit(1)
    simulation = Simulation(world)
    try:
        turns = simulation.run()
    except ValueError as e:
        print(e)
        exit(1)
    for turn, steps in turns.items():
        if turn:
            for drone, spot in steps.items():
                print(f"D{drone}-{spot}", end=" ")
            print()
    graph = Converter.convert_graph(world)
    visualizer = Visualizer(graph)
    visualizer.run()



if __name__ == "__main__":
    main()