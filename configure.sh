#!/bin/bash
# https://docs.aws.amazon.com/linux/al2023/ug/ec2-lamp-amazon-linux-2023.html
dnf update -y
dnf install -y httpd #wget php-fpm php-mysqli php-json php php-devel

# creating index page to server and test
echo "<h1>My CDKTF Website Tutorial</h1>" > /var/www/html/index.html

systemctl start httpd
systemctl enable httpd
systemctl is-enabled httpd
