import os
import glob
import pytest
import numpy as np
import matplotlib.pyplot as plt
from main import main


@pytest.fixture(scope="module", autouse=True)
def setup():
    global latest_file
    path = "src/results/uvw_test_2_meshgrid_*.npy"
    latest_file = max(glob.glob(path), key=os.path.getmtime)


@pytest.mark.validation
@pytest.mark.skip
def test_stress():
    # main(["new", "-p", "example", "-n", "uvw_test", "-d", "10", "10", "10"])
    main(["query", "-n", "uvw_test", "-q", ".real"])

    path = "src/results/uvw_test_2_meshgrid_*.npy"
    global latest_file
    latest_file = max(glob.glob(path), key=os.path.getmtime)

    vel = np.load(latest_file)
    vel[..., :] *= vel[..., :]
    uu = vel[..., 0]
    vv = vel[..., 1]
    ww = vel[..., 2]

    print('Stress components:')
    print("uu:", np.sum(uu) / np.prod(uu.shape))
    print("vv:", np.sum(vv) / np.prod(vv.shape))
    print("ww:", np.sum(ww) / np.prod(ww.shape))


@pytest.mark.validation
@pytest.mark.skip
def test_divergence():
    vel = np.load(latest_file)
    x_sum = np.sum(vel[..., 0]) / np.prod(vel.shape[:3])
    y_sum = np.sum(vel[..., 1]) / np.prod(vel.shape[:3])
    z_sum = np.sum(vel[..., 2]) / np.prod(vel.shape[:3])

    print('Velocity sums:', x_sum, y_sum, z_sum)

    dx: np.ndarray = np.gradient(vel[..., 0], axis=0)
    dy: np.ndarray = np.gradient(vel[..., 1], axis=1)
    dz: np.ndarray = np.gradient(vel[..., 2], axis=2)
    div = dx + dy + dz

    abs_div = np.abs(div)
    print("Max divergence:", np.max(abs_div))

    # Find the index of the maximum divergence along the Z-axis
    z_index = np.argmax(np.max(abs_div, axis=(0, 1)))

    # Select the XY plane slice at this index
    slice = div[z_index, :, :]

    # Plot the 2D slice
    plt.imshow(slice, cmap='viridis')
    plt.colorbar(label='Divergence')
    plt.title(f'XY slice at z = {z_index} where highest divergence occurs')
    plt.show()
