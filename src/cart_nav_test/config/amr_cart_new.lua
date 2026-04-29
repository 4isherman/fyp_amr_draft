-- cartographer_3d.lua
-- 3D Cartographer configuration for ROS 2 Jazzy / Gazebo Harmonic
-- Frames: map -> odom -> base_footprint, tracking via imu_link

include "map_builder.lua"
include "trajectory_builder.lua"

options = {
  -- =========================================================
  -- Frame configuration (do not modify)
  -- =========================================================
  map_frame             = "map",
  tracking_frame        = "imu_link",
  -- published_frame       = "base_footprint",
  published_frame       = "odom",
  odom_frame            = "odom",

  -- published frame = odom, and provide_odom_frame = false, fixes the unstable map odom flickering

  -- =========================================================
  -- Sensor input flags
  -- =========================================================
  provide_odom_frame    = false,
  -- provide_odom_frame    = true,    -- temporary: lets Cartographer publish odom->base_footprint
                                   -- revert to false once diff drive TF is confirmed working
  publish_frame_projected_to_2d = true,

  use_pose_extrapolator = true,
  use_odometry          = true,    -- subscribe to /odom
  use_nav_sat           = false,
  use_landmarks         = false,

  num_laser_scans       = 0,       -- no 2D laser
  num_multi_echo_laser_scans = 0,

  num_point_clouds      = 1,       -- one 3D point cloud topic (e.g. /points)
  num_subdivisions_per_laser_scan = 1,  -- required by cartographer_ros even in 3D-only mode

  lookup_transform_timeout_sec  = 0.3,
  submap_publish_period_sec     = 0.3,
  pose_publish_period_sec       = 5e-3,
  trajectory_publish_period_sec = 30e-3,
  rangefinder_sampling_ratio    = 1.0,
  fixed_frame_pose_sampling_ratio = 1.0,
  imu_sampling_ratio            = 1.0,
  odometry_sampling_ratio       = 1.0,
  landmarks_sampling_ratio      = 1.0,

  -- Required: cartographer_ros reads trajectory_builder and map_builder
  -- from inside the options table, not from the global scope.
  trajectory_builder            = TRAJECTORY_BUILDER,
  map_builder                   = MAP_BUILDER,
}

-- =========================================================
-- Map builder (3D SLAM)
-- =========================================================
MAP_BUILDER.use_trajectory_builder_3d = true
MAP_BUILDER.num_background_threads     = 4

-- =========================================================
-- Trajectory builder 3D
-- =========================================================
TRAJECTORY_BUILDER_3D.num_accumulated_range_data = 1

-- NOTE: lidar running at ~4 Hz. If flicker persists, increase to 2 or 3
-- to accumulate denser scans before insertion at the cost of latency.

-- IMU — required for 3D; must match tracking_frame = "imu_link"
TRAJECTORY_BUILDER_3D.imu_gravity_time_constant = 10.0
TRAJECTORY_BUILDER_3D.pose_extrapolator.use_imu_based = true
TRAJECTORY_BUILDER_3D.pose_extrapolator.constant_velocity.imu_gravity_time_constant = 10.0
TRAJECTORY_BUILDER_3D.pose_extrapolator.constant_velocity.pose_queue_duration = 0.5

-- Range finder
TRAJECTORY_BUILDER_3D.min_range = 0.15
TRAJECTORY_BUILDER_3D.max_range = 10.0

-- Voxel filter (tune to your lidar point density)
TRAJECTORY_BUILDER_3D.voxel_filter_size = 0.15

-- High-resolution adaptive voxel filter
TRAJECTORY_BUILDER_3D.high_resolution_adaptive_voxel_filter = {
  max_length                    = 2.0,
  min_num_points                = 150,
  max_range                     = 15.0,
}

-- Low-resolution adaptive voxel filter
TRAJECTORY_BUILDER_3D.low_resolution_adaptive_voxel_filter = {
  max_length                    = 4.0,
  min_num_points                = 200,
  max_range                     = 60.0,
}

-- Ceres scan matcher (local SLAM)
TRAJECTORY_BUILDER_3D.ceres_scan_matcher = {
  occupied_space_weight_0       = 1.0,
  occupied_space_weight_1       = 6.0,
  translation_weight            = 5.0,
  rotation_weight               = 4e5,   -- very high: scan matcher cannot tilt the map
  only_optimize_yaw             = false,
  ceres_solver_options = {
    use_nonmonotonic_steps      = false,
    max_num_iterations          = 12,
    num_threads                 = 1,
  },
}

