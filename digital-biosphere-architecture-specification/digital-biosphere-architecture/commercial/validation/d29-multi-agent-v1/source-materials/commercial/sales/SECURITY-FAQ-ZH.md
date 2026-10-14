# TITMAS 安全 FAQ

## Receipt 证明安全吗？

不证明。Receipt 证明声明的技术记录和绑定关系可被核验，不证明事实、结果、合法性或绝对安全。

## Monitor 会阻断吗？

不会。`MODE=MONITOR`、`ENFORCEMENT_EFFECT=NONE`。

## 客户原始数据会上传吗？

默认不上传。首个验证使用合成数据；任何客户元数据都需最小化、分类和书面批准。

## 是否开放核心源码？

否。开发者默认获得标准、机器接口、SDK、Sandbox 和受限凭据，不获得私有 Gate/Receipt/Audit 核心。

## 是否已通过独立安全审计？

没有。当前仍有一个 Critical finding 未关闭，独立安全评价仅处于准备状态。

## 是否生产就绪？

否。`PRODUCTION_READY=false`。
