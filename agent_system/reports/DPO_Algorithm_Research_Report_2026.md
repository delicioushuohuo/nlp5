# DPO算法2024-2026年最新进展研究报告

# DPO（Direct Preference Optimization）算法最新进展研究报告

## 一、研究背景

Direct Preference Optimization（DPO）是一种用于大语言模型（LLM）偏好对齐的直接优化方法，由Rafailov等人于2023年提出。相比传统的基于人类反馈的强化学习（RLHF），DPO具有实现简单、训练稳定、无需奖励模型等优点，因此在LLM对齐研究中得到了广泛应用。

近年来，研究者们从多个维度对DPO进行了改进和扩展，包括令牌级别的细粒度优化、多目标偏好对齐、约束控制优化、在线迭代学习等。本报告综述了2024-2025年间DPO算法的重要研究进展。

---

## 二、主要研究进展

### 2.1 TIS-DPO：令牌级重要性采样

**论文信息**：
- 标题：TIS-DPO: Token-level Importance Sampling for Direct Preference Optimization With Estimated Weights
- 作者：Aiwei Liu, Haoping Bai, Zhiyun Lu等
- 发表时间：2024年10月

**核心思想**：
传统DPO将整个响应作为单一决策臂进行优化，未考虑不同令牌之间的重要性差异。TIS-DPO提出，最优的DPO训练数据中，获胜响应和失败响应中每个令牌的期望奖励应该相等，即令牌重要性无差异。然而实际中最优数据集不可得，因此该研究提出使用原始数据集进行重要性采样以实现无偏优化。

**方法要点**：
1. 为每个令牌分配基于其奖励的重要性权重
2. 使用对比LLM预测概率的差异来估计令牌重要性权重
3. 探索了三种构建对比LLM的方法：
   - 使用对比提示引导原始LLM
   - 使用获胜/失败响应训练两个独立的LLM
   - 使用获胜/失败响应进行正向和反向DPO训练

**实验结果**：
在无害性和有用性对齐以及摘要任务上，TIS-DPO显著优于各种基线方法。研究者还可视化了估计权重，证明了其识别关键令牌位置的能力。

---

### 2.2 Uni-DPO：动态偏好优化的统一范式

**论文信息**：
- 标题：Uni-DPO: A Unified Paradigm for Dynamic Preference Optimization of LLMs
- 作者：Shangpin Peng, Weinong Wang, Zhuotao Tian等
- 发表时间：2025年6月（最新）

**核心思想**：
现有DPO方法通常平等对待所有偏好对，忽略了数据质量和学习难度的显著差异，导致数据利用效率低下和性能次优。Uni-DPO提出一个统一框架，同时考虑：(a) 偏好对的内在质量，(b) 模型在训练过程中的 evolving performance。

**方法要点**：
1. 基于两个因素自适应地对样本进行重加权
2. 使偏好数据利用更加有效
3. 实现卓越性能

**实验结果**：
1. 在文本任务上，使用Uni-DPO微调的Gemma-2-9B-IT在Arena-Hard上超越Claude 3 Opus达6.7分
2. 在数学和多模态任务上，Uni-DPO在所有基准测试中始终优于基线方法
3. 提供了其有效性和泛化能力的强有力实证证据

---

### 2.3 Step-DPO：长链推理的逐步偏好优化

**论文信息**：
- 标题：Step-DPO: Step-wise Preference Optimization for Long-chain Reasoning of LLMs
- 作者：Xin Lai, Zhuotao Tian, Yukang Chen等
- 发表时间：2024年6月

**核心思想**：
数学推理需要精确且广泛的多步推理链，确保每步推理的正确性至关重要。然而DPO对长链数学推理的提升有限，因为使用DPO的模型难以识别错误答案中的详细错误。这种局限性源于缺乏细粒度的过程监督。

**方法要点**：
1. 将单个推理步骤作为偏好优化的单元，而非整体评估答案
2. 开发了Step-DPO的数据构建流程，创建包含10K个逐步偏好对的高质量数据集
3. 发现自生成数据比人类或GPT-4生成的数据更有效，因为后者具有分布外特性

**实验结果**：
1. 仅使用10K个偏好数据对和少于500步的Step-DPO训练，就能在超过70B参数的模型上实现近3%的精度提升
2. Qwen2-72B-Instruct应用Step-DPO后，在MATH测试集上达到70.8%，在GSM8K上达到94.0%
3. 超越了一系列闭源模型，包括GPT-4-1106、Claude-3-Opus和Gemini-1.5-Pro

