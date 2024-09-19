import math
import numpy as np
from sklearn.metrics import pairwise_distances


def simulate_clusters(num_clusters, clustered_pts, cluster_size, noise_pts = 0, gradient = False, 
                      space = (0, 1000), cluster_shape = 'circle', aspect_ratio = 1.0, fix_AR = False, 
                      precision_params = (0.0, 0.0), min_sep = None, 
                      length = None, D = None, rate = 10, method = 'normal', multi_emitter = None):
    
    #First create the clusters
    X_clusts, label_list = deposit_clusters(num_clusters, clustered_pts, cluster_size, space, aspect_ratio, min_sep, cluster_shape, fix_AR, method, length, D, rate)     
    #Add noise to the data
    X_noise = add_noise_pts(X_clusts, noise_pts, space, cluster_shape, gradient)
    label_pad = np.pad(label_list, (0, len(X_noise)), 'constant', constant_values = -1)
    #Reshape the data to output Cluster,Noise, and labels
    X_points = np.vstack((X_clusts,X_noise))
    
    X_points_final, labels = add_uncertainty(X_points, label_pad,  multi_emitter,  *precision_params)
    
    return X_points_final, labels

    
def deposit_clusters(num_clusters, clustered_pts, cluster_size, space, aspect_ratio, min_sep, cluster_shape, fix_AR, method, length, D, rate):
    
    if min_sep == None:
        min_sep = 0.5 * np.max(cluster_size)

    centers,cond = set_centers(num_clusters,space,min_sep, cluster_shape)
    if cond==True:
        print('Failed')
        return None
    pts = clustered_pts
    cluster_width = cluster_size
    X_temp_clusts = []
    label_list = []
    for i in range(num_clusters):
        if type(cluster_size) == list:
            cluster_width = np.random.randint(cluster_size[0], cluster_size[1]+1, 1)
        if type(clustered_pts) ==list:
            pts = np.random.randint(clustered_pts[0],clustered_pts[1]+1, 1)

        if cluster_shape == 'circle':
            X_temp = deposit_cluster_ellipse(centers[i], cluster_width, 1.0, pts, True)
        elif cluster_shape == 'ellipse':
            X_temp = deposit_cluster_ellipse(centers[i], cluster_width, aspect_ratio, pts, fix_AR)
        elif cluster_shape == 'micelle':
            X_temp = deposit_cluster_micelle(centers[i], cluster_width, aspect_ratio, pts, fix_AR)
        elif cluster_shape == 'fiber':
            X_temp = deposit_cluster_fiber(centers[i], cluster_width, pts, length, D, rate, method)
        elif cluster_shape == 'sphere':
            X_temp = deposit_cluster_sphere(centers[i], cluster_width, pts)   
            
        label_list.append(np.full(len(X_temp),i))   
        X_temp_clusts.append(X_temp)
    
    
    X_clusters = np.vstack(X_temp_clusts)
    return X_clusters, np.hstack(label_list)

def set_centers(num_clusters,space,min_sep, cluster_shape):
    terminate = False
    centers = [None]
    
    if cluster_shape == 'sphere':
        centers[0] = [np.random.randint(low=space[0]+1,high=space[1]),np.random.randint(low=space[0]+1,high=space[1]), np.random.randint(low=space[0]+1,high=space[1])]
        count = 1
        iterations = 0
        while count<num_clusters:
            centers.append([np.random.randint(low=space[0]+1,high=space[1]),np.random.randint(low=space[0]+1,high=space[1]), np.random.randint(low=space[0]+1,high=space[1])])
            dist_c = dist_check(np.array(centers),min_sep)
            if dist_c==True:
                count+=1
                iterations+=1
            else:
                centers.pop()
                iterations+=1
                if iterations>50000:
                    terminate=True
                    print('Distance between clusters is too restrictive')
                    break
    else:
        centers[0] = [np.random.randint(low=space[0]+1,high=space[1]),np.random.randint(low=space[0]+1,high=space[1])]
        count = 1
        iterations = 0
        while count<num_clusters:
            centers.append([np.random.randint(low=space[0]+1,high=space[1]),np.random.randint(low=space[0]+1,high=space[1])])
            dist_c = dist_check(np.array(centers),min_sep)
            if dist_c==True:
                count+=1
                iterations+=1
            else:
                centers.pop()
                iterations+=1
                if iterations>50000:
                    terminate=True
                    print('Distance between clusters is too restrictive')
                    break

    return np.array(centers),terminate

#Ensures centers are seperated by a defined distance
def dist_check(test_centers,threshold):
    p_test = pairwise_distances(test_centers)
    placeholder = []
    for n,i in enumerate(p_test):
        placeholder.append(np.delete(i,n))
        
    placeholder = np.array(placeholder)
    if np.where(placeholder<threshold)[0].size>0:
        outcome = False
    else:
        outcome = True
    
    return outcome

def deposit_cluster_ellipse(center, cluster_size, aspect_ratio, pts, fix_AR):
    
    cluster_sd = cluster_size / 4

    if aspect_ratio < 1.0:
        raise ValueError(f"aspect_ratio = {aspect_ratio} is invalid, input values must be ≥ 1.0.")
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
        x_hold_rot = ((x_hold[j]-center[0])*(math.cos(theta_rot)))-((y_hold[j]-center[1])*(math.sin(theta_rot)))+center[0]
        y_hold_rot = ((x_hold[j]-center[0])*(math.sin(theta_rot)))+((y_hold[j]-center[1])*(math.cos(theta_rot)))+center[1]
        x.append(x_hold_rot)
        y.append(y_hold_rot)
       
    
    return np.vstack((x,y)).T

