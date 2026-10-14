# TITMAS ROI Calculator / ROI 输入计算器

本文件只定义可测输入，不提供虚假 ROI 数字。

```text
baseline_review_hours
baseline_incident_reconstruction_hours
baseline_unverified_action_count
pilot_integration_hours
pilot_operator_review_hours
pilot_receipt_verification_hours
pilot_false_block_review_hours
pilot_avoided_reconstruction_hours
approved_labor_cost_per_hour_cny
approved_pilot_fee_cny
```

候选公式：

```text
measured_time_saving = baseline_review_hours - pilot_operator_review_hours
measured_reconstruction_saving = baseline_incident_reconstruction_hours - pilot_receipt_verification_hours
gross_measured_benefit = (measured_time_saving + measured_reconstruction_saving) * approved_labor_cost_per_hour_cny
net_measured_benefit = gross_measured_benefit - approved_pilot_fee_cny - approved_internal_integration_cost
```

所有输入必须来自真实试点记录并带来源。没有基线或价格批准时：`ROI=NOT_ASSESSED`。
