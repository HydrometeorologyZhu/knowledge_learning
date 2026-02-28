# 植被极端生长与全球气候极端事件关联性分析

## 1. 目的与方法论

### 研究目的
- 植被极端生长归因分析
- 探究植被极端生长与全球气候极端事件的联系

### 分析方法
- **事件巧合分析**：识别植被极端生长与气候极端事件在时空上的对应关系
- **敏感性分析**：量化不同类型植被对各类气候极端事件的响应程度

### 核心指标
三个植被指标：SIF、NDVI、LAI

## 2. 数据与数据处理

### 2.1 数据概述

| 数据名称 | 数据来源 | 时间分辨率 | 空间分辨率 |
|---------|---------|-----------|-----------|
| SIF | GOSIF | 8天，2000-2024 | 0.05° |
| NDVI | MODIS/Terra Vegetation Indices | 16天，2000.2.18-今 | 0.05° |
| LAI | MODIS/Terra Leaf Area Index | 8天，2000.2.18-今 | 500m |
| 气象数据 | TerraClimate | 月，2000-2024 | 1/24° |
| 植被生长周期 | 根据NDVI划定 | / | / |
| 土地覆盖/利用数据 | MODIS/Terra+Aqua Land Cover Type | 年，2001-今 | 0.05° |

### 数据链接
- **SIF**: https://globalecology.unh.edu/data/GOSIF.html
- **NDVI**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod13c2-061
- **LAI**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mod15a2h-061
- **气象数据**: https://www.climatologylab.org/terraclimate.html
  - Maximum temperature (MaxT)
  - Minimum temperature (MinT)
  - Precipitation (P)
  - Potential evapotranspiration (PET)
- **植被生长周期**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd12q2-061
- **土地覆盖**: https://www.earthdata.nasa.gov/data/catalog/lpcloud-mcd12c1-061

# 2.2 数据预处理

**时间尺度统一设定为：2000–2024 年**  
**空间分辨率统一为：0.05°（最终所有数据统一至 0.25°）**

---

# 2.2.1 NDVI 数据处理

## （1）数据提取与聚合

### 数据来源
MODIS CMG 0.05° 16-day NDVI 产品

### 提取变量
- `MODIS_Grid_16Day_VI_CMG:"CMG 0.05 Deg 16 days NDVI"`
- `MODIS_Grid_16Day_VI_CMG:"CMG 0.05 Deg 16 days NDVI std dev"`

### 时间范围
2000年至今

### 输出格式
合并为一个长期序列的 `.nc` 文件

### 实现方式
使用自编译程序：

```python
extract_data2nc.py
```

---

## （2）数据平滑处理

### 方法
HANTS（Harmonic Analysis of NDVI Time-Series）

### 生长季提取方法
基于 EDVI 上升速率与下降速率识别生长季。

---

# 2.2.2 气象数据处理

## （1）趋势处理策略

同时进行两种处理：

1. 保留原始数据
2. 去趋势数据（最小二乘法）

### 去趋势方法
最小二乘法（Linear Least Squares）

### 科学判断逻辑

- 若去趋势与未去趋势结果一致 → 结论稳健可靠
- 若存在差异 → 需要深入分析长期趋势与短期波动的相对贡献  
  → 该差异本身可能具有重要科学意义

---

## （2）极端事件定义

### 判定标准
大于或小于年际变化的 **1 个标准差（1σ）**

说明：
- 1.5σ、2.0σ 事件过少，不采用

### 时间尺度
按年统计

### 判定范围
仅在生长季（SOS–EOS）期间判断

示例：
- 若 2001 年生长季为 DOY 100–240  
- 仅在 100–240 范围内判断是否为极端气候事件

---

# 3 气象数据预处理流程

## 原始数据说明

文件命名格式：

```text
TerraClimate_tmax_YYYY.nc
```

其中：
- `YYYY` 为年份
- `tmax` 为变量（最大温度）

### nc 文件变量
- `crs`
- `lon`
- `lat`
- `tmax`
- `time`（格式：YYYY-MM-DD）

### 原始分辨率
- 纬度大小：4320
- 经度大小：8640
- 分辨率：1/24°

---

## 处理目标

### （1）重采样

- 重采样至 0.25°
- 网格与 GPP 文件一致
- 方法：Bilinear interpolation

---

### （2）掩膜处理

- 若 GPP 文件中该像元为 NaN
- 气象变量对应像元赋值为 NaN

