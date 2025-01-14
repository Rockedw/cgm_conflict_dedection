# -*- coding: utf-8 -*-
from graphviz import Digraph

# 创建有向图
graph = Digraph('RequirementsModel', format='png', encoding='utf-8', graph_attr={'fontname': 'Microsoft YaHei'})

# 添加节点和边
graph.node('MachineDomain', 'CTCS-3级列控系统', shape='box', color='blue')

given_domains = [
    '列车', '司机', '铁路数字移动通信系统(GSM-R)', '车载外部设备', '地面外部设备',
    '无线闭塞中心(RBC)', '无源应答器', 'TCC', '临时限速服务器', '地面电子单元(LEU)',
    '有源应答器', '轨道电路', '联锁', 'CTC', 'TSRS', '安全计算机', '应答器传输模块(BTM)',
    '无线传输模块', '人机界面(DMI)', '列车接口单元', '测速测距单元', '记录器(司法/数据记录器)',
    '轨道电路信息读取器(TCR)', '记录器下载工具'
]

for domain in given_domains:
    graph.node(domain, domain, shape='box', color='green')
    graph.edge('MachineDomain', domain)

graph.node('DesignDomain', '无', shape='box', color='orange')
graph.edge('MachineDomain', 'DesignDomain')

requirements_domains = [
    '<RBC，生成发送给列车的消息>', '<RBC，为列车提供行车许可(MA)>', '<RBC，通过GSM-R向车载设备传送MA及线路描述信息等信息>',
    '<应答器，提供上行传输链路>', '<应答器，提供消息符合要求的报文>', '<TCC，实现轨道电路编码功能>',
    '<TCC，通过LEU及有源应答器向CTCS-3级后备系统(CTCS-2级)传送临时限速信息和进路信息>',
    '<TSRS，集中管理临时限速命令>', '<TSRS，向RBC、TCC传递临时限速信息>', '<LEU，生成应答器所要传输报文的电子设备>',
    '<轨道电路，实现列车占用检查>', '<轨道电路，提供前方闭塞分区空闲信息>', '<联锁，实现对进路、信号和道岔的控制>',
    '<联锁，向列控系统提供进路信息>', '<CTC，实现所有列车的按图进路控制和列车进路控制自动化>',
    '<CTC，在操作台上下达和撤销临时限速命令>', '<安全计算机，监控列车安全运行>', '<BTM，通过应答器天线接收地面应答器的信息>',
    '<无线传输模块，通过GSM-R车载电台连接进行车-地之间双向信息传输>', '<DMI，司机与车载设备之间进行信息交互>',
    '<列车接口单元，提供安全计算机与列车相关设备之间的接口>', '<测速测距单元，接收测速传感器等设备的信号，测量列车运行速度和运行距离>',
    '<记录器，记录与列车运行安全有关的数据，并响应记录数据的下载需求>', '<TCR，接收轨道电路的信息>',
    '<记录器下载工具，对记录器数据进行下载>'
]

for req_domain in requirements_domains:
    graph.node(req_domain, req_domain, shape='box', color='purple')
    graph.edge('RequirementsDomain', req_domain)

phenomenon_sharing = [
    '<RBC，列车，生成发送给列车的消息>', '<RBC，GSM-R车载电台，通过GSM-R向车载设备传送MA及线路描述信息等信息>',
    '<应答器，车载设备，向车载设备传送报文的点式传输设备>', '<TCC，RBC，通过联锁向RBC传送轨道区段状态信息>',
    '<TCC，LEU，有源应答器，向CTCS-3级后备系统(CTCS-2级)传送临时限速信息和进路信息>',
    '<TSRS，RBC，传递临时限速信息>', '<TSRS，TCC，传递临时限速信息>', '<LEU，地面设备，生成应答器所要传输报文的电子设备>',
    '<轨道电路，列车，实现列车占用检查>', '<轨道电路，列车，提供前方闭塞分区空闲信息>',
    '<联锁，进路、信号和道岔，实现对其的控制>', '<联锁，列控系统，提供进路信息>',
    '<CTC，列车，实现按图进路控制和列车进路控制自动化>', '<CTC，操作台，下达和撤销临时限速命令>',
    '<BTM，应答器，通过应答器天线接收地面应答器的信息>', '<无线传输模块，GSM-R车载电台，进行车-地之间双向信息传输>',
    '<DMI，司机，信息交互>', '<列车接口单元，安全计算机，接口>',
    '<测速测距单元，测速传感器，测量列车运行速度和运行距离>', '<记录器，列车，记录与列车运行安全有关的数据>',
    '<TCR，轨道电路，接收轨道电路的信息>', '<记录器下载工具，记录器数据，下载>'
]

