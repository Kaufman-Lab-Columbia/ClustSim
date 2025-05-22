# ClustSim 
![image](https://github.com/user-attachments/assets/a7bbbf8c-941a-439f-b600-07930b03ced8)

ClustSim is a Python program designed to construct simulated single molecule localization microscopy (SMLM) data in 2D or 3D. This implementation is capable of simulating clusters with varying degrees of complexity, clusters with noise, localization uncertainties, and multi-emitter behavior. 

## Getting Started
### Dependencies
- scikit-learn
- Matplotlib
- NumPy
### Installation
ClustSim can be installed via pip:
```
pip install ClustSim
```

## Basic Usage
Intro_ClustSim.ipynb follows along with the information provided below.
### Simple Clusters
By default, `simulate_clusters()` simulates circular clusters on a 1000 x 1000 plane (arbitrary units). The function returns an `(N, d)` shaped array of coordinates and an `(N,)` shaped array of integer labels that map points to cluster assignments, where `N` is the total number of points deposited in the simulation plane and `d` is the dimensionality of the data. For visualization of the simulated clusters, use `plot_clusters()` as demonstrated below.

```
X, labels = simulate_clusters(
  num_clusters=10, clustered_pts=50, cluster_size=100
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/6a7a0dee-2d11-4a39-b396-356e090aa614
</p>

### Varying Cluster Shape
Circular, elliptical, micellular, or fibrillar clusters in 2D, or spherical clusters in 3D, can be simulated by setting the `cluster_shape` parameter to `'circle'`, `'ellipse'`, `'micelle'`, `'fiber'`, or `'sphere'`, respectively. The simulation size is defined by setting `space=upper_bound` which will set the size of the simulation with origin set at 0. Otherwise, the origin can be set manually with `space=(lower_bound, upper_bound)`. The separation between cluster centers can also be set using the `min_sep` argument. 

```
X, labels = simulate_clusters(
  num_clusters=25, clustered_pts=50, cluster_size=200,
  space=(0, 5000), min_sep=400.0, cluster_shape='micelle'
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/f309b8ad-be30-4198-afdf-e51686312489
</p>

### Simulating Noise
Noise can be added to simulated clustered data by setting the number of noise points to be deposited among already existing clustered points. The background noise is uniform by default, but can be modified to have a gradient to mimic the uneven noise commonly associated with TIRF imaging in SMLM. This is done by setting `gradient=True`. Noise points are assigned a label of -1. 

```
X, labels = simulate_clusters(
  num_clusters=25, clustered_pts=50, cluster_size=200,
  noise_pts=3000, min_sep=400.0, space=(0, 5000)
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/33576e83-60e8-4e8e-85c8-2cb5a1b15ace
</p>

```
X, labels = simulate_clusters(
  num_clusters=25, clustered_pts=50, cluster_size=200,
  noise_pts=3000, space=(0, 5000), gradient=True
)

plot_clusters(X, labels)
```
<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/f70913f2-c675-43c5-a57b-e14b37ac47fe
</p>


### Complex Clusters
More complex cluster shapes can be achieved by adjusting `aspect_ratio` to a value greater than 1. The input parameter `fix_AR=True` will set all cluster aspect ratios to the same value, while `fix_AR=False` will enable each cluster to have a unique aspect ratio that is randomly set betweeen 1 and the user defined `aspect_ratio`. 

```
X, labels = simulate_clusters(
  num_clusters=15, clustered_pts=100, cluster_size=200,
  min_sep=800.0, noise_pts=3000, space=(0, 5000),
  cluster_shape='ellipse', aspect_ratio=4.0, fix_AR=True
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/76a0b0f3-29f9-45ef-87d3-9aad4abf0a68
</p>

```
X, labels = simulate_clusters(
  num_clusters=15, clustered_pts=100, cluster_size=200,
  min_sep=800.0, noise_pts=3000, space=(0, 5000),
  cluster_shape='micelle', aspect_ratio=4.0, fix_AR=False
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/39896990-d5fe-4bcc-8b62-e8b3a510d8c5
</p>


Fibrillar clusters can be simulated by inputting an additional fiber size parameter, `length`, and a fiber persistence parameter, `D`. Here, the `cluster_size` input sets the fiber width. Decreasing the `D` parameter will result in straighter fibers, while increasing `D` will result in more fiber curvature. 

```
X, labels = simulate_clusters(
  num_clusters=10, clustered_pts=500, cluster_size=200,
  noise_pts=1500, space=(0, 10000), cluster_shape='fiber',
  length=2000, D=0.01
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/697c989b-dcbc-4936-8434-a5138c802c4c
</p>

### Defining localization uncertainty
In SMLM, each point has a localization uncertainty that is dependent on the signal intensity of the emitter in the source image. Heterogeneous signal intensities across many emitters lead to a generally broad spread of uncertainties, which often follows a log-normal distribution. To recapitulate experimental uncertainties, the user can specify the characteristics of the underlying log-normal distribution from which each point receives a unique localization uncertainty. The `precision_params` input is a list corresponding to the mean and standard deviation of this log-normal distribution. Uncertainties are drawn randomly from this distribution using `numpy.random.lognormal()`, where `precision_params=(mean, stdev)`. By default, these parameters are both set to 0.

```
X, labels = simulate_clusters(
  num_clusters=20, clustered_pts=25, cluster_size=200,
  min_sep=400.0, noise_pts=1500, space=(0, 3000),
  precision_params=(3.0, 0.28)
)

plot_clusters(X, labels)
```

<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/6ea540c3-c53a-4445-8c6a-cd76ddc73795
</p>


For 3D clusters, the first two numbers in `precision_params` correspond to the lateral uncertainty, while the next two correspond to the axial uncertainty, such that `precision_params=(lateral_mean, lateral_stdev, axial_mean, axial_stdev)`.

```
X, labels = simulate_clusters(
  num_clusters=20, clustered_pts=50, cluster_size=200,
  min_sep=400.0, noise_pts=1500, space=(0, 3000),
  cluster_shape='sphere', precision_params=(3.0, 0.28, 4.0, 0.28)
)

plot_clusters(X, labels)
```
<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/03dc39da-9fb1-4068-a9a9-55eca9397aa7
</p>
	
### Simulating multi-emitters
During SMLM imaging, a single emitter will commonly blink on and off multiple times, leading to multiple localizations for a single molecule. Providing an input value for `multi_emitter` will recapitulate this behavior. The input for `multi_emitter` should be set to a floating point value which corresponds to the mean number of localizations per molecule as defined by a Poisson distribution. By default, `multi_emitter` is set to `None`, resulting in each molecule being represented by exactly one localization.

```
X, labels = simulate_clusters(
  num_clusters=20, clustered_pts=25, cluster_size=200,
  min_sep=400.0, noise_pts=1500, space=(0, 3000),
  gradient=True, precision_params=(3.0, 0.28), multi_emitter=3.0
)

plot_clusters(X, labels)
```
<p align="center">
  <img width="300" height="300" src=https://github.com/user-attachments/assets/d615b980-871c-4ffa-a5ac-ee3d1cd2ea1e
</p>
 
## License
ClustSim is licensed with an MIT license. See LICENSE file for more information. 
## Referencing
If you use ClustSim for your work, cite with the following (currently in preprint):

Hammer, J. L., Devanny, A. J. & Kaufman, L. J. Density-based optimization for unbiased, reproducible clustering applied to single molecule localization microscopy. Preprint at https://www.biorxiv.org/content/10.1101/2024.11.01.621498v1 (2024)

## Contact 
kaufmangroup.rubylab@gmail.com
