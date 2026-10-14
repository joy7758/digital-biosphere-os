# TITMAS Monitor/Enforce Demo Script / 演示脚本

场景：Coding Agent 准备执行发布或合并；只使用隔离合成仓库。

1. 展示无 Gate 的动作尝试与重建困难，不执行真实发布；
2. 用同一声明任务进入 Monitor，展示 `WOULD_BLOCK`、`ENFORCEMENT_EFFECT=NONE`、Receipt 与 Audit；
3. 用隔离 Enforce 测试展示 `BLOCK`，确认发布/合并未发生；
4. 独立验证 Receipt，明确 PASS 不等于 Fact True；
5. 导出 Audit Bundle 并重放；
6. 展示 `NOT_ASSESSED`、失败记录、撤销和已知限制；
7. 记录工具调用、延迟、复核时间和集成步骤的真实值。

禁止使用真实生产仓库、真实客户数据、有效生产凭据或对外发送。演示不构成产品可售、生产就绪或客户采用。
