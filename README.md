# Clust-Sim SMLM

Clust-Sim SMLM constructs simulations in 2D or 3D. 



## How to use
### Simple Clusters
By default, the simulate_clusters function simulates circular clusters on a 1000 x 1000 nm plane. The output is a array of coordinates and an array of integers that map to cluster assignments. 

```
X, labels = simulate_clusters(num_clusters = 10, clustered_pts = 50, cluster_size = 100)

plot_clusters(X,labels)
```

### Varying Cluster Shape
The method can simulate circular, elliptic, micellular, or fibrillar clusters in 2D or spherical clusters in 3D via cluster_shape set to 'circle', 'ellipse', 'micelle', 'fiber', or 'sphere'. The simulation size can be set by setting space = [lower bound, upper bound]. The separation between clusters can also be set by the min_sep argument. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50,
		cluster_size = 200, space = [0,5000],
		min_sep = 400, cluster_shape = 'micelle')

plot_clusters(X,labels)
```

### Simulating Noise
Noise can be added to the simulated data by setting the number of noise points to be added. The background noise is uniform by default can be set to have a gradient to mimic noise commonly associated with single molecule localization microscopy by setting gradient = True. Noise is assigned as -1. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 200, noise_pts = 3000, 
	min_sep = 400, space = [0,5000])

plot_clusters(X,labels)
```
```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 200, noise_pts = 3000,
	space = [0,5000], gradient = True)

plot_clusters(X,labels)
```

### Complex Clustering
More complex cluster shapes can be achieved by adjusting the aspect_ratio to a value greater than 1. Setting fix_AR = True will set all cluster aspect ratios to the same value, fix_AR = False will enable each cluster to have a unique aspect ratio that is randomly set betweeen 1 and the user defined aspect_ratio. 

```
simulate_clusters(num_clusters = 15, clustered_pts = 100, cluster_size = 200, min_sep = 800,
	noise_pts = 3000, space = [0,5000], cluster_shape = 'ellipse',
	aspect_ratio = 4, fix_AR = True)
```
```
simulate_clusters(num_clusters = 15, clustered_pts = 100, cluster_size = 200, min_sep = 800,
	noise_pts = 3000, space = [0,5000], cluster_shape = 'micelle',
	aspect_ratio = 4, fix_AR = False)
```

Fibrillar clusters are designed to 



### Defining localization uncertainty
Designed to recapitulate single molecule localization microscopy, the cluster construction enables the user to define the uncertainty distribution of positions. Setting the precision mean and standard deviation will change the log normal distribution which the uncertainty of each point is extracted from. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100, 
	 space = 5000, cluster_shape = 'circle', precision_params = [])
plot_clusters(X,labels)
```
