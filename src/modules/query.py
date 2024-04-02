import json
import numpy as np
from modules import file_io
from modules.flow_field import FlowField
from modules import visualize


class Query:
    _instance = None

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
                return velocities
            except Exception as e:
                return f"Error calculating velocity at points: {e}"
        return "Invalid request mode"