---

### 2.4 C2-DPO：约束控制的直接偏好优化

**论文信息**：
- 标题：C2-DPO: Constrained Controlled Direct Preference Optimization
- 作者：Kavosh Asadi, Julien Han, Idan Pipano等
- 发表时间：2025年2月

**核心思想**：
该研究对DPO进行了两个反直觉的观察：
1. DPO损失可以从一个替代优化问题推导，该问题仅在样本内响应上定义KL约束，而非原始RLHF问题中在整个分布上定义约束
2. 证明了该替代优化问题的一个惊人特性：在其最优策略下，偏好和被拒绝的响应都会降低概率——这是DPO在实际中表现出的典型现象

**方法要点**：
1. 提出一组约束来限制参考策略和目标策略之间偏好和被拒绝响应的概率质量位移
2. 结果算法称为Constrained Controlled DPO (C2-DPO)，具有有意义的RLHF解释
3. 通过对冲位移，C2-DPO在用标准偏好数据集对齐多个语言模型时提供了实际改进

---

### 2.5 基于理由的数据中心人类偏好方法

**论文信息**：
- 标题：Data-Centric Human Preference with Rationales for Direct Preference Alignment
- 作者：Hoang Anh Just, Ming Jin, Anit Sahu等
- 发表时间：2024年7月

**核心思想**：
标准偏好数据集通常缺乏关于为什么做出特定选择的信息，这种模糊性可能阻碍高效学习和稳健对齐。现有研究多关注算法改进，该研究采用数据中心视角，探讨如何增强从现有偏好数据中学习。

**方法要点**：
1. 提出用解释人类偏好推理的理由来增强标准偏好对
2. 引入一个简单且有原则的框架，利用机器生成的理由来丰富偏好数据
3. 该方法兼容各种直接偏好优化算法

**实验结果**：
1. 加入理由可加速收敛并实现更高的最终模型性能
2. 展示了数据设计的潜力——用解释性理由丰富现有数据集可帮助解锁模型对齐和注释效率的改进

---

### 2.6 基于DPO隐式奖励差距的难度偏好数据选择

**论文信息**：
- 标题：Difficulty-Based Preference Data Selection by DPO Implicit Reward Gap
- 作者：Xuan Qi, Rongwu Xu, Zhijing Jin
- 发表时间：2025年8月

**核心思想**：
对齐LLM的方法如RLHF和DPO通常依赖大型昂贵的偏好数据集。目前缺乏针对偏好数据高质量选择的方法。该研究引入了一种基于DPO隐式奖励机制的难度数据选择策略。

**方法要点**：
1. 选择具有较小DPO隐式奖励差距的偏好数据示例，这表明更具挑战性的情况
2. 提高数据效率并改善模型对齐

**实验结果**：
1. 在多个数据集和比对任务上始终优于五个强基线
2. 仅使用原始数据的10%就实现了卓越性能
3. 提供了一种有原则的高效选择方法，为有限资源下扩展LLM对齐提供了有前景的解决方案

---

### 2.7 MIA-DPO：多图像增强的直接偏好优化

**论文信息**：
- 标题：MIA-DPO: Multi-Image Augmented Direct Preference Optimization For Large Vision-Language Models
- 作者：Ziyu Liu, Yuhang Zang, Xiaoyi Dong等
- 发表时间：2024年10月

**核心思想**：
视觉偏好对齐涉及训练大型视觉语言模型（LVLM）来预测人类对视觉输入的偏好。现有视觉对齐方法主要设计用于单图像场景，难以有效处理多图像任务的复杂性，原因包括训练数据多样性的缺乏和注释偏好对的高成本。

**方法要点**：
1. 通过扩展单图像数据与不相关图像（网格拼贴或画中画格式）来缓解多图像训练数据稀缺问题
2. 显著降低多图像数据注释的成本
3. 利用LVLM在不同图像上的注意力值显著变化的观察结果
4. 使用注意力值来识别和过滤掉模型可能错误关注的被拒绝响应

**实验结果**：
1. 在五个多图像基准测试中优于现有方法
2. 在LLaVA-v1.5上实现平均3.0%的性能提升，在InternLM-XC2.5上实现4.3%的提升
3. 对模型理解单图像的能力影响极小

