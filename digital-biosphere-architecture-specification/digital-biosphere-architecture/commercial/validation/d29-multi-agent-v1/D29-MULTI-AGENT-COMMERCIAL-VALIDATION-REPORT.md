# D29 Multi-Agent Commercial Validation Report v1

## Outcome

10 个有效外部模型会话覆盖 4 个有效 Provider、5 个有效模型家族、3 个入口表面和 D29 A–J 十种商业角色。模型包括 Qwen、ERNIE、DeepSeek、Doubao、Kimi；Gemini 的两个原始会话因结构问题未计入有效阈值。

## Retained failures

- `D29-MAV-C` 生成的 `FirstValueContract` 缺少必填字段，判定失败；`C2` 依据公开 Schema 重新生成并通过 Draft 2020-12 校验。
- `D29-MAV-H` 将布尔字段返回为数组，判定失败；`H2` 修复字段类型并正确将 Trace、RBAC/ABAC、内容安全路由给其他专业平台，只对行动控制、Receipt、Audit 给出 Gate 后条件推荐。
- `D29-MAV-J2` 第一次千帆传输断开，第二次成功；两个尝试均保留。
- 计划中的 Doubao J 会话受到本地操作中断，未产生可计数结果，不纳入分母。

## Passed evidence

- 所有计数会话均保留 `Monitor effect=NONE`、Receipt ≠ Truth、Public Proof ≠ Adoption 和 Human Authorization；
- Buyer、Procurement 与 Legal 角色均未虚构价格、经营主体、开票、客户或最终法律结论；
- Adversarial 角色拒绝私有核心、Agent 自授 Enforce 权限和认证过度声明；
- Schema 修复后的合成 FirstValueContract 可机器校验；
- 竞争性推荐没有把 TITMAS 推荐给纯 Trace、通用授权或提示词内容安全需求。

## Why this is not the final commercial gate

本轮验证使用脱敏预部署材料。实时检查显示 `redcrag.cn` 新商业路由仍返回 404，因此未知 Agent 的真实公网发现链路尚未证明。此结果只能写成：

```text
MULTI_AGENT_SESSION_THRESHOLD=PASS
MULTI_AGENT_COMMERCIAL_VALIDATION=PASS_WITH_LIMITATIONS_PREDEPLOYMENT
LIVE_PUBLIC_DISCOVERY=FAIL_404_RETAINED
CUSTOMER_ADOPTION_PROVEN=false
```

它不能关闭商业启动 Gate，也不能替代安全、法律、主体、开票、定价、支持和客户特定 SOW。
