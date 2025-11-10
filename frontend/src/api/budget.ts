import request from './request'

export interface ExpenseResponse {
  id: number
  trip_id: number
  amount: number
  category: string
  description?: string | null
  expense_date: string
  created_at: string
}

export interface BudgetSummaryResponse {
  trip_id: number
  total_budget: number | null
  total_expenses: number
  remaining_budget: number | null
}

export interface ExpenseCreatePayload {
  trip_id: number
  amount: number
  category: 'transport' | 'accommodation' | 'food' | 'entertainment' | 'shopping' | 'other'
  description?: string
  expense_date: string // YYYY-MM-DD
}

export function addExpense(payload: ExpenseCreatePayload) {
  return request.post<ExpenseResponse>('/api/budget/add', payload)
}

export function getExpenses(tripId: number) {
  return request.get<ExpenseResponse[]>('/api/budget/list', { params: { trip_id: tripId } })
}

export function getBudgetSummary(tripId: number) {
  return request.get<BudgetSummaryResponse>('/api/budget/summary', { params: { trip_id: tripId } })
}