---

### （3）时间格式转换

- 原格式：YYYY-MM-DD
- 转换为：DOY（年内第几天）

---

### （4）函数接口

```python
def process_climate(
    input_GPP_file_nc,
    input_climate_file,
    output_climate_file
):
    """
    1. 重采样至0.25°
    2. 应用GPP掩膜
    3. 时间转换为DOY
    4. 输出nc文件
    """
    pass
```

---

## 输出文件格式

```text
TerraClimate_变量_detrend_YYYY_0.25deg.nc
```

### 变量包括
- lon
- lat
- time（DOY）
- 变量名

---

# 4 生长季文件结构

文件名：

```text
Phenology_YYYY.nc
```

### 公共变量
- lon
- lat

### 生长季变量
- SOS1
- EOS1
- DOS1
- SOS2
- EOS2
- DOS2

---

## 规则说明

### 单峰生长
- SOS2、EOS2、DOS2 全为 NaN

### 双峰生长
- 两组均有值

### 时间格式
- DOY 格式
- 允许：
  - 负值（表示距本年前 n 天）
  - >365（表示距本年后 n−365 天）

---

# 5 极端气象事件识别

## 输入函数

```python
def detect_extreme_events(
    phenology_file,
    detrended_climate_file,
    output_file,
    threshold_type,   # "greater" 或 "less"
    variable_name
):
    """
    1. 读取SOS-EOS
    2. 提取生长季气候变量
    3. 计算年际标准差
    4. 判断 >1σ 或 < -1σ
    5. 统计极端事件次数
    """
    pass
```

---

## 输出文件变量

- lat
- lon
- event_counts

表示每个像元在生长季期间的极端事件个数。

---

# 6 性能优化方案

- 使用 `@njit` 加速
- 并行计算
- 共享内存
- 纬度分块计算
- 显示进度条
- 优化内存占用

---

# 7 GPP 数据预处理

## （1）无效值剔除

对于每个像元：

- 若整个时间序列最大值 < 2.0  
→ 判定为裸地或无植被区域  
→ 剔除

---

## （2）重采样

- 方法：Bilinear
- 分辨率统一至 0.25°

---

## （3）插值

- 方法：PCHIP
- 构建 2000–2024 年逐日连续数据

---

## （4）Savitzky-Golay 平滑

逐年进行平滑处理。

---

## （5）Grubbs 迭代异常值剔除

### 处理步骤

1. 计算平滑 GPP
2. 计算比值：平滑GPP / 原始GPP
3. 若比值 > 平均比值的标准差 → 判为异常
4. 用平滑值替换异常值
5. 继续迭代

### 终止条件

- 达到 20 次迭代
- 或无异常值

---

## （6）年末过平滑修正

由于 Savitzky-Golay 会导致年末过平滑：

- 对 DOY 330 – 次年 30
- 使用小窗口再平滑
- 替换原过平滑数据

---

# 8 生长季识别方法（全球尺度）

## 窗口构建

窗口年 = 本年 ± 半年  
解决南半球跨年生长问题。

---

## （1）基点与峰值识别

方法：PELT

- 基点 → 峰值 → 下一个基点
- 上升段为生长期

---

## （2）伪峰剔除

- 基于振幅阈值筛选

---

## （3）SOS / EOS 判定

采用 10% 振幅阈值法：

- SOS：上升至振幅10%位置
- EOS：下降至振幅10%位置

---

# 9 生长类型划分

| 类型 | 说明 |
|------|------|
| 单峰 | 一个生长期 |
| 双峰 | 两个显著生长期 |
| 常年生长 | 直接设定 SOS=1，EOS=365 |

---

# 10 植被类型重分类

| 新类别 | 包含原始类别 | 生态含义 |
|--------|-------------|----------|
| Evergreen forests | 1 + 2 | 常绿林（高稳定GPP，对水分更敏感） |
| Deciduous forests | 3 + 4 | 落叶林（强季节性，对温度极端更敏感） |
| Mixed forests | 5 | 混交林（过渡响应） |
| Shrublands | 6 + 7 | 灌丛（半干旱水分限制明显） |
| Savannas & woody grass systems | 8 + 9 | 稀树草原（强水热耦合系统） |
| Grasslands | 10 | 草地（对干旱与热浪极端高度敏感） |
| Wetlands | 11 | 湿地（能量限制 + 水文控制） |

---