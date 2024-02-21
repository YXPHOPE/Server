# 文件服务器

把你的电脑变成一个服务器，以为在相同子网内的所有终端提供如下功能：

- 文件共享和文件浏览器
- 远程桌面控制
- 远程命令行
- 远程对话

[English](Readme.md)

## 安装

安装 python，并添加到环境变量

```bash
pip install -r requirements.txt
python Server.py
```

浏览器打开 localhost:80 (默认使用端口80)，非本机终端打开 ip_address:80

## 功能

### File Browser

image

music + lrc lyric

video + subtitle

document: doc, xls, txt, html

### Remote Control

control windows system remotely

Operation supported:

- On computer: mouse, keyboard
- On mobile: one finger to click, scroll, long press to right click or drag.
