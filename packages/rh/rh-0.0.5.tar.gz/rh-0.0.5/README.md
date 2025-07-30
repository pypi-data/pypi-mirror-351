# rh
Supervised clustering

To install:	```pip install rh```

## Overview
The `rh` package provides tools for supervised clustering, integrating label information into the clustering process. This is particularly useful when you have labeled data and you want to ensure that the clusters are formed considering these labels. The package includes classes and functions that extend the functionality of scikit-learn's clustering algorithms, allowing for more nuanced clustering strategies that can be tailored based on the characteristics of the data and the labels.

## Main Features
- **SupervisedKMeans**: A class that performs K-Means clustering in a supervised manner, where the number of clusters per class can vary based on the distribution of data points among the classes.
- **SeperateClassKMeans**: A class that fits a separate KMeans clustering to each class found in the dataset, with options to adjust the number of clusters per class based on different strategies such as volume (number of points) or inertia (within-cluster sum of squares).
- **Utility Functions**: Functions like `_choose_class_weights` and `_choose_distribution_according_to_weights` help in determining the number of clusters for each class based on specified criteria.

## Installation
You can install the `rh` package using pip:
```bash
pip install rh
```

## Usage Examples

### SupervisedKMeans
```python
from rh import SupervisedKMeans
import numpy as np

# Example data
X = np.array([[1, 2], [1, 4], [1, 0],
              [10, 2], [10, 4], [10, 0]])
y = np.array([0, 0, 0, 1, 1, 1])

# Initialize and fit the model
model = SupervisedKMeans(n_clusters=2)
model.fit(X, y)

# Predict new data
print(model.predict(np.array([[1, 1], [10, 3]])))
```

### SeperateClassKMeans
```python
from rh import SeperateClassKMeans
import numpy as np

# Example data
X = np.array([[1, 2], [1, 4], [1, 0],
              [10, 2], [10, 4], [10, 0]])
y = np.array([0, 0, 0, 1, 1, 1])

# Initialize and fit the model
model = SeperateClassKMeans(n_clusters=2, method='volume')
model.fit(X, y)

# Access cluster centers
print(model.cluster_centers_)
```

## Documentation

### Classes
- **SupervisedKMeans**: Clusters data by first fitting a KMeans model to the most frequent classes until the number of clusters is exhausted. It then assigns new data points to these clusters or to the nearest cluster if the class was not seen during training.
- **SeperateClassKMeans**: Fits a separate KMeans model to each class in the dataset. The number of clusters for each class can be specified or automatically determined based on the method chosen (`volume` or `inertia`).

### Functions
- **y_idx_dict(y)**: Creates a dictionary mapping each unique label in `y` to the indices of samples with that label.
- **kmeans_per_y_dict(X, y, y_idx=None)**: Fits a KMeans model to the data points in `X` corresponding to each unique label in `y`.
- **_choose_class_weights(X, y, n_clusters, method, clusterer)**: Determines the number of clusters for each class based on the specified method.
- **_choose_distribution_according_to_weights(weights, total_int_to_distribute)**: Distributes a total integer amount proportionally across items based on their weights.

## Contributing
Contributions to the `rh` package are welcome. Please ensure that any pull requests or issues are relevant to supervised clustering enhancements or bug fixes.