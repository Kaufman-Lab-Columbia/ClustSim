# Clust-Sim SMLM

Clust-Sim SMLM is a python program designed to constructs single molecule localization microscopy (SMLM) simulations in 2D or 3D. The implementation is capable of constructing clusters with varying degrees of complexity, allows for the addition of noise, and can enable the user to set the underlying uncertainty distributions of the localizations. 

## Getting Started
### Dependencies
- sci-kit learn
- matplotlib
- numpy
### Installation
Clust-Sim SMLM can be installed via pip:
```
pip install ....?
```
or
```
pip install ....?
```

## Usage
Introduction_sim.py follows along with the information provided below.
### Simple Clusters
By default, the simulate_clusters function simulates circular clusters on a 1000 x 1000 nm plane. The function returns an array of coordinates and an array of integers that map to cluster assignments. The plot_clusters function allows for easy visualization of the simulated clusters. 
```
X, labels = simulate_clusters(num_clusters = 10, clustered_pts = 50, cluster_size = 100)

plot_clusters(X,labels)
```
![image](https://github.com/user-attachments/assets/6a7a0dee-2d11-4a39-b396-356e090aa614)

### Varying Cluster Shape
Circular, elliptic, micellular, or fibrillar clusters in 2D or spherical clusters in 3D  can be simulated via cluster_shape set to 'circle', 'ellipse', 'micelle', 'fiber', or 'sphere', respectively. The simulation size can be set by setting space = [lower bound, upper bound]. The separation between clusters can also be set by the min_sep argument. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50,
		cluster_size = 200, space = [0,5000],
		min_sep = 400, cluster_shape = 'micelle')

plot_clusters(X,labels)
```
![image](https://github.com/user-attachments/assets/f309b8ad-be30-4198-afdf-e51686312489)

### Simulating Noise
Noise can be added to the simulated data by setting the number of noise points to be added. The background noise is uniform by default can be set to have a gradient to mimic noise commonly associated with single molecule localization microscopy by setting gradient = True. Noise is assigned as -1. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 200, noise_pts = 3000, 
	min_sep = 400, space = [0,5000])

plot_clusters(X,labels)
```
![image](https://github.com/user-attachments/assets/33576e83-60e8-4e8e-85c8-2cb5a1b15ace)

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 200, noise_pts = 3000,
	space = [0,5000], gradient = True)

plot_clusters(X,labels)
```
![image](https://github.com/user-attachments/assets/f70913f2-c675-43c5-a57b-e14b37ac47fe)

### Complex Clusters
More complex cluster shapes can be achieved by adjusting the aspect_ratio to a value greater than 1. Setting fix_AR = True will set all cluster aspect ratios to the same value, fix_AR = False will enable each cluster to have a unique aspect ratio that is randomly set betweeen 1 and the user defined aspect_ratio. 

```
simulate_clusters(num_clusters = 15, clustered_pts = 100, cluster_size = 200, min_sep = 800,
	noise_pts = 3000, space = [0,5000], cluster_shape = 'ellipse',
	aspect_ratio = 4, fix_AR = True)
```
![image](https://github.com/user-attachments/assets/76a0b0f3-29f9-45ef-87d3-9aad4abf0a68)

```
simulate_clusters(num_clusters = 15, clustered_pts = 100, cluster_size = 200, min_sep = 800,
	noise_pts = 3000, space = [0,5000], cluster_shape = 'micelle',
	aspect_ratio = 4, fix_AR = False)
```
![image](https://github.com/user-attachments/assets/39896990-d5fe-4bcc-8b62-e8b3a510d8c5)
Fibrillar clusters are designed to 



### Defining localization uncertainty
Designed to recapitulate single molecule localization microscopy, the cluster construction enables the user to define the uncertainty distribution of positions. Setting the precision mean and standard deviation will change the log normal distribution which the uncertainty of each point is extracted from. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100, 
	 space = 5000, cluster_shape = 'circle', precision_params = [])
plot_clusters(X,labels)
```
## License
Clust_Sim-SMLM is licensed with an MIT license. See LICENSE file for more information. 
## Referencing
If you use Clust_Sim-SMLM for your work, cite with the following:
```
Cite here
```
## Contact 
