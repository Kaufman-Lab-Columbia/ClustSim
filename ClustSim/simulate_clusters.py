import math
import numpy as np
from sklearn.metrics import pairwise_distances
from collections.abc import Sequence
from typing import List, Tuple, Union, Optional
import numpy.typing as npt


def simulate_clusters(
    num_clusters: int, 
    clustered_pts: Union[int, Tuple[int, int]], 
    cluster_size: Union[int, Tuple[int, int]], 
    noise_pts: int = 0, 
    gradient: bool = False, 
    space: Union[int, Tuple[int, int]] = (0, 1000), 
    cluster_shape: str = 'circle', 
    aspect_ratio: float = 1.0, 
    fix_AR: bool = True, 
    precision_params: Union[Tuple[float, float],
                            Tuple[float, float, float, float]] = (0.0, 0.0), 
    min_sep: Optional[float] = None, 
    length: Union[int, Tuple[int, int]] = 300, 
    D: float = 0.01, 
    rate: int = 10, 
    method: str = 'normal', 
    multi_emitter: Optional[float] = None
) -> Tuple[npt.NDArray[np.float_], npt.NDArray[np.int_]]:
    """
    Simulates clusters of variable type on a simlation grid of specified size.
    
    Args:
        num_clusters (int): 
            The number of clusters to deposit.
        clustered_pts (Union[int, Tuple[int, int]]): 
            The number of points per cluster. If a single integer is passed, all
            clusters will contain the same number of points. If a pair of integers
            (a, b) is passed, the number of points will be variable and this input
            will specify the lower (a) and upper (b) bounds of the possible points
            per cluster. The number of points belonging to each cluster will be
            selected randomly within the input range [a, b - 1].
        cluster_size (Union[int, Tuple[int, int]]):
            The size of each cluster. If a single integer is passed, all clusters
            will be assigned the same size. If a pair of integers (a, b) is passed, 
            cluster sizes will be variable and this input will specify the lower (a)
            and upper (b) bounds of the possible cluster sizes. The size of each
            cluster will be selected randomly within the input range [a, b - 1]. See
            specific cluster deposition functions for the definition of size for
            each cluster type.
        noise_pts (int): 
            The number of unclustered noise points to add to the simulation grid
            after depositing clustered points.
        gradient (bool): 
            Sets the character of the noise. False will result in uniform random
            noise, while True will yield an uneven gradient of noise.
        space (Union[int,Tuple[int, int]): 
            The bounds of the simulation plane. A single value will set the 
            upper bound with a lower bound default of 0. A tuple 
            (lower_bound, upper_bound) will set a custom lower bound. These
            bounds are applied to all dimensions.
        cluster_shape (str): 
            The type of clusters to simulate. This can be set to: "circle",
            "ellipse", "micelle", "fiber", or "sphere".
        aspect_ratio (float): 
            The aspect ratio of elliptical or micellular clusters. This argument is
            ignored for circular and spherical clusters (which are fixed to have
            aspect ratio = 1.0) as well as for fibers, which do not have a
            meaningful concept of an aspect ratio.
        fix_AR (bool):
            Sets either a constant (True) or variable (False) aspect ratio for
            elliptical and micellular clusters. If False, aspect ratios will be
            randomly assigned to each cluster by random uniform selection in the
            range [1.0, aspect_ratio), as specified by the aspect_ratio argument.
        precision_params (Union[Tuple[float, float],
                                Tuple[float, float, float, float]]):
            The mean and standard deviation of the lognormal distribution from which
            localization uncertainties will be drawn, passed as (mean, stdev). For
            3D data, parameters should be specified for both lateral and axial
            precision as (mean_lateral, stdev_lateral, mean_axial, stdev_axial).
        min_sep (Optional[float]):
            The minimum separation between cluster centers. If no input is given,
            the default value is set as follows: for a single cluster_size input
            min_sep = 0.5 * cluster_size, while for a (lower_bound, upper_bound)
            cluster_size input, min_sep = 0.5 * max(cluster_size).
        length (Union[int, Tuple[int, int]]):
            The length of a fibrillar cluster. Fibrillar clusters are deposited
            first by longitudinally growing the fiber backbone to reach the desired
            length, and then growing the fiber laterally around the backbone points
            to reach the desired width. The length grows in integer steps as
            dictated by the rate argument. If the input length is not a multiple of
            rate, it will be rounded down to the the next smallest divisible
            integer. If a single integer is passed, all fibers will be assigned the
            same length. If a pair of integers (a, b) is passed, the length of each
            fiber will be variable and this input will specify the lower (a) and
            upper (b) bounds of the possible lengths. The length of each fiber will
            be selected randomly from within the range [a, b - 1], and then rounded
            down to the next smallest integer divisible by the rate.
        D (float):
            A rotational diffusion constant that describes the evolution of the
            angle that specifies the direction of longitudinal fiber growth. Larger
            values result in rapid rotational diffusion and more fiber curvature,
            while smaller values result in less rotational diffusion and more linear
            fibers.
        rate (int):
            The rate of fiber growth during cluster deposition. A single integer
            value that defines the euclidean distance between points in the fiber
            backbone. The clustered_pts, length, and rate args all set the number of
            points (density) deposited at each backbone point along the fibrillar
            cluster, according to: density = round(pts / (length / rate)). Ensure
            that the rounded integer for density is ≥ 1 to obtain a valid cluster.
        method (str):
            The method for growing fibrillar clusters laterally after setting the
            fiber backbone. Keyword "random" distributes random uniform points
            within a width = cluster_size centered around the backbone point, while
            "normal" draws points from a random normal distribution with
            standard deviation = cluster_size / 4, again centered around the point
            defining the fiber backbone.
        multi_emitter (Optional[float]):
            An optional floating point value that allows the addition of multiple
            localizations per point. After depositing all clustered and noise
            points, multiple localizations are deposited around each initial point
            within a region defined by its localization uncertainty, in order to
            simulate multiple on/off cycles for a given molecule. The input value,
            which should be > 1.0, specifies the mean of a Poisson distribution. The
            number of localizations at each point is randomly drawn from this
            distribution. If no input value is given, there will only be one
            localization per molecule and the original positions of the deposited
            points will not be modified.

    Returns:
        Tuple containing:
            - npt.NDArray[np.float_]: Array of float coordinates with shape (N, d),
              where N is the total number of points (clustered + noise) and d is the
              dimensionality of the data.
            - npt.NDArray[np.int_]: Array of integer labels with shape (N,) mapping to
              cluster assignments. -1 indicates noise, while cluster labels are a set
              of consecutive integers that span the range [0, num_clusters - 1].
    """

    # Create the clusters with the specified parameters

    try:
        length_space = len(space)
        if lenght_space != 2:
            print('Warning: more than two values specified for space parameter.'+
                ' Bounds should be either a single upper bound or (lower bound, upper bound)')
    except TypeError:
        space = (0, space)

    try:
        X_clusts, label_list = deposit_clusters(
            num_clusters, clustered_pts, cluster_size, space, aspect_ratio,
            min_sep, cluster_shape, fix_AR, method, length, D, rate
        )
    except ValueError as e:
        print(f"Error creating clusters: {e}")
        return None, None

    # Add noise points after depositing clusters
    X_noise = add_noise_pts(
        X_clusts, noise_pts, space, cluster_shape, gradient
    )

    # Add noise labels to the labels array
    label_pad = np.pad(
        label_list, (0, len(X_noise)), 'constant', constant_values = -1
    )

    # Combine cluster and noise points into a single array
    X_points = np.vstack((X_clusts, X_noise))
    
    # Apply uncertainty and multi emitter correction to all points
    X_points_final, labels = add_uncertainty(
        X_points, label_pad,  multi_emitter,  *precision_params
    )
    
    return X_points_final, labels

    
