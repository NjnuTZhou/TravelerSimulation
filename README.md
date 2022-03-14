# TravelerSimulation
  毕业论文模拟程序源码（基于路径选择模式的景区游客空间行为模拟研究）
## 1.coord_transform.py
  坐标转换：wgs84、bd、gcj02互转
## 2.file_operation.py
  文件操作：json文件写入与读取、csv写入与读取
## 3.GeoUtils.py
  地理操作：距离计算，路径id计算
## 4.simulation.py
  基于效用概率路径选择方式的模拟
## 5.simulation_maxU
  基于最大效用路径选择方式的模拟
## 6.simulation_params2.json
  模拟程序所用的初始参数，包括路网拓扑、出入口节点、景点信息、提前计算好的效用解释变量
# 依赖库
  pip install geopy\n
  pip install tqdm
# 使用方式
  1.下载源码之后，创建以下目录
    simulation.py：simulationData/simulation_traveler_distribution\n
    simulation_maxU.py：simulationData_maxU/simulation_traveler_distribution
  2.运行程序
    python simulation.py
    python simulation_maxU
# 注意！！！
  1.程序运行比较吃电脑性能，模拟一次需约2~3小时，一次请只运行一个模拟进程。\n
  2.程序入口函数为main()
  
    ```
    def main():
      simulation_params = SimulationParams(fo.open_json_file('simulation_params_2.json'))
      get_path_length(simulation_params)

      base_params = BaseParams(0)
      print('------simulating workday...')
      simulation(base_params, simulation_params)

      base_params1 = BaseParams(1)
      print('------simulating holiday...')
      simulation(base_params1, simulation_params)
    ```
    
    main函数中包括两个模拟，分别为工作日(0)和节假日(1)，如果只模拟一个，将另外一个注释即可
# 输出结果解释
  1.simulationData/timeData*.json：模拟结果的时间序列，表示景区内人数随时间变化的趋势\n
  2.simulationData/simulationData*.json：模拟的每个游客的轨迹序列及其他参数\n
  :grinning:*值为0或1，表示该结果属于工作日还是节假日\n
  3.simulation_traveler.distribution/*_#.geojson：景区内游客的空间分布数据，坐标系为wgs84\n
  :grinning:*值为0或1，表示该结果属于工作日还是节假日；#值为≥1，表示时间点\n
  
      
