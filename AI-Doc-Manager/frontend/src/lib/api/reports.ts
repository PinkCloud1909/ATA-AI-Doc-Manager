import apiClient from "./client"

export interface ReportSummary {
  total: number; draft: number; pending_review: number
  approved: number; rejected: number; expired: number
}
export interface ApprovalRate { approved: number; rejected: number; rate: number }
export interface AvgGradeByType { document_type: string; avg_grade: number; count: number }
export interface ActivityItem  { user: string; action: string; document_id: string; timestamp: string }

export const reportsApi = {
  getSummary:     async () => (await apiClient.get<ReportSummary>("/reports/summary")).data,
  getApprovalRate: async () => (await apiClient.get<ApprovalRate>("/reports/approval-rate")).data,
  getAvgGrade:    async () => (await apiClient.get<AvgGradeByType[]>("/reports/avg-grade")).data,
  getActivity:    async (limit = 20) =>
    (await apiClient.get<ActivityItem[]>("/reports/activity", { params: { limit } })).data,
}