def deposit_clusters(
    num_clusters: int,
    clustered_pts: Union[int, Tuple[int, int]],
    cluster_size: Union[int, Tuple[int, int]],
    space: Tuple[int, int],
    aspect_ratio: float,
    min_sep: Optional[float],
    cluster_shape: str,
    fix_AR: bool,
    method: str,
    length: Union[int, Tuple[int, int]],
    D: float,
    rate: int
) -> Tuple[npt.NDArray[np.float_], npt.NDArray[np.int_]]:
    """
    Calls functions which deposit clustered points of a specific type in the
    simlation grid.
    
    Args:
        See simulate_clusters() for a full description of args.

    Returns:
        Tuple containing:
            - npt.NDArray[np.float_]: Array of float coordinates with shape (N, d),
              where N is the number of clustered points and d is the dimensionality of
              the data.
            - npt.NDArray[np.int_]: Array of integer labels of shape (N,) mapping to
              cluster assignments. Labels are a set of consecutive integers that span
              the range [0, num_clusters - 1].
    """

    if min_sep is None:
        min_sep = 0.5 * np.max(cluster_size)

    centers,cond = set_centers(num_clusters, space, min_sep, cluster_shape)

    if cond == True:
        raise ValueError("Distance between clusters is too restrictive")


    pts = clustered_pts
    cluster_width = cluster_size
    X_temp_clusts = []
    label_list = []

    is_clustered_pts_seq = isinstance(clustered_pts, Sequence)
    is_cluster_size_seq = isinstance(cluster_size, Sequence)

    for i in range(num_clusters):
        if is_cluster_size_seq:
            cluster_width = np.random.randint(cluster_size[0], cluster_size[1] + 1, 1)
        if is_clustered_pts_seq:
            pts = np.random.randint(clustered_pts[0], clustered_pts[1] + 1, 1)

        if cluster_shape == 'circle':
            X_temp = deposit_cluster_ellipse(centers[i], cluster_width, 1.0, pts, True)
        elif cluster_shape == 'ellipse':
            X_temp = deposit_cluster_ellipse(
                centers[i], cluster_width, aspect_ratio, pts, fix_AR
            )
        elif cluster_shape == 'micelle':
            X_temp = deposit_cluster_micelle(
                centers[i], cluster_width, aspect_ratio, pts, fix_AR
            )
        elif cluster_shape == 'fiber':
            X_temp = deposit_cluster_fiber(
                centers[i], cluster_width, pts, length, D, rate, method
            )
        elif cluster_shape == 'sphere':
            X_temp = deposit_cluster_sphere(centers[i], cluster_width, pts)
            
        label_list.append(np.full(len(X_temp),i))   
        X_temp_clusts.append(X_temp)
    
    X_clusters = np.vstack(X_temp_clusts)

    return X_clusters, np.hstack(label_list)


