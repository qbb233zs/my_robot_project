#ifndef MAIN_WINDOW_H
#define MAIN_WINDOW_H

#include <QMainWindow>
#include <rclcpp/rclcpp.hpp>
#include <geometry_msgs/msg/twist.hpp>

QT_BEGIN_NAMESPACE
namespace Ui { class MainWindow; }
QT_END_NAMESPACE

class MainWindow : public QMainWindow
{
    Q_OBJECT

public:
    static std::shared_ptr<rclcpp::Node>getNode() {
        return node_;
    }
    MainWindow(QWidget *parent = nullptr);
    ~MainWindow();

private slots:
    // 在这里声明槽函数
    void onSendClicked();

private:
    Ui::MainWindow *ui;
    rclcpp::Publisher<geometry_msgs::msg::Twist>::SharedPtr publisher_;
    static std::shared_ptr<rclcpp::Node> node_; 
};

#endif 