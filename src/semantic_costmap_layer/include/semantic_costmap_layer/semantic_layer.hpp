#pragma once

#include "nav2_costmap_2d/layer.hpp"
#include "nav2_costmap_2d/layered_costmap.hpp"
#include "rclcpp/rclcpp.hpp"
#include "semantic_costmap_layer_msgs/msg/semantic_object_array.hpp"
// #include "semantic_costmap_layer_msgs/msg/semantic_object.hpp"

namespace semantic_costmap_layer
{

    class SemanticLayer : public nav2_costmap_2d::Layer
    {
    public:
        SemanticLayer();

        virtual void onInitialize();
        virtual void updateBounds(
            double robot_x,
            double robot_y,
            double robot_yaw,
            double *min_x,
            double *min_y,
            double *max_x,
            double *max_y);

        virtual void updateCosts(
            nav2_costmap_2d::Costmap2D &master_grid,
            int min_i,
            int min_j,
            int max_i,
            int max_j);

        virtual void reset();

        bool isClearable() { return false; }

    private:
        struct DetectedObject
        {
            std::string class_name;
            double x;
            double y;
            float confidence;
            double size_x;
            double size_y;
        };

        struct WorldToMapObj
        {
            unsigned int x;
            unsigned int y;
            bool world_to_map_success;
        };

        std::vector<DetectedObject> objects_;

        void callback(
            const semantic_costmap_layer_msgs::msg::SemanticObjectArray::SharedPtr msg);

        rclcpp::Subscription<
            semantic_costmap_layer_msgs::msg::SemanticObjectArray>::SharedPtr subscription_;

        std::mutex mutex_;
    };

}