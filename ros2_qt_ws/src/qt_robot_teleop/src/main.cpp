#include "main_window.h"
#include <QApplication>
#include <rclcpp/rclcpp.hpp>
#include <thread>

int main(int argc, char *argv[]) {
    // 初始化 Qt 应用
    QApplication a(argc, argv);

    // 初始化 ROS2
    rclcpp::init(argc, argv);

    // 创建并显示主窗口
    MainWindow w;
    w.show();

    // 在单独的线程中运行 ROS2 spin，避免阻塞 Qt 事件循环
    std::thread ros_spin_thread([]() {
        auto node = MainWindow::getNode();
        if (node) {
            rclcpp::spin(node);
        }
    });

    // 运行 Qt 事件循环（主线程）
    int result = a.exec();

    // 退出前清理 ROS2 和线程
    rclcpp::shutdown();
    if (ros_spin_thread.joinable()) {
        ros_spin_thread.join();
    }

    return result;
}