-- Motion filter (suppress submaps while robot is still)
TRAJECTORY_BUILDER_3D.motion_filter = {
  max_time_seconds              = 0.25,  -- must be less than scan period (~0.25s at 4Hz)
  max_distance_meters           = 0.01,
  max_angle_radians             = 0.001,
}

-- Submaps
TRAJECTORY_BUILDER_3D.submaps = {
  high_resolution               = 0.10,
  high_resolution_max_range     = 20.0,
  low_resolution                = 0.45,
  num_range_data                = 160,
  range_data_inserter = {
    hit_probability             = 0.55,
    miss_probability            = 0.49,
    num_free_space_voxels       = 2,
    intensity_threshold         = 100,
  },
}

-- =========================================================
-- Pose graph (global SLAM / loop closure)
-- =========================================================
POSE_GRAPH.optimize_every_n_nodes        = 90  -- less frequent optimization = less frequent Z jumps
POSE_GRAPH.constraint_builder.sampling_ratio               = 0.03
POSE_GRAPH.constraint_builder.max_constraint_distance      = 15.0
POSE_GRAPH.constraint_builder.min_score                    = 0.55
POSE_GRAPH.constraint_builder.global_localization_min_score = 0.60

POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.branch_and_bound_depth    = 8
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.full_resolution_depth      = 3
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.min_rotational_score       = 0.77
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.min_low_resolution_score   = 0.55
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.linear_xy_search_window    = 5.0
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.linear_z_search_window     = 1.0
POSE_GRAPH.constraint_builder.fast_correlative_scan_matcher_3d.angular_search_window      = math.rad(15.)

POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.occupied_space_weight_0  = 5.0
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.occupied_space_weight_1  = 30.0
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.translation_weight       = 10.0
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.rotation_weight          = 40.0 --1.0
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.only_optimize_yaw        = true
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.ceres_solver_options.use_nonmonotonic_steps = false
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.ceres_solver_options.max_num_iterations     = 10
POSE_GRAPH.constraint_builder.ceres_scan_matcher_3d.ceres_solver_options.num_threads            = 1

POSE_GRAPH.optimization_problem.huber_scale                        = 5e2
POSE_GRAPH.optimization_problem.acceleration_weight                = 1.1e3
POSE_GRAPH.optimization_problem.rotation_weight                    = 3.2e5
POSE_GRAPH.optimization_problem.use_online_imu_extrinsics_in_3d   = true
POSE_GRAPH.optimization_problem.fix_z_in_3d                       = true
POSE_GRAPH.optimization_problem.local_slam_pose_translation_weight = 1e5
POSE_GRAPH.optimization_problem.local_slam_pose_rotation_weight    = 1e5
POSE_GRAPH.optimization_problem.odometry_translation_weight        = 1e5
POSE_GRAPH.optimization_problem.odometry_rotation_weight           = 1e5
POSE_GRAPH.optimization_problem.fixed_frame_pose_translation_weight = 1e1
POSE_GRAPH.optimization_problem.fixed_frame_pose_rotation_weight   = 1e2
POSE_GRAPH.optimization_problem.fixed_frame_pose_use_tolerant_loss = false
POSE_GRAPH.optimization_problem.fixed_frame_pose_tolerant_loss_param_a = 1
POSE_GRAPH.optimization_problem.fixed_frame_pose_tolerant_loss_param_b = 1
POSE_GRAPH.optimization_problem.log_solver_summary                 = false
POSE_GRAPH.optimization_problem.ceres_solver_options.use_nonmonotonic_steps = false
POSE_GRAPH.optimization_problem.ceres_solver_options.max_num_iterations     = 200
POSE_GRAPH.optimization_problem.ceres_solver_options.num_threads            = 4

POSE_GRAPH.max_num_final_iterations  = 200
POSE_GRAPH.global_sampling_ratio     = 0.003
POSE_GRAPH.log_residual_histograms   = true
POSE_GRAPH.global_constraint_search_after_n_seconds = 10.0
POSE_GRAPH.matcher_translation_weight = 5e2
POSE_GRAPH.matcher_rotation_weight    = 1.6e3

return options