def set_centers(
    num_clusters: int,
    space: Tuple[int, int],
    min_sep: float,
    cluster_shape: str
) -> Tuple[npt.NDArray[np.int_], bool]:
    """
    Defines the centers of clusters before depositing clustered points,
    ensuring that clusters are sufficiently spaced apart as specified by a
    minimum separation distance.
    
    Args:
        See simulate_clusters() for a full description of args.

    Returns:
        Tuple containing:
            - npt.NDArray[np.int_]: Array of integer coordinates with shape (N, d),
              where N is the number of clusters and d is the dimensionality of the
              data.
            - bool: Indicates whether to terminate the execution of the simulation if
              cluster centers could not be deposited according to the desired minimum
              separation distance.
    """

    terminate = False
    centers = [None]
    
    if cluster_shape == 'sphere':
        centers[0] = [
            np.random.randint(low=space[0] + 1, high=space[1]),
            np.random.randint(low=space[0] + 1, high=space[1]),
            np.random.randint(low=space[0] + 1, high=space[1])
        ]
        count = 1
        iterations = 0
        while count < num_clusters:
            centers.append([
                np.random.randint(low=space[0] + 1, high=space[1]),
                np.random.randint(low=space[0] + 1, high=space[1]),
                np.random.randint(low=space[0] + 1, high=space[1])
            ])
            dist_c = dist_check(np.array(centers), min_sep)
            if dist_c == True:
                count += 1
                iterations += 1
            else:
                centers.pop()
                iterations += 1
                if iterations > 50000:
                    terminate = True
                    break
    else:
        centers[0] = [
            np.random.randint(low=space[0]+1,high=space[1]),
            np.random.randint(low=space[0]+1,high=space[1])
        ]
        count = 1
        iterations = 0
        while count < num_clusters:
            centers.append([
                np.random.randint(low=space[0]+1,high=space[1]),
                np.random.randint(low=space[0]+1,high=space[1])
            ])
            dist_c = dist_check(np.array(centers), min_sep)
            if dist_c == True:
                count += 1
                iterations += 1
            else:
                centers.pop()
                iterations += 1
                if iterations > 50000:
                    terminate = True
                    break

    return np.array(centers), terminate