for sharing in phenomenon_sharing:
    graph.edge('PhenomenonSharing', sharing)

requirements_quotes = [
    '<RBC，生成发送给列车的消息>', '<RBC，为列车提供行车许可(MA)>', '<RBC，通过GSM-R向车载设备传送MA及线路描述信息等信息>',
    '<应答器，提供上行传输链路>', '<应答器，提供消息符合要求的报文>', '<TCC，实现轨道电路编码功能>',
    '<TCC，通过LEU及有源应答器向CTCS-3级后备系统(CTCS-2级)传送临时限速信息和进路信息>',
    '<TSRS，集中管理临时限速命令>', '<TSRS，向RBC、TCC传递临时限速信息>', '<LEU，生成应答器所要传输报文的电子设备>',
    '<轨道电路，实现列车占用检查>', '<轨道电路，提供前方闭塞分区空闲信息>', '<联锁，实现对进路、信号和道岔的控制>',
    '<联锁，向列控系统提供进路信息>', '<CTC，实现所有列车的按图进路控制和列车进路控制自动化>',
    '<CTC，在操作台上下达和撤销临时限速命令>', '<安全计算机，监控列车安全运行>', '<BTM，通过应答器天线接收地面应答器的信息>',
    '<无线传输模块，通过GSM-R车载电台连接进行车-地之间双向信息传输>', '<DMI，司机与车载设备之间进行信息交互>',
    '<列车接口单元，提供安全计算机与列车相关设备之间的接口>', '<测速测距单元，接收测速传感器等设备的信号，测量列车运行速度和运行距离>',
    '<记录器，记录与列车运行安全有关的数据，并响应记录数据的下载需求>', '<TCR，接收轨道电路的信息>',
    '<记录器下载工具，对记录器数据进行下载>'
]

for quote in requirements_quotes:
    graph.edge('RequirementsQuotes', quote)

requirements_constraints = [
    '<RBC，列车，生成发送给列车的消息>', '<RBC，为列车提供行车许可(MA)>', '<RBC，通过GSM-R向车载设备传送MA及线路描述信息等信息>',
    '<应答器，提供上行传输链路>', '<应答器，提供消息符合要求的报文>', '<TCC，实现轨道电路编码功能>',
    '<TCC，通过LEU及有源应答器向CTCS-3级后备系统(CTCS-2级)传送临时限速信息和进路信息>',
    '<TSRS，集中管理临时限速命令>', '<TSRS，向RBC、TCC传递临时限速信息>', '<LEU，生成应答器所要传输报文的电子设备>',
    '<轨道电路，实现列车占用检查>', '<轨道电路，提供前方闭塞分区空闲信息>', '<联锁，实现对进路、信号和道岔的控制>',
    '<联锁，向列控系统提供进路信息>', '<CTC，实现所有列车的按图进路控制和列车进路控制自动化>',
    '<CTC，在操作台上下达和撤销临时限速命令>', '<安全计算机，监控列车安全运行>', '<BTM，通过应答器天线接收地面应答器的信息>',
    '<无线传输模块，通过GSM-R车载电台连接进行车-地之间双向信息传输>', '<DMI，司机与车载设备之间进行信息交互>',
    '<列车接口单元，提供安全计算机与列车相关设备之间的接口>', '<测速测距单元，接收测速传感器等设备的信号，测量列车运行速度和运行距离>',
    '<记录器，记录与列车运行安全有关的数据，并响应记录数据的下载需求>', '<TCR，接收轨道电路的信息>',
    '<记录器下载工具，对记录器数据进行下载>'
]

for constraint in requirements_constraints:
    graph.edge('RequirementsConstraints', constraint)

# 渲染为png图片
graph.render('RequirementsModel', format='png', cleanup=True)
