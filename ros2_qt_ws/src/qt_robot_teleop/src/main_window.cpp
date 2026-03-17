#include "main_window.h"
#include "ui_main_window.h"
#include <QMessageBox>

// 初始化静态节点指针
std::shared_ptr<rclcpp::Node> MainWindow::node_ = nullptr;

MainWindow::MainWindow(QWidget *parent)
    : QMainWindow(parent)
    , ui(new Ui::MainWindow)
{
    ui->setupUi(this);

    node_ = rclcpp::Node::make_shared("qt_teleop_node");
    publisher_ = node_->create_publisher<geometry_msgs::msg::Twist>("/cmd_vel", 10);

    // 连接按钮点击信号到槽函数
    connect(ui->pushButton, &QPushButton::clicked, this, &MainWindow::onSendClicked);
}

MainWindow::~MainWindow()
{
    delete ui;
}

void MainWindow::onSendClicked()
{
    QString input = ui->lineEdit->text().trimmed(); 
    auto twist_msg = geometry_msgs::msg::Twist();

    if (input == "前进" || input == "forward") {
        twist_msg.linear.x = 0.5;   
        twist_msg.angular.z = 0.0; 
    } else if (input == "后退" || input == "backward") {
        twist_msg.linear.x = -0.3;  
        twist_msg.angular.z = 0.0;
    } else if (input == "左转" || input == "left") {
        twist_msg.linear.x = 0.2;   
        twist_msg.angular.z = 0.5;   
    } else if (input == "右转" || input == "right") {
        twist_msg.linear.x = 0.2;
        twist_msg.angular.z = -0.5;  
    } else if (input == "停止" || input == "stop") {
        twist_msg.linear.x = 0.0;
        twist_msg.angular.z = 0.0;
    } else {
   
        ui->lineEdit->clear();
        ui->lineEdit->setPlaceholderText("请输入：前进/后退/左转/右转/停止");
        QMessageBox::warning(this, "错误", "无效指令！请输入：前进/后退/左转/右转/停止");
        return;
    }

    publisher_->publish(twist_msg);

    ui->lineEdit->clear();
}