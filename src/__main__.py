from argparse import ArgumentParser
from tkinter import filedialog
from rich.panel import Panel
from rich import print

from .map_parser import load_map, LexingError, ParsingError, ValidationError
from .simulation import Simulation
from .visualizer import Converter, Visualizer


def print_error(message: str) -> None:
    """Display an error message and exit the application.

    Args:
        message: Error message to display.
    """
    panel = Panel(
        message,
        title="Error:",
        title_align="left",
        border_style="red",
    )
    print(panel)
    exit(1)


def main() -> None:
    """Main function"""
    parser = ArgumentParser(
        prog="Fly-in",
        description="Drone routing system simulator",
        epilog="This project has been created as part of the 42 curriculum by "
        "smakkass",
    )
    parser.add_argument(
        "--map",
        "-m",
        help="Path to map file",
    )
    args = parser.parse_args()
    map_file = args.map or filedialog.askopenfilename(initialdir="maps/")
    if not map_file:
        print_error("Please Chose a Map File")

    try:
        world = load_map(map_file)
    except (LexingError, ParsingError, ValidationError, ValueError) as e:
        print_error(f"{e}")
    simulation = Simulation(world)
    try:
        turns = simulation.run()
    except ValueError as e:
        print_error(f"{e}")
    for turn, steps in turns.items():
        if turn:
            for drone, spot in steps.items():
                print(f"D{drone}-{spot}", end=" ")
            print()
    graph = Converter.convert_graph(world)
    converted_turns = Converter.convert_turns(turns)
    visualizer = Visualizer(graph, world.nb_drones, converted_turns)
    visualizer.run()


if __name__ == "__main__":
    main()
