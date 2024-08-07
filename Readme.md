[icon]

# Chao.li

[Badges]

## Introduction - 介绍
Roku tv项目半自动化测试套件，
覆盖 HDMI  CEA-861 以及 VESA-Signals-PC 两部分测试用例
覆盖 USB Local  UI、Options、Functional-Video、Functional-Audio、Functional-Photo几部分测试用例

### Summary - 概要
基于pytest框架开发的 自动化测试工具，用于amlogic tv项目 产品线

### Features - 特性

## Requirements - 必要条件
测试环境 windows + python3.x 
测试设备 Master 8100s


## Configuration - 配置
/config/config.yaml

## Installation - 安装
pip -r install requirements.txt

## Usage - 用法
python main.py

## Development - 开发

## Changelog - 更新日志
V1.0  框架初步完成，用例验证符合预期

V1.1  调整config 配置方式，取消 config/roku/config.yaml 中的配置，统一在config/config.yaml 下配置

V1.2  添加 telnet 对不同地域 不同的标识符的适配

V2.0  完成本地播放 ui 相关用例 11 条; 调整picture 设置逻辑 

V2.1  完成本地播放相关用例53条；完成第一阶段

V2.2  完成本地播放用例 初步验收

## FAQ - 常见问题

## Support - 支持

### Dos - 文档
https://confluence.amlogic.com/pages/viewpage.action?pageId=371159583

### Contact - 联系
qq: 257912958
teams: chao.li

## Authors and acknowledgment - 贡献者和感谢
@jianhui.peng @jianfan.ai@menghui.liu

## License - 版权信息