<template>
  <div class="summary-grid">
    <el-card class="summary-card budget" shadow="hover">
      <div class="card-title">总预算</div>
      <div class="card-value">{{ displayCurrency(summary?.total_budget) }}</div>
    </el-card>
    <el-card class="summary-card spent" shadow="hover">
      <div class="card-title">已花费</div>
      <div class="card-value">{{ displayCurrency(summary?.total_expenses ?? 0) }}</div>
    </el-card>
    <el-card class="summary-card remaining" shadow="hover">
      <div class="card-title">剩余资金</div>
      <div class="card-value">{{ displayCurrency(summary?.remaining_budget) }}</div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import type { BudgetSummaryResponse } from '@/api/budget'
defineProps<{ summary: BudgetSummaryResponse | null }>()

function displayCurrency(v: number | null | undefined) {
  if (v === null || v === undefined) return '未设置'
  try {
    return '¥' + Number(v).toFixed(2)
  } catch {
    return '¥' + v
  }
}
</script>

<style scoped>
.summary-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}
.summary-card {
  border-radius: 12px;
  border: 1px solid #edf2ed;
}
.card-title {
  color: #6b8e6b;
  font-size: 14px;
  margin-bottom: 8px;
}
.card-value {
  color: #2c3e50;
  font-size: 24px;
  font-weight: 600;
}
.summary-card.budget {
  box-shadow: 0 2px 12px rgba(143, 188, 143, 0.12);
}
.summary-card.spent {
  box-shadow: 0 2px 12px rgba(255, 140, 0, 0.12);
}
.summary-card.remaining {
  box-shadow: 0 2px 12px rgba(72, 209, 204, 0.12);
}

@media (max-width: 768px) {
  .summary-grid {
    grid-template-columns: 1fr;
  }
}
</style>