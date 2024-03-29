# -*- coding: utf-8 -*-
"""cifar10.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1uULo0iVPYGJxClnH-J2O4UBT40JY4Y92

# The CIFAR-10 dataset

This document is a summerized version of https://www.cs.toronto.edu/~kriz/cifar.html.

The CIFAR-10 dataset consists of 60000 32x32 colour images in 10 classes, with 6000 images per class. There are 50000 training images and 10000 test images. 

The dataset is divided into five training batches and one test batch, each with 10,000 images. The test batch contains exactly 1,000 randomly-selected images from each class. The training batches contain the remaining images in random order, but some training batches may contain more images from one class than another. Between them, the training batches contain exactly 5000 images from each class. 

## Download

The URL of the python version is https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz

## Dataset layout

The archive contains the files `data_batch_1`, `data_batch_2`, ..., `data_batch_5`, as well as `test_batch`. Each of these files is a Python "pickled" object. Here is a routine which will open such a file and return a dictionary:
"""

def unpickle(file):
  import pickle
  with open(file, 'rb') as fo:
    dict = pickle.load(fo, encoding='bytes')
  return dict

"""Loaded in this way, each of the batch files contains a dictionary with the following elements:


* **data** - a 10,000 x 3,072 numpy array of `uint8s`. Each row of the array stores a 32 x 32 colour image. The first 1,024 entries contain the red channel values, the next 1,024 the green, and the final 1,024 the blue. The image is stored in row-major order, so that the first 32 entries of the array are the red channel values of the first row of the image.

* **labels** - a list of 10,000 numbers in the range 0-9. The number at index `i` indicates the label of the `i`th image in the array **data**.


The dataset contains another file, called `batches.meta`. It too contains a Python dictionary object. It has the following entries:
* **label_names** - a 10-element list which gives meaningful names to the numeric labels in the labels array described above. For example, `label_names[0] == "airplane"`, `label_names[1] == "automobile"`, etc.
"""

# Load CIFAR-10 with Numpy
# https://mattpetersen.github.io/load-cifar10-with-numpy

import tarfile
import os
from urllib.request import urlretrieve
import numpy as np

def cifar10(path=None):
    """Return (train_images, train_labels, test_images, test_labels).
  
    Args:
        path (str): Directory containing CIFAR-10. 
        Default is '/content/cv-dataset/cifar10'.
        Create if nonexistant. Download CIFAR-10 if missing.
      
    Returns:
        Tuple of (train_images, train_labels, test_images, test_labels), each
        a matrix. Rows are examples. Columns of images are pixel values,
        with the order (red -> blue -> green). Columns of labels are a onehot
        encoding of the correct class.
    """
    url = 'https://www.cs.toronto.edu/~kriz/'
    tar = 'cifar-10-binary.tar.gz'
    files = ['cifar-10-batches-bin/data_batch_1.bin',
            'cifar-10-batches-bin/data_batch_2.bin',
            'cifar-10-batches-bin/data_batch_3.bin',
            'cifar-10-batches-bin/data_batch_4.bin',
            'cifar-10-batches-bin/data_batch_5.bin',
            'cifar-10-batches-bin/test_batch.bin' ]
    label_file = 'cifar-10-batches-bin/batches.meta.txt' # added by skjung
  
    if path is None:
        # Set path to /content/data/cifar10
        # path = os.path.join(os.path.expanduser('~'), 'cv-dataset', 'cifar10')
        path = '/content/cv-dataset/cifar10'
    
    # Create path if it doesn't exist
    os.makedirs(path, exist_ok=True)
  
    # Download tarfile if missing
    if tar not in os.listdir(path):
        urlretrieve(''.join((url, tar)), os.path.join(path, tar))
        print('Downloaded %s to %s' % (tar, path))
    
    # Load data from tarfile
    with tarfile.open(os.path.join(path, tar)) as tar_object:
        # Extract the label_names, added by skjung
        f = tar_object.extractfile(label_file)
        label_names = f.read().decode('ascii').split('\n')
        f.close()
        label_names = label_names[0:10]
        
        # Each file contains 10,000 color images and 10,000 labels
        fsize = 10000 * (32 * 32 * 3) + 10000
      
        # There are 6 files (5 train and 1 test)
        buffr = np.zeros(fsize * 6, dtype='uint8')

        # Get members of tar corresponding to data files
        # -- The tar contains README's and other extraneous stuff
        members = [file for file in tar_object if file.name in files]
        
        # Sort those members by name
        # -- Ensures we load train data in the proper order
        # -- Ensures that test data is the last file in the list
        members.sort(key=lambda member: member.name)

        # Extract data from members
        for i, member in enumerate(members):
            # Get member as a file object
            f = tar_object.extractfile(member)
            # Read bytes from that file object into buffr
            buffr[i * fsize:(i + 1) * fsize] = np.frombuffer(f.read(), 'B')

        # Parse data from buffer
        # -- Examples are in chunks of 3,073 bytes
        # -- First byte of each chunk is the label
        # -- Next 32 * 32 * 3 = 3,072 bytes are its corresponding image

        # Labels are the first byte of every chunk
        labels = buffr[::3073]

        # Pixels are everything remaining after we delete the labels
        pixels = np.delete(buffr, np.arange(0, buffr.size, 3073))
        images = pixels.reshape(-1, 3072).astype('float32') / 255

        # Split into train and test
        train_images, test_images = images[:50000], images[50000:]
        train_labels, test_labels = labels[:50000], labels[50000:]

        """ removed by skjung
        def _onehot(integer_labels):
            # Return matrix whose rows are onehot encodings of integers.
            n_rows = len(integer_labels)
            n_cols = integer_labels.max() + 1
            onehot = np.zeros((n_rows, n_cols), dtype='uint8')
            onehot[np.arange(n_rows), integer_labels] = 1
            return onehot
        """
        
        return train_images, train_labels, \
                test_images, test_labels, label_names
        # changed by skjung
        # return train_images, _onehot(train_labels), \
        #         test_images, _onehot(test_labels)

import matplotlib.pyplot as plt

def plot_sampleImages(images, labels, label_names, columSize):
    ysize = images.shape[0] // columSize
    fig, axs = plt.subplots(ysize, columSize, figsize=(15, ysize*1.5))
    for i, ax in enumerate(axs.flat):
        image = np.transpose(np.reshape(images[i],(3,32,32)), (1,2,0))
        ax.imshow(image)

        # Show the classes as the label on the x-axis.
        xlabel = label_names[labels[i]]
        ax.set_xlabel(xlabel)        
        
        # Remove ticks from the plot.
        ax.set_xticks([])
        ax.set_yticks([])

# train_images, train_labels, test_images, test_labels, label_names = cifar10()

# plot_sampleImages(train_images[:100,:], train_labels[:100], label_names, 10)

# plot_sampleImages(test_images[:10,:], test_labels[:10], label_names, 10)