def dist_check(
    test_centers: npt.NDArray[np.int_],
    threshold: float
) -> bool:
    """
    Ensures that cluster centers are farther apart than the input value
    threshold (by euclidean distance) for set_centers().
    
    Args:
        test_centers (npt.NDArray[np.int_]):
            Array containing the proposed cluster centers.
        threshold (float):
            The euclidean distance that all cluster centers must be separated by to
            be considered a valid set of placements.

    Returns:
         - bool: Indicates whether the current set of centers meets (True) or fails
           (False) the distance separation criterion.
    """

    p_test = pairwise_distances(test_centers)
    placeholder = []
    for n,i in enumerate(p_test):
        placeholder.append(np.delete(i, n))
        
    placeholder = np.array(placeholder)
    if np.where(placeholder < threshold)[0].size > 0:
        outcome = False
    else:
        outcome = True
    
    return outcome


def deposit_cluster_ellipse(
    center: npt.NDArray[np.int_],
    cluster_size: float,
    aspect_ratio: float,
    pts: int,
    fix_AR: bool
) -> npt.NDArray[np.float_]:
    """
    Deposit a single instance of a circlular or elliptical cluster.
    
    Args:
        center (npt.NDArray[np.int_]):
            The center coordinate of the current cluster.
        cluster_size (float):
            The size of the current cluster. For ellipses and circles, this is the
            apparent width of a normal distribution from which the clustered points
            are drawn, which is defined here as standard deviation * 4.
        aspect_ratio (float):
            See simulate_clusters().
        pts (int):
            The number of points that will be deposited and assigned as belonging to
            this cluster instance.
        fix_AR (bool):
            See simulate_clusters().

    Returns:
        - npt.NDArray[np.float_]: Array of float coordinates of shape (N, d),
          where N is the number of points in this cluster instance and d is the
          dimensionality of the data.
    """

    cluster_sd = cluster_size / 4

    if aspect_ratio < 1.0:
        raise ValueError(
            f"aspect_ratio = {aspect_ratio} is invalid, input values must be ≥ 1.0."
        )
    else:
        if fix_AR == True:
            elongation = cluster_sd * aspect_ratio
        else:
            elongation = np.random.uniform(cluster_sd, cluster_sd * aspect_ratio)

    x_hold = np.random.normal(loc=center[0], scale=cluster_sd, size=int(pts))
    y_hold = np.random.normal(loc=center[1], scale=elongation, size=int(pts))
    theta_rot = np.random.uniform(0, 2 * np.pi)

    x = []
    y = []
    for j in range(len(x_hold)):
        x_hold_rot = (
            ((x_hold[j] - center[0]) * (math.cos(theta_rot)))
            - ((y_hold[j] - center[1]) * (math.sin(theta_rot)))
            + center[0]
        )
        y_hold_rot = (
            ((x_hold[j] - center[0]) * (math.sin(theta_rot)))
            + ((y_hold[j] - center[1]) * (math.cos(theta_rot)))
            + center[1]
        )
        x.append(x_hold_rot)
        y.append(y_hold_rot)
       
    
    return np.vstack((x, y)).T


def deposit_cluster_micelle(
    center: npt.NDArray[np.int_],
    cluster_size: float,
    aspect_ratio: float,
    pts: int,
    fix_AR: bool
) -> npt.NDArray[np.float_]:
    """
    Deposit a single instance of a micelle shaped cluster.
    
    Args:
        center (npt.NDArray[np.int_]):
            The center coordinate of the current cluster.
        cluster_size (float):
            The size of the current cluster. For micelles, the size refers to the
            outer diameter. Clustered points are drawn from a random uniform
            distribution centered around the cluster center, such that the micelle
            inner diameter = outer diameter * 2 / 3.
        aspect_ratio (float):
            See simulate_clusters().
        pts (int):
            The number of points that will be deposited and assigned as belonging to
            this cluster instance.
        fix_AR (bool):
            See simulate_clusters().

    Returns:
        - npt.NDArray[np.float_]: Array of float coordinates of shape (N, d),
          where N is the number of points in this cluster instance and d is the
          dimensionality of the data.
    """

    if aspect_ratio < 1.0:
        raise ValueError(
            f"aspect_ratio = {aspect_ratio} is invalid, input values must be ≥ 1.0."
        )
    else:
        if fix_AR == True:
            elongation = aspect_ratio
        else:
            elongation = np.random.uniform(1, aspect_ratio)
            
    R = cluster_size / 2
    theta_inner = np.random.uniform(0, 2 * np.pi, pts)
    radius = np.random.uniform(R / 1.5, R, pts)
    x_hold = (radius * np.cos(theta_inner) * elongation) + center[0]
    y_hold = (radius * np.sin(theta_inner)) + center[1]
    
    theta_rot = np.random.uniform(0, 2 * np.pi)
    x = []
    y = []
    for j in range(len(x_hold)):
        x_rot = (
            ((x_hold[j] - center[0]) * (math.cos(theta_rot))) 
            - ((y_hold[j] - center[1]) * (math.sin(theta_rot))) 
            + center[0]
        )
        y_rot = (
            ((x_hold[j] - center[0]) * (math.sin(theta_rot)))
            + ((y_hold[j] - center[1]) * (math.cos(theta_rot)))
            + center[1]
        )
        x.append(x_rot)
        y.append(y_rot)
        
    
    return np.vstack((x, y)).T


