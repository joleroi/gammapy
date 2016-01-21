import numpy as np
import matplotlib.pyplot as plt
from gammapy.data import DataStore
from gammapy.datasets import gammapy_extra
from gammapy.background import EnergyOffsetArray


def make_counts_array():
    """Make an example counts array with energy and offset axes."""
    data_store = DataStore.from_dir(gammapy_extra.dir / 'datasets/hess-crab4')

    event_lists = []
    for obs_id in data_store.obs_table['OBS_ID']:
        event_list = data_store.load(obs_id, 'events')
        event_lists.append(event_list)

    energy = np.logspace(-1, 2, 100)
    offset = np.linspace(0, 2.5, 100)
    array = EnergyOffsetArray(energy, offset)
    array.fill_events(event_lists)

    return array


if __name__ == '__main__':
    array = make_counts_array()
    array.plot_image()
    plt.show()
