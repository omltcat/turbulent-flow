import json
import numpy as np
from datetime import datetime
from modules import file_io
from modules.flow_field import FlowField
from modules import visualize
from modules import utils


class Query:
    """
    Singleton class to handle query requests on a flow field.
    Currently only save results to disk in numpy format.
    """
    _instance = None

    save_results = True

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Query, cls).__new__(cls)
        return cls._instance

    def __init__(self, field: FlowField):
        self.field = field

    def handle_request(self, request: str, format="string"):
        """
        Handle query request on flow field.
        Supports two modes: meshgrid and points.
        For points, it currrently uses single point meshgrid calculation.

        Parameters
        ----------
        request : str
            Query request string or file name.
        format : str, optional
            Format of request, by default "string"

        Returns
        -------
        response : str
            Response message.

        """
        # Parse request
        if format == "file":
            request = file_io.read("queries", request, format="json")
        else:
            try:
                request: dict = json.loads(request)
            except Exception as e:
                raise Exception(f"Invalid query request string: {e}")

        mode: str = request.get("mode", "INVALID")
        params: dict = request.get("params", None)
        if not isinstance(params, dict):
            raise TypeError("Invalid request parameters")

        # File name for saving results
        current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{self.field.name}_{mode}_{current_time}"

        # Response message
        response = f"Velocity calculation complete (mode: {mode})."

        # Handle meshgrid request
        if mode == "meshgrid":
            # Extract mesh parameters
            low_bounds = params.get("low_bounds", None)
            high_bounds = params.get("high_bounds", None)

            kwargs = utils.filter_keys(params, ["low_bounds", "high_bounds", "step_size", "chunk_size", "time"])

            # Calculate velocity in meshgrid
            try:
                vel = self.field.sum_vel_mesh(**kwargs)
            except Exception as e:
                raise Exception(f"Error calculating velocity in meshgrid: {e}")

            # Save raw results to disk
            if isinstance(vel, np.ndarray) and self.save_results:
                try:
                    file_io.write("results", filename, vel, format="npy")
                    response += f"\nRaw result saved to results/{filename}.npy"
                except Exception as e:
                    raise Exception(f"Error saving raw result: {e}")

            # Plot meshgrid if requested
            plot: dict = request.get("plot", None)
            if plot is not None:
                try:
                    fig = visualize.plot_mesh(
                        vel,
                        low_bounds,
                        high_bounds,
                        **plot,
                    )
                except Exception as e:
                    raise Exception(f"Error plotting meshgrid: {e}")

                # Save plot to disk
                try:
                    file_io.write("plots", filename, fig, format="png")
                    response += f"\nPlot saved to plots/{filename}.png"
                except Exception as e:
                    raise Exception(f"Error saving plot: {e}")
            return response

        # Handle points request
        elif mode == "points":
            # Extract points coordinates
            coords: list = params.get("coords", None)
            if coords is None:
                coords = [[0, 0, 0]]
            if not isinstance(coords, list) or len(coords) == 0:
                raise TypeError("Invalid request parameters, coords must be a list of 3D points")

            # Calculate velocity at each point
            velocities = np.zeros((len(coords), 3))
            try:
                for i, coord in enumerate(coords):
                    velocities[i] = self.field.sum_vel_mesh(
                        low_bounds=coord, high_bounds=coord, time=params.get("time", 0)
                    )
            except Exception as e:
                raise Exception(f"Error calculating velocity at points: {e}")

            # Save results to disk
            if isinstance(velocities, np.ndarray):
                try:
                    file_io.write("results", filename, velocities, format="npy")
                    response += f"\nRaw result saved to results/{filename}.npy"
                except Exception as e:
                    raise Exception(f"Error saving result: {e}")
            return response

        # No valid mode found
        else:
            raise Exception("Invalid request mode")
