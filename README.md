# proxyPool
自建代理池



- cmd.py
    - 命令行工具

- settings.py
    - 项目配置
  
- proxyPool.py
    - 代理池控制（redis 有序集合）

- vpsClient.py
    - vps拨号客户端

- server.py
    - web服务

- schedule.py
  - 任务调度，以及拨号策略


**版本 0.1.0**

- **功能**
- vps使用tinyproxy进行拨号
- 代理池以redis的有序列表维护
- 两种模式拨号：定时拨号，次数拨号；拨号任务均采用协程并发完成
- 接口是使用fastapi实现，默认使用过次数少的ip


- **可优化**
- 拨号流程代码可优化
- 项目配置及各类初始化参数优化
- 异常处理
- 封装为库