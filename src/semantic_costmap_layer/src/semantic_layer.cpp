#include <mutex>
#include <array>
#include "../include/semantic_costmap_layer/semantic_layer.hpp"
#include "pluginlib/class_list_macros.hpp"

namespace semantic_costmap_layer
{

    SemanticLayer::SemanticLayer()
    {
    }

    void SemanticLayer::onInitialize()
    {
        auto node = node_.lock();

        current_ = true;
        enabled_ = true;

        subscription_ =
            node->create_subscription<
                semantic_costmap_layer_msgs::msg::SemanticObjectArray>(
                "/semantic_objects",
                10,
                std::bind(
                    &SemanticLayer::callback,
                    this,
                    std::placeholders::_1));

        RCLCPP_INFO(
            node->get_logger(),
            "Semantic layer initialized");
    }

    void SemanticLayer::callback(
        const semantic_costmap_layer_msgs::msg::SemanticObjectArray::SharedPtr msg)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        objects_.clear();

        for (const auto &obj : msg->objects)
        {
            objects_.push_back({obj.class_name,
                                obj.position.x,
                                obj.position.y,
                                obj.confidence,
                                obj.size.x,
                                obj.size.y});
        }
    }

    void SemanticLayer::updateBounds(
        double robot_x,
        double robot_y,
        double robot_yaw,
        double *min_x,
        double *min_y,
        double *max_x,
        double *max_y)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        for (const auto &obj : objects_)
        {
            const double radius = 0.5;

            *min_x = std::min(
                *min_x,
                obj.x - radius);

            *min_y = std::min(
                *min_y,
                obj.y - radius);

            *max_x = std::max(
                *max_x,
                obj.x + radius);

            *max_y = std::max(
                *max_y,
                obj.y + radius);
        }
    }

   
    void SemanticLayer::updateCosts(
        nav2_costmap_2d::Costmap2D &master_grid,
        int min_i,
        int min_j,
        int max_i,
        int max_j)
    {
        std::lock_guard<std::mutex> lock(mutex_);

        auto node = node_.lock();

        for (const auto &obj : objects_)
        {
            // if detected class is not human/person, skip
            if (obj.class_name != "person")
                continue;
                
            WorldToMapObj tl, tr, bl, br;
          
            tl.world_to_map_success = master_grid.worldToMap(
                obj.x - obj.size_x / 2,
                obj.y - obj.size_y / 2,
                tl.x,
                tl.y);

            tr.world_to_map_success = master_grid.worldToMap(
                obj.x + obj.size_x / 2,
                obj.y - obj.size_y / 2,
                tr.x,
                tr.y);

            bl.world_to_map_success = master_grid.worldToMap(
                obj.x - obj.size_x / 2,
                obj.y + obj.size_y / 2,
                bl.x,
                bl.y);

            br.world_to_map_success = master_grid.worldToMap(
                obj.x + obj.size_x / 2,
                obj.y + obj.size_y / 2,
                br.x,
                br.y);

            std::array<WorldToMapObj, 4> corner_points_arr = {tl, tr, bl, br};
            int idx = 0;
            for (const auto &point : corner_points_arr)
            {
                if (point.world_to_map_success)
                {
                    idx++;
                    master_grid.setCost(
                        point.x,
                        point.y,
                        nav2_costmap_2d::LETHAL_OBSTACLE);
                }
                else
                {
                    RCLCPP_WARN(
                        node->get_logger(),
                        "worldToMap FAILED [%d]", idx++);
                }
            }
        }
    }

    void SemanticLayer::reset()
    {
        objects_.clear();
    }

}

PLUGINLIB_EXPORT_CLASS(
    semantic_costmap_layer::SemanticLayer,
    nav2_costmap_2d::Layer)
