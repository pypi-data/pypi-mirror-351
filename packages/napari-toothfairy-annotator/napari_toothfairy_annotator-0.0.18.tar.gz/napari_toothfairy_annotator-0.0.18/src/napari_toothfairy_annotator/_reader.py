import os
import numpy as np


def napari_get_reader(path):
    print(path)
    if isinstance(path, str) and os.path.isdir(path):
        return reader_function
    return None


def reader_function(path):
    annotation_path = os.path.join(path, 'annotation.npy')
    volume_path = os.path.join(path, 'volume.npy')

    annotation = np.load(annotation_path)
    volume = np.load(volume_path)
    metadata = {'parent_folder': path}

    return [
        (
            volume, 
            {
                'name': 'volume',
                'metadata': metadata,
            },
            'image'
        ), (
            annotation,
            {
                'name': 'annotation',
                'metadata': metadata
            },
            'labels'
        )
    ]
