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
            "\n\n\nSemantic layer initialized\n\n\n");
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

    // void SemanticLayer::updateBounds(
    //     double robot_x,
    //     double robot_y,
    //     double robot_yaw,
    //     double *min_x,
    //     double *min_y,
    //     double *max_x,
    //     double *max_y)
    // {
    //     for (const auto &obj : objects_)
    //     {
    //         *min_x = std::min(*min_x, obj.x - 1.0);
    //         *min_y = std::min(*min_y, obj.y - 1.0);

    //         *max_x = std::max(*max_x, obj.x + 1.0);
    //         *max_y = std::max(*max_y, obj.y + 1.0);
    //     }
    // }

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

    // void SemanticLayer::updateCosts(
    //     nav2_costmap_2d::Costmap2D &master_grid,
    //     int min_i,
    //     int min_j,
    //     int max_i,
    //     int max_j)
    // {
    //     // RCLCPP_INFO(
    //     //     node_.lock()->get_logger(),
    //     //     "Objects: %ld",
    //     //     objects_.size());

    //     // RCLCPP_INFO(
    //     //     node_.lock()->get_logger(),
    //     //     "Global frame: %s",
    //     //     layered_costmap_->getGlobalFrameID().c_str());

    //     std::lock_guard<std::mutex> lock(mutex_);

    //     for (const auto &obj : objects_)
    //     {
    //         unsigned int mx, my;

    //         if (master_grid.worldToMap(obj.x, obj.y, mx, my))
    //         {
    //             unsigned char cost;

    //             if (obj.class_name == "person")
    //             {
    //                 cost = nav2_costmap_2d::LETHAL_OBSTACLE;
    //             }
    //             else if (obj.class_name == "chair")
    //             {
    //                 cost = 180;
    //             }
    //             else
    //             {
    //                 cost = 1;
    //             }

    //             RCLCPP_INFO(
    //                 node_.lock()->get_logger(),
    //                 "Object Detected: %s, Score: %f, Cost: %d",
    //                 obj.class_name.c_str(), obj.confidence, cost);
    //             RCLCPP_INFO(
    //                 node_.lock()->get_logger(),
    //                 "Object Position: %.2f %.2f",
    //                 obj.x,
    //                 obj.y);

    //             master_grid.setCost(mx, my, cost);
    //         }
    //     }
    // }

    // void SemanticLayer::updateCosts(
    //     nav2_costmap_2d::Costmap2D &master_grid,
    //     int min_i,
    //     int min_j,
    //     int max_i,
    //     int max_j)
    // {
    //     std::lock_guard<std::mutex> lock(mutex_);

    //     auto node = node_.lock();

    //     for (const auto &obj : objects_)
    //     {
    //         unsigned int mx, my;

    //         bool success =
    //             master_grid.worldToMap(
    //                 obj.x,
    //                 obj.y,
    //                 mx,
    //                 my);

    //         RCLCPP_INFO(
    //             node->get_logger(),
    //             "(%s) Object world: %.2f %.2f",
    //             obj.class_name.c_str(),
    //             obj.x,
    //             obj.y);

    //         if (!success)
    //         {
    //             RCLCPP_WARN(
    //                 node->get_logger(),
    //                 "worldToMap FAILED");
    //             continue;
    //         }

    //         RCLCPP_INFO(
    //             node->get_logger(),
    //             "Map coords: %u %u",
    //             mx,
    //             my);

    //         master_grid.setCost(
    //             mx,
    //             my,
    //             nav2_costmap_2d::LETHAL_OBSTACLE);
    //     }
    // }
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
            if (obj.class_name != "person")
                continue;
                
            // top/bottom left/right of bounding box
            // unsigned int mx_tl, my_tl, mx_tr, my_tr, mx_bl, my_bl, mx_br, my_br;
            WorldToMapObj tl, tr, bl, br;
            // std::array<WorldToMapObj> test;
            // for (const auto &wtm_obj : test)
            // {
            //     tl.x = obj.x - obj.size_x/2;
            //     tl.y = obj.y - obj.size_y/2;
            //     tl.world_to_map_success = master_grid.worldToMap(
            //                                             obj.x,
            //                                             obj.y,
            //                                             tl.x,
            //                                             tl.y);
            // }
            // mx_tl = obj.x - obj.size_x/2;
            // my_tl = obj.y - obj.size_y/2;

            // mx_tr = obj.x + obj.size_x/2;
            // my_tr = obj.y - obj.size_y/2;

            // mx_bl = obj.x - obj.size_x/2;
            // my_bl = obj.y + obj.size_y/2;

            // mx_br = obj.x + obj.size_x/2;
            // my_br = obj.y + obj.size_y/2;

            // tl.x = obj.x - obj.size_x / 2;
            // tl.y = obj.y - obj.size_y / 2;
            tl.world_to_map_success = master_grid.worldToMap(
                obj.x - obj.size_x / 2,
                obj.y - obj.size_y / 2,
                tl.x,
                tl.y);
            // tr.x = obj.x + obj.size_x / 2;
            // tr.y = obj.y - obj.size_y / 2;
            tr.world_to_map_success = master_grid.worldToMap(
                obj.x + obj.size_x / 2,
                obj.y - obj.size_y / 2,
                tr.x,
                tr.y);
            // bl.x = obj.x - obj.size_x / 2;
            // bl.y = obj.y + obj.size_y / 2;
            bl.world_to_map_success = master_grid.worldToMap(
                obj.x - obj.size_x / 2,
                obj.y + obj.size_y / 2,
                bl.x,
                bl.y);
            // br.x = obj.x + obj.size_x / 2;
            // br.y = obj.y + obj.size_y / 2;
            br.world_to_map_success = master_grid.worldToMap(
                obj.x + obj.size_x / 2,
                obj.y + obj.size_y / 2,
                br.x,
                br.y);

            // tl.world_to_map_success = master_grid.worldToMap(
            //     obj.x,
            //     obj.y,
            //     tl.x,
            //     tl.y);
            // tr.x = obj.x + obj.size_x / 2;
            // tr.y = obj.y - obj.size_y / 2;
            // tr.world_to_map_success = master_grid.worldToMap(
            //     obj.x,
            //     obj.y,
            //     tr.x,
            //     tr.y);
            // bl.x = obj.x - obj.size_x / 2;
            // bl.y = obj.y + obj.size_y / 2;
            // bl.world_to_map_success = master_grid.worldToMap(
            //     obj.x,
            //     obj.y,
            //     bl.x,
            //     bl.y);
            // br.x = obj.x + obj.size_x / 2;
            // br.y = obj.y + obj.size_y / 2;
            // br.world_to_map_success = master_grid.worldToMap(
            //     obj.x,
            //     obj.y,
            //     br.x,
            //     br.y);

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

            // bool success =
            //     master_grid.worldToMap(
            //         obj.x,
            //         obj.y,
            //         mx,
            //         my);

            // RCLCPP_INFO(
            //     node->get_logger(),
            //     "(%s) Object world: %.2f %.2f",
            //     obj.class_name.c_str(),
            //     obj.x,
            //     obj.y);

            // if (!success)
            // {
            //     RCLCPP_WARN(
            //         node->get_logger(),
            //         "worldToMap FAILED");
            //     continue;
            // }

            // RCLCPP_INFO(
            //     node->get_logger(),
            //     "Map coords: %u %u",
            //     mx,
            //     my);

            // if (tl.world_to_map_success)
            // {
            //     master_grid.setCost(
            //         tl.x,
            //         tl.y,
            //         nav2_costmap_2d::LETHAL_OBSTACLE);
            // }
            // if (tr.world_to_map_success)
            // {
            //     master_grid.setCost(
            //         tr.x,
            //         tr.y,
            //         nav2_costmap_2d::LETHAL_OBSTACLE);
            // }
            // if (bl.world_to_map_success)
            // {
            //     master_grid.setCost(
            //         bl.x,
            //         bl.y,
            //         nav2_costmap_2d::LETHAL_OBSTACLE);
            // }
            // if (br.world_to_map_success)
            // {
            //     master_grid.setCost(
            //         br.x,
            //         br.y,
            //         nav2_costmap_2d::LETHAL_OBSTACLE);
            // }
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

