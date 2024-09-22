import matplotlib.pyplot as plt
import numpy as np
import numpy.typing as npt

def plot_clusters(
    X: npt.NDArray[np.float_],
    labels: npt.NDArray[np.int_]
) -> None:
    """
    Plots simulated points, grouping points into clusters or noise based on
    the labels passed to the function.
    
    Args:
        X:
            Array of float coordinates containing all points, both noise and
            clustered. The array will have shape (N, d), where N is the number of
            total points and d is the dimensionality of the data.
        labels:
            Array of integer labels assigning points to clusters or noise of shape
            (N,), where N is the total number of points.

    Returns:
        None.
    """

    clusterIDSplit = np.where(np.diff(labels))[0] 
    clustergroups = np.split(X, clusterIDSplit + 1)
    
    if X.shape[-1] == 2:
        lens = []
        for i in range(len(clustergroups) - 1):
            lens.append(len(clustergroups[i]))
            plt.scatter(*clustergroups[i].T, s=0.1)
        plt.scatter(*clustergroups[-1].T, color='k', s=0.1, alpha=0.5)
        

    elif X.shape[-1] == 3:
        fig = plt.figure()
        ax = plt.axes(projection="3d")
        for i in range(len(clustergroups) - 1):
            ax.scatter3D(
                clustergroups[i][:,0], clustergroups[i][:,1], clustergroups[i][:,2],
                s=0.1
            )
        ax.scatter3D(
            clustergroups[-1][:,0], clustergroups[-1][:,1], clustergroups[-1][:,2],
            color='k', s=0.1, alpha=0.5
        )
        
    plt.gca().set_aspect('equal')
    plt.title('Simulated Clusters')
    plt.show