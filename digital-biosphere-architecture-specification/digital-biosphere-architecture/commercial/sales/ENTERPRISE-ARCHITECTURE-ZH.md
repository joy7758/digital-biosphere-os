# TITMAS 企业私有部署架构草案

## 平面划分

- **Customer Data Plane**：原始内容、动作系统、本地策略缓存、本地密钥/KMS 和可选本地 Receipt；
- **TITMAS Private Platform Plane**：Workspace、Agent Registry、Gate、Receipt、Verification、Audit、Usage；
- **Management Plane**：人工开通、配置、版本、支持和部署记录。

候选部署包括中国受控私有试点、客户 VPC、本地部署和未来隔离环境。当前仅有架构和参考实现证据，不存在已批准年度 SLA、生产部署或客户采用。

不得新增第二套身份、证据、策略、回执、审计、租户或密钥核心。
