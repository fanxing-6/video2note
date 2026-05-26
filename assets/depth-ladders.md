# Depth Ladders

只在材料支持时启用。启用后就要真正落到正文里，不能停在分析骨架。

## 1. Optimization Layers and Bottlenecks

适用：算法、系统、Infra、产品被放在一条链上讨论时。

最低输出：

- 分层结构
- 层间反馈或约束关系
- 一张机制图或决策图

理想形式化：

- 目标函数、瓶颈方程，或“上层目标如何被下层约束改变”的变量化描述

## 2. Role / Career / Decision Economics

适用：岗位选择、方向下注、路径比较。

最低输出：

- 收益来源
- 进入门槛或竞争池
- 反馈速度
- 技术复利或可迁移性
- 对读者的选择建议

理想形式化：

- 一个简单的期望收益、风险回报或决策评分模型

## 3. RL / Post-training

适用：强化学习、GRPO、reward model、后训练。

最低输出：

- 目标是什么
- reward 来自哪里
- 哪一步最容易失效
- 短期机会与长期限制

理想形式化：

- 一个奖励函数、目标函数或 calibration 关系式

## 4. API vs Self-model Economics

适用：直接调用现成模型、微调、训练细分模型、推理成本比较。

最低输出：

- 成本变量有哪些
- 哪些约束会让 API 路线失效
- 何时值得切到细分模型

理想形式化：

- 一个服务成本或盈亏平衡模型

## 5. Multi-agent / Pipeline Optimization

适用：多 Agent、供应链类流程、串并行管线、端到端 bottleneck。

最低输出：

- 阶段分解
- handoff / retry / bottleneck 位置
- 调优杠杆

理想形式化：

- 端到端时延、吞吐或错误传播分解式

## 6. Data Center / Hardware / Power Constraints

适用：GPU 数据中心、供电、冷却、芯片、容量规划。

最低输出：

- 供电、冷却、网络、容量至少四项中的三项
- 说明为什么这不是“简单运维”
- 给出组织或采购层面的约束

理想形式化：

- PUE、容量预算或机房扩容约束模型

## 7. Industry AI Adoption

适用：传统行业 AI 化、垂直数据、行业渗透、产品转型。

最低输出：

- 工作流插入点
- 采用摩擦
- 数据或 domain knowledge 的作用
- 为什么这一波比以前更容易扩散

理想形式化：

- 一个“数据、工作流、采用成本、价值回收”之间的关系模型
