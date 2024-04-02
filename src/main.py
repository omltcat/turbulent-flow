import argparse
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField
from modules.query import Query
from modules import shape_function


def main(args=None):
    parser = argparse.ArgumentParser(
        description="Turbulent Flow Synthetic Eddy Generator"
    )

    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser(
        "new", help="Create a new field, show help: 'new -h'."
    )
    new_parser.add_argument(
        "-p",
        required=True,
        metavar="PROFILE",
        help="Eddy profile file name in 'profiles' folder",
    )
    new_parser.add_argument(
        "-n", required=True, metavar="NAME", help="Name of the new field"
    )
    new_parser.add_argument(
        "-d",
        required=True,
        metavar=("Lx", "Ly", "Lx"),
        nargs=3,
        type=float,
        help="Dimensions of the new field, separated by spaces",
    )
    new_parser.add_argument(
        "-v",
        default=0.0,
        metavar="Vx",
        type=float,
        help="Average flow velocity in x direction (default: 0.0)",
    )

    query_parser = subparsers.add_parser(
        "query", help="Query velocities on an existing field, show help: 'query -h'."
    )

    query_parser.add_argument(
        "-n", required=True, metavar="NAME", help="Name of the existing field"
    )

    query_parser.add_argument(
        "-q",
        required=True,
        metavar="QUERY",
        help="Query points file as defined in 'queries' folder",
    )

    query_parser.add_argument(
        "-s", metavar="SHAPE", help="Shape function to be used (default: gaussian)"
    )

    query_parser.add_argument(
        "-c",
        metavar="CUTOFF",
        type=float,
        help="Cutoff value in shape function, mutiples of length-scale (default: 2.0)",
    )

    args = parser.parse_args(args)

    if hasattr(args, 'n'):
        args.n = args.n.replace(".json", "")
    if hasattr(args, 'q'):
        args.q = args.q.replace(".json", "")

    if args.command == "new":
        try:
            profile = EddyProfile(args.p)
            field = FlowField(
                profile=profile, name=args.n, dimensions=args.d, avg_vel=args.v
            )
            field.save()
        except Exception as e:
            print(f"Error creating new field: {e}")
        print(f"New field '{args.n}' created and saved successfully")

    if args.command == "query":
        try:
            field = FlowField.load(args.n)
            query = Query(field)
        except Exception as e:
            print(f"Error loading field '{args.n}': {e}")

        try:
            if args.s is not None:
                shape_function.set_active(args.s)
            if args.c is not None:
                shape_function.set_cutoff(args.c)
        except Exception as e:
            print(f"Error setting shape function: {e}")

        try:
            result = query.handle_request(request=args.q, format="file")
            if isinstance(result, str):
                print(result)
            elif isinstance(result, Figure):
                plt.show()
        except Exception as e:
            print(f"Error handling query: {e}")


if __name__ == "__main__":
    main()