#Micelle clusters ***********************************
def deposit_cluster_micelle(center, cluster_size, aspect_ratio, pts, fix_AR):
    
    if aspect_ratio < 1.0:
        raise ValueError(f"aspect_ratio = {aspect_ratio} is invalid, input values must be ≥ 1.0.")
    else:
        if fix_AR == True:
            elongation = aspect_ratio
        else:
            elongation = np.random.uniform(1, aspect_ratio)
            
    R = cluster_size/2
    theta_inner = np.random.uniform(0,2*np.pi, pts)
    radius = np.random.uniform(R/1.5,R, pts)
    x_hold = (radius * (np.cos(theta_inner)*elongation))+center[0]
    y_hold = (radius * np.sin(theta_inner))+center[1]
    
    theta_rot = np.random.uniform(0,(2*np.pi))
    x = []
    y = []
    for j in range(len(x_hold)):
        x_rot = ((x_hold[j]-center[0])*(math.cos(theta_rot)))-((y_hold[j]-center[1])*(math.sin(theta_rot)))+center[0]
        y_rot = ((x_hold[j]-center[0])*(math.sin(theta_rot)))+((y_hold[j]-center[1])*(math.cos(theta_rot)))+center[1]
        x.append(x_rot)
        y.append(y_rot)
        
    
    return np.vstack((x,y)).T

def deposit_cluster_fiber(center, cluster_size, pts, length, D, rate, method):
    
    if type(length) == list:
        length = np.random.randint(length[0] // rate, length[1] // rate + 1, 1)[0] * rate
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
        frame_center = [(frame_center_a[0] + frame_center_b[0]) / 2, (frame_center_a[1] + frame_center_b[1]) / 2]

    x_shift_center = center[0] - frame_center[0]
    y_shift_center = center[1] - frame_center[1]
    fiber_frame_recenter = np.vstack((fiber_frame[:,0] + x_shift_center, fiber_frame[:,1] + y_shift_center)).T
        
    x = []
    y = []
    for i in fiber_frame_recenter:
        if method == 'normal':
            # normally distributed points
            x_hold = np.random.normal(i[0], cluster_size / 4, density)
            y_hold = np.random.normal(i[1], cluster_size / 4, density)
        elif method == 'random': 
            # randomly distributed points
            x_hold = np.random.uniform(i[0] - (cluster_size / 2), i[0] + (cluster_size / 2), density)
            y_hold = np.random.uniform(i[1] - (cluster_size / 2), i[1] + (cluster_size / 2), density)
            
        x.append(x_hold)
        y.append(y_hold)
        
    
    return np.vstack((np.hstack(x), np.hstack(y))).T    
    
def deposit_cluster_sphere(center, cluster_size, pts):
    cluster_sd = cluster_size/4
    x = np.random.normal(loc=center[0],scale=cluster_sd,size=int(pts))
    y = np.random.normal(loc=center[1],scale=cluster_sd,size=int(pts))
    z = np.random.normal(loc=center[2],scale=cluster_sd,size=int(pts))
    
    return np.vstack((x,y,z)).T  



# Pts unassigned to any clusters added to the space
def add_noise_pts(X_coords, noise_pts, space, cluster_shape, gradient = False):
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
        X_noise = np.array([np.random.uniform(space_min, space_max, size=pts),
                            np.random.uniform(space_min, space_max, size=pts), 
                            np.random.uniform(space_min, space_max, size=pts)])
        return(X_noise.T)
    else:    
        if gradient:
            total_space = space_max - space_min
            space_jump = total_space/10
            noise_pts_set = []
            total_noise_pts = []
            for i in range(10):
                if i == 9:
                    space_pts = int(pts-np.sum(total_noise_pts))
                else:
                    space_pts = int((.042553 + (i*0.0127659)) * pts)
                    total_noise_pts.append(space_pts)

                low_x = int(i*space_jump)+space_min
                high_x = int((i*space_jump) + space_jump)+space_min
                noise_section = np.array([np.random.uniform(low_x, high_x, size = space_pts), 
                                          np.random.uniform(space_min, space_max, size = space_pts)])
                noise_pts_set.append(noise_section.T)

            X_noise = np.vstack(noise_pts_set)
            return X_noise
        else:
            X_noise = np.array([np.random.uniform(space_min,space_max,size=pts),
                                np.random.uniform(space_min,space_max,size=pts)])
            return X_noise.T
        

# coords in the nx2 or nx3 points array
# default behavior is no z (precision arrays set to None)
# conditional execution of the z dim requires both mean and sigma for the axial to not be None-type
def add_uncertainty(coords, label_pad, multi_emitter, mean_lat_prec, sigma_lat_prec,
                    mean_ax_prec=None, sigma_ax_prec=None):
   
    num_points = coords.shape[0]

    # Generate the lateral precisions
    lateral_prec = np.random.lognormal(mean=mean_lat_prec, sigma=sigma_lat_prec, size=num_points) / 2.355

    # Generate the axial positions if needed
    if mean_ax_prec and sigma_ax_prec:
        axial_prec = np.random.lognormal(mean=mean_ax_prec, sigma=sigma_ax_prec, size=num_points) / 2.355
   
    x_ns = []
    y_ns = []
    z_ns = []
    
    if multi_emitter is None:
        multi_emitters_list = np.full(num_points, 1)
        labels = label_pad
    else:
        multi_emitters_list = np.random.poisson(lam = multi_emitter, size = num_points)
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
