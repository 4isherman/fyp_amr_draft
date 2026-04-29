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

-- Range finder
TRAJECTORY_BUILDER_3D.min_range = 0.15
TRAJECTORY_BUILDER_3D.max_range = 10.0


return options