/*
#include <mutex>
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

        // objects_.push_back({
        //     "chairss",
        //     4.0,
        //     0.0
        // });
        // objects_.push_back({
        //     "chairss",
        //     4.0,
        //     1.0
        // });
        // objects_.push_back({
        //     "chairss",
        //     4.0,
        //     2.0
        // });
        // objects_.push_back({
        //     "chairss",
        //     4.0,
        //     -1.0
        // });
        // objects_.push_back({
        //     "chairss",
        //     4.0,
        //     -2.0
        // });

        RCLCPP_INFO(
            node->get_logger(),
            "\n\n\nSemantic layer initialized XD\n\n\n");

        // RCLCPP_INFO(
        //     node_.lock()->get_logger(),
        //     "Objects(Init): %ld",
        //     objects_.size());
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
        for (const auto &obj : objects_)
        {
            *min_x = std::min(*min_x, obj.x - 1.0);
            *min_y = std::min(*min_y, obj.y - 1.0);

            *max_x = std::max(*max_x, obj.x + 1.0);
            *max_y = std::max(*max_y, obj.y + 1.0);
        }
    }
    // void SemanticLayer::updateBounds(
    //     double robot_x,
    //     double robot_y,
    //     double robot_yaw,
    //     double *min_x,
    //     double *min_y,
    //     double *max_x,
    //     double *max_y)
    // {
    //     objects_.clear();

    //     // object 1m in front of robot
    //     double obj_x =
    //         robot_x + 1.0 * cos(robot_yaw);

    //     double obj_y =
    //         robot_y + 1.0 * sin(robot_yaw);

    //     objects_.push_back({"person",
    //                         obj_x,
    //                         obj_y});

    //     // expand bounds only
    //     *min_x = std::min(*min_x, obj_x - 1.0);
    //     *min_y = std::min(*min_y, obj_y - 1.0);

    //     *max_x = std::max(*max_x, obj_x + 1.0);
    //     *max_y = std::max(*max_y, obj_y + 1.0);
    // }

    void SemanticLayer::updateCosts(
        nav2_costmap_2d::Costmap2D &master_grid,
        int min_i,
        int min_j,
        int max_i,
        int max_j)
    {
        // RCLCPP_INFO(
        //     node_.lock()->get_logger(),
        //     "Objects: %ld",
        //     objects_.size());

        // RCLCPP_INFO(
        //     node_.lock()->get_logger(),
        //     "Global frame: %s",
        //     layered_costmap_->getGlobalFrameID().c_str());

        for (const auto &obj : objects_)
        {
            unsigned int mx, my;

            if (master_grid.worldToMap(obj.x, obj.y, mx, my))
            {
                unsigned char cost;

                if (obj.class_name == "person")
                {
                    cost = nav2_costmap_2d::LETHAL_OBSTACLE;
                }
                else if (obj.class_name == "chair")
                {
                    cost = 180;
                }
                else
                {
                    cost = 100;
                }

                master_grid.setCost(mx, my, cost);
            }
        }
    }
    // void SemanticLayer::updateCosts(
    //     nav2_costmap_2d::Costmap2D &master_grid,
    //     int min_i,
    //     int min_j,
    //     int max_i,
    //     int max_j)
    // {
    //     auto node = node_.lock();

    //     RCLCPP_INFO(
    //         node->get_logger(),
    //         "Semantic updateCosts called");

    //     for (const auto &obj : objects_)
    //     {
    //         unsigned int mx, my;

    //         bool success =
    //             master_grid.worldToMap(
    //                 obj.x,
    //                 obj.y,
    //                 mx,
    //                 my);

    //         RCLCPP_INFO(
    //             node->get_logger(),
    //             "Object world=(%.2f, %.2f), map success=%d",
    //             obj.x,
    //             obj.y,
    //             success);

    //         if (success)
    //         {
    //             RCLCPP_INFO(
    //                 node->get_logger(),
    //                 "Writing cost at (%u, %u)",
    //                 mx,
    //                 my);

    //             master_grid.setCost(
    //                 mx,
    //                 my,
    //                 nav2_costmap_2d::LETHAL_OBSTACLE);
    //         }
    //     }
    // }

    void SemanticLayer::reset()
    {
        objects_.clear();
    }

}

PLUGINLIB_EXPORT_CLASS(
    semantic_costmap_layer::SemanticLayer,
    nav2_costmap_2d::Layer)

*/