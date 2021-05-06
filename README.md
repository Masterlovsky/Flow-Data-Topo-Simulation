# flow_data_topo_simulation
> 使用第三方库pyecharts创建节点流关系图
> pyecharts官网： https://pyecharts.org/#/

### 使用说明：

1. 将拓扑文件放入community_small.txt中，**\t**分隔。 文件格式为：源节点，目的节点，原节点所在社区，目的节点所在社区。
   
2. 将节点负载和边负载关系放入flow_data.txt中，空格分隔。文件格式为：原节点，目的节点，原节点负载，目的节点负载，边权重。
   
3. 将节点类型关系放入node_type.txt，逗号分隔，共三行，第一行为源节点集合，第二行为目的节点集合，第三行为RP节点集合，第四行为ln（叶子）节点集合。
   
4. 运行simulation_flow_graph.py 生成html文件
   
5. 在浏览器打开html文件预览

### 环境依赖：
- pyecharts 1.9.0
- numpy 1.19.2

**pyecharts源码安装(请使用本项目中的源码)**
```shell
$ cd pyecharts
$ pip install -r requirements.txt
$ python setup.py install
```


### 结果展示图样例：
![img.png](img.png)