import json
import numpy as np
from datetime import datetime
from modules import file_io
from modules.flow_field import FlowField
from modules import visualize


class Query:
    _instance = None

    save_results = True

    def __new__(cls, *args, **kwargs):
        if not isinstance(cls._instance, cls):
            cls._instance = super(Query, cls).__new__(cls)
        return cls._instance

    def __init__(self, field: FlowField):
        self.field = field

    def handle_request(self, request: str, format="string"):
        if format == "file":
            request = file_io.read("queries", request, format="json")
        else:
            try:
                request: dict = json.loads(request)
            except Exception as e:
                return f"Invalid query request string: {e}"

        mode: str = request.get("mode", None)
        params: dict = request.get("params", None)
        if not isinstance(params, dict):
            return "Invalid request parameters"

        if mode == "meshgrid":
            low_bounds = params.get("low_bounds", None)
            high_bounds = params.get("high_bounds", None)

            keys = ["low_bounds", "high_bounds", "step_size", "chunk_size", "t"]
            args = {key: params[key] for key in keys if key in params}

            try:
                vel = self.field.sum_vel_mesh(
                    **args,
                )
            except Exception as e:
                return f"Error calculating velocity in meshgrid: {e}"

            if isinstance(vel, np.ndarray) and self.save_results:
                try:
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{self.field.name}_meshgrid_{current_time}"
                    file_io.write("results", filename, vel, format="npy")
                except Exception as e:
                    return f"Error saving result: {e}"

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
                    return f"Error plotting meshgrid: {e}"
                return fig
            else:
                return "Meshgrid velocity calculation complete"

        if request.get("mode") == "points":
            coords: list = params.get("coords", None)
            if coords is None:
                coords = [[0, 0, 0]]
            if not isinstance(coords, list) or len(coords) == 0:
                return "Invalid request parameters, coords must be a list of 3D points"

            velocities = np.zeros((len(coords), 3))
            try:
                for i, coord in enumerate(coords):
                    velocities[i] = self.field.sum_vel_mesh(
                        low_bounds=coord, high_bounds=coord, t=params.get("t", 0)
                    )
            except Exception as e:
                return f"Error calculating velocity at points: {e}"
            if isinstance(velocities, np.ndarray):
                try:
                    current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{self.field.name}_points_{current_time}"
                    file_io.write("results", filename, velocities, format="npy")
                except Exception as e:
                    return f"Error saving result: {e}"
            return "Points velocity calculation complete"
        return "Invalid request mode"
