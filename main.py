#!/usr/bin/env python
from constructs import Construct
from cdktf import App, TerraformStack, TerraformOutput
# 1. initialize aws provider
# need to install aws provider module
# pipenv install cdktf-cdktf-provider-aws
from cdktf_cdktf_provider_aws.provider import AwsProvider

#2. Add EC2 resource
from cdktf_cdktf_provider_aws.instance import Instance
from cdktf_cdktf_provider_aws.data_aws_ami      import DataAwsAmi

#3. Security gorup 
from cdktf_cdktf_provider_aws.security_group import SecurityGroup


 
class MyStack(TerraformStack):
    def __init__(self, scope: Construct, id: str):
        super().__init__(scope, id)

        # define resources here
        AwsProvider(self, "AWS", region="us-east-1")

        #2. Adding EC2 instalce
        #
        # data "aws_ami" "example" {
        #     executable_users = ["self"]
        #     most_recent      = true
        #     name_regex       = "^myami-\\d{3}"
        #     owners           = ["self"]

        #     filter {
        #         name   = "name"
        #         values = ["myami-*"]
        #     }

        #     filter {
        #         name   = "root-device-type"
        #         values = ["ebs"]
        #     }

        #     filter {
        #         name   = "virtualization-type"
        #         values = ["hvm"]
        #     }
        # }
        # resource "aws_instance" "web" {
        #     ami           = data.aws_ami.ubuntu.id
        #     instance_type = "t3.micro"

        #     tags = {
        #         Name = "HelloWorld"
        #     }
        # }
        ami = DataAwsAmi(self,"AmazonLinuxAmi", 
            most_recent = True, 
            owners = ["amazon"],

            filter=[
                    {
                        "name":"name", 
                        "values":["al2023-ami*"]
                    },
                    {
                        "name":"architecture", 
                        "values":["x86_64"]
                    },
                    {
                        "name":"virtualization-type", 
                        "values":["hvm"]
                    },
                    ])
        
        print("ami id:", ami.id)

        # Install webserver (LAMP Stack)
        # doc: https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/install-LAMP.html

        configure_file = "configure.sh"
        with open(configure_file) as f:
            install_script = f.read()

        # 3. creating a security gorup to allow http from the word
        allow_http = SecurityGroup(self, "allowHttp",
                                   egress=[{
                                            "fromPort"       : 0,
                                            "toPort"         : 0,
                                            "protocol"       : "-1",
                                            "cidrBlocks"     : ["0.0.0.0/0"],
                                            "ipv6CidrBlocks" : ["::/0"],
                                   }],
                                   ingress=[{
                                       "description": "allow http traffic",
                                       "fromPort":80,
                                       "toPort":80,
                                       "cidrBlocks": ["0.0.0.0/0"],
                                       "protocol": "tcp"
                                   }, 
                                   {
                                       "description": "allow SSH form my ip",
                                       "fromPort":22,
                                       "toPort":22,
                                       "cidrBlocks": ["50.235.238.194/32"],
                                       "protocol": "tcp"
                                   },
                                   ]                      
                                   )


        server = Instance(self, "WebServer", 
            ami=ami.id,
            instance_type="t3.large",
            user_data = install_script,
            vpc_security_group_ids=[allow_http.id],
            #key_name="test",
            tags={"Name":"Webserver"} )
    
        #4. displaying website url

        TerraformOutput(self, "website_url",
                value="http://"+server.public_ip ,
                )

app = App()
MyStack(app, "midterm_cdktf_website")

app.synth()
