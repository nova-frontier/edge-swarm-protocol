# L2 · 香农港 / Port Shannon

**先说明通信条件，再讨论群体协作。**

GROUNDSTATE 的受限通信节点，关注带宽、时延、丢包和短时中断下的信息交换。

当前状态：**v0.1 合成信道探针**。提供可复现的离散事件模拟；未实现智能体决策、共识算法、无线电物理模型或真实机器人组网。

## 先运行

Python 3.11+，仅标准库。

```bash
python channel_sim.py --nodes 3 --rounds 5 --seed 7
python channel_sim.py --nodes 4 --loss 0.2 --latency-ms 100 --jitter-ms 30 --bandwidth-bps 10000 --blackout 300 600 --seed 7
python -m unittest discover -s tests -v
```

第一条命令调度 30 次点对点发送。所有默认消息均能在观察期限内到达。输出逐事件记录与交付统计；这只说明该合成设定下的信道行为。

## 模型与口径

每轮每个节点向其他节点发包；每个发送端共享一个串行上行队列。传输耗时为 `payload_bytes × 8 / bandwidth_bps`。随后叠加固定延迟和 `[0, jitter_ms]` 均匀抖动，按随机种子应用独立丢包。没有重传、路由、接收端竞争、协议头或策略学习。

中断窗口只检查发送开始或到达时间是否落在 `[start, end)`；不模拟整段传输与中断的重叠。`late` 指到达时间超过 `horizon_ms`。`bytes_scheduled` 为全部调度消息的载荷字节数，包含丢失和超时消息，不代表观察期内实际链路吞吐。平均延迟只统计按期到达的消息。

[实验矩阵](protocols/channel-matrix.md) 区分理想、受限、中断三种条件。比较时必须报告完整参数、种子与失败口径；消息交付率不能替代任务成功率或协作收敛性。

下一步：策略适配、序列号与重复处理、任务指标和硬件链路回放。均待实现。

[总纲](https://github.com/nova-frontier/manifesto) · [提出问题](https://github.com/nova-frontier/edge-swarm-protocol/issues) · [贡献](CONTRIBUTING.md) · [MIT](LICENSE)