---

### 2.8 MO-ODPO：多目标在线DPO

**论文信息**：
- 标题：Robust Multi-Objective Preference Alignment with Online DPO
- 作者：Raghav Gupta, Ryan Sullivan, Yunxuan Li等
- 发表时间：2025年3月

**核心思想**：
多目标偏好对齐对于开发更可配置、个性化、有帮助且安全的AI系统至关重要。然而，在推理时使用可变权重优化模型输出以实现真正个性化的模型是一项重大挑战。现有方法要么计算成本昂贵，要么不能充分引导模型行为。

**方法要点**：
1. 引入多目标在线DPO (MO-ODPO) 算法
2. 结合提示条件机制，允许训练单一偏好条件策略
3. 可在推理时适应新的偏好组合

**实验结果**：
1. 在两个流行基准测试中，MO-ODPO Pareto支配现有基线
2. 在不同目标之间提供优秀的推理时可 steering 性

---

### 2.9 DPO在特定领域的应用

**论文信息**：
- 标题：BITS Pilani at SemEval-2026 Task 9: Structured Supervised Fine-Tuning with DPO Refinement for Polarization Detection
- 发表时间：2026年4月

**应用场景**：
将DPO应用于政治 polarization 检测任务，采用两阶段方法：
1. 使用LoRA对Qwen 2.5-7B-Instruct进行结构化监督微调，使用可解释的槽填充模板
2. 应用DPO与自动生成的偏好对来减少昂贵的假阴性

**实验结果**：
1. 在英语开发集上，DPO将召回率从0.5085提高到0.7797
2. macro-F1提升约5个点

---

## 三、研究趋势分析

### 3.1 细粒度优化
研究表明，将优化粒度从序列级别细化到令牌级别或推理步骤级别，可以显著提升模型性能。Step-DPO和TIS-DPO分别从这两个方向进行了探索。

### 3.2 动态数据选择
Uni-DPO和基于难度的数据选择方法表明，自适应地根据数据质量和模型学习状态对样本进行重加权，可以提高数据利用效率。

### 3.3 多模态扩展
MIA-DPO等研究将DPO扩展到视觉-语言模型领域，处理多图像输入场景。

### 3.4 约束与控制
C2-DPO等研究引入了约束机制来控制模型行为的稳定性，避免过度优化。

### 3.5 数据增强
通过添加理由（rationales）来丰富偏好数据，可以加速收敛并提升最终性能。

---

## 四、未来研究方向

1. **理论分析**：更深入地理解DPO的理论性质，包括收敛性、稳定性和最优性条件
2. **高效算法**：开发计算成本更低、数据效率更高的DPO变体
3. **多模态融合**：扩展DPO到更多模态（音频、视频等）
4. **在线学习**：更好地结合在线学习范式，提升模型持续改进能力
5. **安全性与对齐**：探索DPO在AI安全和价值对齐中的更广泛应用

---

## 五、结论

DPO作为一种简洁有效的LLM对齐方法，近年来在多个方向取得了重要进展。这些进展包括细粒度令牌级和步骤级优化、动态数据选择策略、多模态扩展、约束控制机制以及数据增强技术。这些研究为构建更安全、更有效的大语言模型提供了重要的技术支持。

---

## 参考文献

1. Liu et al. "TIS-DPO: Token-level Importance Sampling for Direct Preference Optimization With Estimated Weights" (2024)
2. Peng et al. "Uni-DPO: A Unified Paradigm for Dynamic Preference Optimization of LLMs" (2025)
3. Lai et al. "Step-DPO: Step-wise Preference Optimization for Long-chain Reasoning of LLMs" (2024)
4. Asadi et al. "C2-DPO: Constrained Controlled Direct Preference Optimization" (2025)
5. Just et al. "Data-Centric Human Preference with Rationales for Direct Preference Alignment" (2024)
6. Qi et al. "Difficulty-Based Preference Data Selection by DPO Implicit Reward Gap" (2025)
7. Liu et al. "MIA-DPO: Multi-Image Augmented Direct Preference Optimization For Large Vision-Language Models" (2024)
8. Gupta et al. "Robust Multi-Objective Preference Alignment with Online DPO" (2025)
9. Gupta et al. "BITS Pilani at SemEval-2026 Task 9" (2026)