def deposit_cluster_fiber(
    center: npt.NDArray[np.int_], 
    cluster_size: float, 
    pts: int, 
    length: Union[int, Tuple[int, int]], 
    D: float, 
    rate: int, 
    method: str
) -> npt.NDArray[np.float_]:
    """
    Deposit a single instance of a fiber shaped cluster.
    
    Args:
        center (npt.NDArray[np.int_]):
            The center coordinate for the fiber being deposited. The center
            coordinate marks the midpoint of the fiber along the longitudinal
            direction.
        cluster_size (float):
            The lateral width of the fiber, which is dependent on the method
            argument. For method = "normal", the cluster_size is the the apparent
            width of a random normal distribution centered around a fiber backbone
            point, with standard deviation = cluster_size / 4. For
            method = "random", the cluster_size is the width of a random uniform
            distribution centered around the fiber backbone point.
        pts (int):
            The number of points that will be deposited and assigned as belonging to
            this cluster instance.
        D (float):
            See simulate_clusters().
        rate (int):
            See simulate_clusters().
        method (str):
            See simulate_clusters().

    Returns:
        - npt.NDArray[np.float_]: Array of float coordinates of shape (N, d),
          where N is the number of points in this cluster instance and d is the
          dimensionality of the data.
    """

    if isinstance(length, Sequence):
        length = (
            np.random.randint(length[0] // rate, length[1] // rate + 1, 1)[0] * rate
        )
    else:
        length = (length // rate) * rate
    
    steps = length // rate - 1
    density = np.round(pts / (length / rate)).astype(int)
    
    #define fiber path
    angles = np.zeros(steps)
    angles[0] = np.random.uniform(0, 2 * np.pi)
    noise = np.random.normal(0, np.sqrt(2 * D), size=length)
    for i in range(1, steps):
        angles[i] = angles[i - 1] + noise[i] * 1
    
    angle_index = 0
    disps = []
    for i in range(steps):
        current_ang = angles[angle_index]
        angle_index += 1
        # calculate displacement based on fixed growth rate
        dx = rate * np.cos(current_ang)
        dy = rate * np.sin(current_ang)
        disps.append([dx, dy])

    disps = np.array(disps)
    start = [0, 0] # random xy point in space
    pos = []
    pos.append(start)
    for i in disps:
        current = np.array(pos[-1])
        xy_temp = current + i
        pos.append(xy_temp)   
    fiber_frame = np.array(pos)
    
    
    # Shift fiber centers to center of backbone
    frame_pts = len(fiber_frame)

    if frame_pts % 2 == 0:
        frame_center = fiber_frame[int(frame_pts / 2)]
    else:
        frame_center_a = fiber_frame[int((frame_pts / 2) - 0.5)]
        frame_center_b = fiber_frame[int((frame_pts / 2) + 0.5)]
        frame_center = [
            (frame_center_a[0] + frame_center_b[0]) / 2,
            (frame_center_a[1] + frame_center_b[1]) / 2
        ]

    x_shift_center = center[0] - frame_center[0]
    y_shift_center = center[1] - frame_center[1]
    fiber_frame_recenter = np.vstack((
        fiber_frame[:,0] + x_shift_center,
        fiber_frame[:,1] + y_shift_center
    )).T
        
    x = []
    y = []
    for i in fiber_frame_recenter:
        if method == 'normal':
            # normally distributed points
            x_hold = np.random.normal(i[0], cluster_size / 4, density)
            y_hold = np.random.normal(i[1], cluster_size / 4, density)
        elif method == 'random': 
            # randomly distributed points
            x_hold = np.random.uniform(
                i[0] - (cluster_size / 2), i[0] + (cluster_size / 2), density
            )
            y_hold = np.random.uniform(
                i[1] - (cluster_size / 2), i[1] + (cluster_size / 2), density
            )
            
        x.append(x_hold)
        y.append(y_hold)
        
    
    return np.vstack((np.hstack(x), np.hstack(y))).T    
    

def deposit_cluster_sphere(
    center: npt.NDArray[np.int_], 
    cluster_size: float, 
    pts: int
) -> npt.NDArray[np.float_]:
    """
    Deposit a single instance of a 3D spherical cluster.
    
    Args:
        center (npt.NDArray[np.int_]):
            The center coordinate of the current cluster.
        cluster_size (float):
            For spherical clusters, the cluster_size is the apparent width of the
            cluster in lateral and axial directions. In both cases, this width
            corresponds to 4 * standard deviation of the underlying normal
            distribution from which clustered points are drawn.
        pts (int):
            The number of points that will be deposited and assigned as belonging to
            this cluster instance.

    Returns:
        - npt.NDArray[np.float_]: Array of float coordinates of shape (N, d),
          where N is the number of points in this cluster instance and d is the
          dimensionality of the data.
    """

    cluster_sd = cluster_size / 4
    x = np.random.normal(loc=center[0], scale=cluster_sd, size=int(pts))
    y = np.random.normal(loc=center[1], scale=cluster_sd, size=int(pts))
    z = np.random.normal(loc=center[2], scale=cluster_sd, size=int(pts))
    
    return np.vstack((x,y,z)).T  


def add_noise_pts(
    X_coords: npt.NDArray[np.float_], 
    noise_pts: int, 
    space: Tuple[int, int], 
    cluster_shape: str, 
    gradient: bool
) -> npt.NDArray[np.float_]:
    """
    Add noise points to the simulation grid after depositing clustered points.
    
    Args:
        X_coords (npt.NDArray[np.float_]):
            Coordinates of all points belonging to clusters that have already been
            deposited by cluster deposition functions.
        noise_pts (int):
            See simulate_clusters().
        space (Tuple[int, int]):
            See simulate_clusters().
        cluster_shape (str):
            The type of cluster: "circle", "ellipse", "micelle", "fiber", or
            "sphere" as described in simulate_clusters(). Noise deposition only
            depends on the dimensionality of the data. For "sphere", noise points
            are deposited in 3-dimensions, while for all other cluster shapes points
            are deposited in 2-dimensions.
        gradient (bool):
            See simulate_clusters().

    Returns:
        - npt.NDArray[np.float_]: Array of float coordinates with shape (N, d),
          where N is the number of noise points deposited and d is the
          dimensionality of the data.
    """

    pts = int(noise_pts)
    space_min_coords = np.min(X_coords)
    space_max_coords = np.max(X_coords)
    if space_min_coords < space[0]:
        space_min = space_min_coords
    else:
        space_min = space[0]
    if space_max_coords > space[1]:
        space_max = space_max_coords
    else:
        space_max = space[1]
    
    if cluster_shape == 'sphere':
        X_noise = np.array([
            np.random.uniform(space_min, space_max, size=pts),
            np.random.uniform(space_min, space_max, size=pts), 
            np.random.uniform(space_min, space_max, size=pts)
        ])
        
        return X_noise.T
    else:    
        if gradient:
            total_space = space_max - space_min
            space_jump = total_space / 10
            noise_pts_set = []
            total_noise_pts = []
            for i in range(10):
                if i == 9:
                    space_pts = int(pts - np.sum(total_noise_pts))
                else:
                    space_pts = int((0.042553 + (i * 0.0127659)) * pts)
                    total_noise_pts.append(space_pts)

                low_x = int(i * space_jump) + space_min
                high_x = int((i * space_jump) + space_jump) + space_min
                noise_section = np.array([
                                    np.random.uniform(low_x, high_x, size=space_pts), 
                                    np.random.uniform(space_min, space_max, size=space_pts)
                                ])
                noise_pts_set.append(noise_section.T)

            X_noise = np.vstack(noise_pts_set)

            return X_noise
        else:
            X_noise = np.array([
                np.random.uniform(space_min,space_max,size=pts),
                np.random.uniform(space_min,space_max,size=pts)
            ])

            return X_noise.T
        

def add_uncertainty(
    coords: npt.NDArray[np.float_], 
    label_pad: npt.NDArray[np.int_], 
    multi_emitter: Optional[float], 
    mean_lat_prec: float, 
    sigma_lat_prec: float,
    mean_ax_prec: Optional[float] = None, 
    sigma_ax_prec: Optional[float] = None
) -> Tuple[npt.NDArray[np.float_], npt.NDArray[np.int_]]:
    """
    Applies localization uncertainty to each coordinate. Also adds
    localizations to simulate multi-emitter behavior if desired.
    
    Args:
        coords (npt.NDArray[np.float_]):
            Coordinates of all points (both noise and belonging to clusters) in the
            simulation grid.
        label_pad (npt.NDArray[np.int_]):
            The labels assigning points to clusters/noise.
        multi_emitter (Optional[float]):
            See simulate_clusters().
        mean_lat_prec (float):
            The mean of the lognormal distribution describing the lateral
            uncertainty from which individual localization uncertainties are drawn, 
            passed from precision_params.
        sigma_lat_prec (float):
            The standard deviation of the lognormal distribution describing the
            lateral uncertainty from which individual localization uncertainties are
            drawn, passed from precision_params.
        mean_ax_prec (Optional[float]):
            The mean of the lognormal distribution describing the axial uncertainty
            from which individual localization uncertainties are drawn, passed from
            precision_params.
        sigma_ax_prec (Optional[float]):
            The standard deviation of the lognormal distribution describing the
            axial uncertainty from which individual localization uncertainties are
            drawn, passed from precision_params.

    Returns:
        Tuple containing:
            - npt.NDArray[np.float_]: Array of float coordinates with shape (N, d),
              where N is the total number of points in the simulation grid after
              applying localization uncertainty and optional multi emitter
              adjustments, and d is the dimensionality of the data.
            - npt.NDArray[np.int_]: Array of integer labels with shape (N,) where N is
              the total number of points in the simulation grid after applying
              uncertainty and optional multi emitter adjustments.
    """

    num_points = coords.shape[0]

    # Generate the lateral precisions
    lateral_prec = (
        np.random.lognormal(mean=mean_lat_prec, sigma=sigma_lat_prec, size=num_points)
        / 2.355
    )

    # Generate the axial positions if needed
    if mean_ax_prec and sigma_ax_prec:
        axial_prec = (
            np.random.lognormal(mean=mean_ax_prec, sigma=sigma_ax_prec, size=num_points) 
            / 2.355
        )
   
    x_ns = []
    y_ns = []
    z_ns = []
    
    if multi_emitter is None:
        multi_emitters_list = np.full(num_points, 1)
        labels = label_pad
    else:
        multi_emitters_list = np.random.poisson(lam=multi_emitter, size=num_points)
        labels_out = []
        for i in range(len(label_pad)):
            labels_out.append(np.full(multi_emitters_list[i], label_pad[i]))
        labels = np.hstack(labels_out)
    
    for n, i in enumerate(coords):
        # Lognormal input distribution sets the stdev of the molecule localization
        lat_stdev = lateral_prec[n]

        # Generate noisy coordinates in 2D
        for j in range(multi_emitters_list[n]):
            x_n = np.random.normal(loc=i[0], scale=lat_stdev)
            y_n = np.random.normal(loc=i[1], scale=lat_stdev)

            x_ns.append(x_n)
            y_ns.append(y_n)

        # Generate the z noise if needed
            if mean_ax_prec and sigma_ax_prec:
                ax_stdev = axial_prec[n]
                z_n = np.random.normal(loc=i[2], scale=ax_stdev)
                z_ns.append(z_n)

    output = np.vstack((x_ns, y_ns)).T if not (mean_ax_prec and sigma_ax_prec) else np.vstack((x_ns, y_ns, z_ns)).T
                       
    return output, labels
