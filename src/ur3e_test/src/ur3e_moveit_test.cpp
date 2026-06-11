#include <moveit/move_group_interface/move_group_interface.h>
#include <moveit/planning_scene_interface/planning_scene_interface.h>

#include <moveit_msgs/msg/display_robot_state.h>
#include <moveit_msgs/msg/display_trajectory.h>

#include <moveit_msgs/msg/attached_collision_object.h>
#include <moveit_msgs/msg/collision_object.h>

static const rclcpp::Logger LOGGER = rclcpp::get_logger("ur3_test");
static const std::string planning_group_name = "ur3_arm";

double deg_to_rad(double deg) {
	return deg * 3.14 / 180.0;
}

int main(int argc, char** argv) {
	rclcpp::init(argc, argv);
	rclcpp::NodeOptions node_options;
	node_options.automatically_declare_parameters_from_overrides(true);
	auto move_group_node = rclcpp::Node::make_shared("move_group_interface", node_options);
	rclcpp::executors::SingleThreadedExecutor executor;
	executor.add_node(move_group_node);
	std::thread([&executor]() { executor.spin(); }).detach();
	RCLCPP_INFO(LOGGER,"successfully set up shared node and init");
	// scene setup
	moveit::planning_interface::MoveGroupInterface move_group(
			move_group_node, planning_group_name
			);
	moveit::planning_interface::PlanningSceneInterface planning_scene_interface;
	//const moveit::core::JointModelGroup* joint_model_group =
	//	move_group.getCurrentState()->getJointModelGroup(planning_group_name);
	move_group.startStateMonitor(2.0);
	moveit::core::RobotStatePtr curr_state;
	while(!move_group.getCurrentState(2.0))
		RCLCPP_INFO(LOGGER, "getting current state");
	// target pose and planning step
	RCLCPP_INFO(LOGGER,"initialized mgi, psi, and jmg");
	geometry_msgs::msg::Pose target_pose;
	target_pose.orientation.w = 1.0;
	target_pose.position.x = 0.1;
	target_pose.position.y = -0.3;
	target_pose.position.z = 0.3;
	move_group.setPoseTarget(target_pose);
	//RCLCPP_INFO(LOGGER,"set pose target");
	moveit::planning_interface::MoveGroupInterface::Plan plan;
	bool success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
	if(!success) {
		return -1;
	}
	// execution
	move_group.move();
	rclcpp::sleep_for(std::chrono::seconds(5));
	// joint value version
	//bool success;
	curr_state = move_group.getCurrentState();
	std::vector<double> joint_group_poses = {-358, -223, 72, 86, -18, -205};
	for(size_t i = 0; i < joint_group_poses.size(); i++) {
		joint_group_poses[i] = deg_to_rad(joint_group_poses[i]);
	}
	move_group.setJointValueTarget(joint_group_poses);
	success = (move_group.plan(plan) == moveit::core::MoveItErrorCode::SUCCESS);
	if(!success) {
		return -1;
	}
	move_group.move();
	rclcpp::shutdown();	
}
