# Cluster Simulate SMLM

Cluster Simulate SMLM constructs simulations in 2D or 3D. 
By default, the simulate_clusters function simulates circular clusters on a 3000 x 3000 nm plane. 

```
X, labels = simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100)

plot_clusters(X,labels)
```
		![image](https://github.com/user-attachments/assets/350e1c87-27a2-4488-b6e5-250d0efec4c3)

The method can simulate circular, elliptic, micellular, or fibrillar clusters in 2D or spherical clusters in 3D via cluster_shape set to 'circle', 'ellipse', 'micelle', or 'fiber'.

```
simulate_clusters(num_clusters = 25, clustered_pts = 50,
	cluster_size = 100, space = 5000, cluster_shape = 'micelle')

plot_clusters(X,labels)
```

Noise can be added to the simulated data by setting the number of noise points. The background noise can be uniform or have a gradient to mimic noise commonly associated with single molecule localization microscopy. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100, noise = 3000, 
	gradient = 'False', space = 5000, cluster_shape = 'ellipse', aspect_ratio = 3, fix_AR = False)

plot_clusters(X,labels)

simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100, noise = 3000,
	gradient = 'True', space = 5000, cluster_shape = 'ellipse', aspect_ratio = 3, fix_AR = False)

plot_clusters(X,labels)
```

Designed to recapitulate single molecule localization microscopy, the cluster construction enables the user to define the uncertainty distribution of positions. Setting the precision mean and standard deviation will change the log normal distribution which the uncertainty of each point is extracted from. 

```
simulate_clusters(num_clusters = 25, clustered_pts = 50, cluster_size = 100, 
	 space = 5000, cluster_shape = 'circle', precision_params = [])
plot_clusters(X,labels)
```
