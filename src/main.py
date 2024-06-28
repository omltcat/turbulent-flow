import sys
import argparse
import matplotlib.pyplot as plt
from modules.eddy_profile import EddyProfile
from modules.flow_field import FlowField
from modules.query import Query
from modules import shape_function


def main(args=None):
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Turbulent Flow Synthetic Eddy Generator"
    )

    subparsers = parser.add_subparsers(dest="command")

    # New field subparser
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
        default=0,
        metavar="Vx",
        type=float,
        help="Average flow velocity in x direction (default: 0)",
    )

    # Query field subparser
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

    # Parse arguments
    args = parser.parse_args(args)

    if hasattr(args, 'n'):
        args.n = args.n.replace(".json", "")
    if hasattr(args, 'q'):
        args.q = args.q.replace(".json", "")

    # Create new field
    if args.command == "new":
        try:
            profile = EddyProfile(args.p)
            field = FlowField(
                profile=profile, name=args.n, dimensions=args.d, avg_vel=args.v
            )
            field.save()
            print(f"New field '{args.n}' created and saved successfully")
        except Exception as e:
            print(f"Error creating new field: {e}", file=sys.stderr)
            return

    # Query exiting field
    if args.command == "query":
        try:
            field = FlowField.load(args.n)
            query = Query(field)
        except Exception as e:
            print(f"Error loading field '{args.n}': {e}", file=sys.stderr)
            return

        try:
            if args.s is not None:
                shape_function.set_active(args.s)
            if args.c is not None:
                shape_function.set_cutoff(args.c)
        except Exception as e:
            print(f"Error setting shape function: {e}", file=sys.stderr)
            return

        try:
            response = query.handle_request(request=args.q, format="file")
            print(response)
            if "Plot saved" in response and __name__ == "__main__":
                plt.show()
        except Exception as e:
            print(f"Error handling query: {e}", file=sys.stderr)
            return


if __name__ == "__main__":
    main()
