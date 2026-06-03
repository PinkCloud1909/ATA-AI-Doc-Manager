"use client"

import { useQuery } from "@tanstack/react-query"
import { reportsApi } from "@/lib/api/reports"

export default function ReportsPage() {
  const { data: summary }  = useQuery({ queryKey: ["reports", "summary"],       queryFn: reportsApi.getSummary })
  const { data: approval } = useQuery({ queryKey: ["reports", "approval-rate"], queryFn: reportsApi.getApprovalRate })
  const { data: grades }   = useQuery({ queryKey: ["reports", "avg-grade"],     queryFn: reportsApi.getAvgGrade })
  const { data: activity } = useQuery({ queryKey: ["reports", "activity"],      queryFn: () => reportsApi.getActivity(20) })

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-slate-800">Báo cáo</h1>
        <p className="text-sm text-slate-500 mt-0.5">Thống kê hệ thống tài liệu</p>
      </div>

      {/* Summary + Approval rate */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
        {/* Status breakdown */}
        <div className="lg:col-span-2 bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">Phân bố trạng thái</h2>
          {summary && (
            <div className="space-y-3">
              {[
                { label: "Đã duyệt",  value: summary.approved,       max: summary.total, color: "bg-emerald-500" },
                { label: "Chờ duyệt", value: summary.pending_review,  max: summary.total, color: "bg-amber-400" },
                { label: "Từ chối",   value: summary.rejected,        max: summary.total, color: "bg-red-400" },
                { label: "Nháp",      value: summary.draft,           max: summary.total, color: "bg-slate-300" },
                { label: "Hết hạn",   value: summary.expired,         max: summary.total, color: "bg-slate-200" },
              ].map((row) => (
                <div key={row.label} className="space-y-1">
                  <div className="flex justify-between text-sm">
                    <span className="text-slate-600">{row.label}</span>
                    <span className="font-medium text-slate-800">{row.value}</span>
                  </div>
                  <div className="w-full bg-slate-100 rounded-full h-2 overflow-hidden">
                    <div
                      className={`${row.color} h-2 rounded-full transition-all duration-500`}
                      style={{ width: row.max ? `${(row.value / row.max) * 100}%` : "0%" }}
                    />
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Approval rate */}
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5 space-y-4">
          <h2 className="text-sm font-semibold text-slate-700">Tỉ lệ phê duyệt</h2>
          {approval && (
            <>
              <div className="text-center py-4">
                <p className="text-5xl font-bold text-emerald-600">
                  {(approval.rate * 100).toFixed(0)}%
                </p>
                <p className="text-xs text-slate-400 mt-1">được phê duyệt</p>
              </div>
              <div className="grid grid-cols-2 gap-3 text-sm text-center">
                <div className="bg-emerald-50 rounded-lg p-3">
                  <p className="font-bold text-emerald-700 text-xl">{approval.approved}</p>
                  <p className="text-emerald-600 text-xs">Chấp thuận</p>
                </div>
                <div className="bg-red-50 rounded-lg p-3">
                  <p className="font-bold text-red-600 text-xl">{approval.rejected}</p>
                  <p className="text-red-500 text-xs">Từ chối</p>
                </div>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Avg grade by type */}
      {grades && grades.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm p-5">
          <h2 className="text-sm font-semibold text-slate-700 mb-4">
            Điểm chất lượng trung bình theo loại tài liệu
          </h2>
          <div className="flex gap-6 flex-wrap">
            {grades.map((g) => (
              <div key={g.document_type} className="text-center">
                <p className={`text-3xl font-bold ${
                  g.avg_grade >= 7 ? "text-emerald-600" :
                  g.avg_grade >= 5 ? "text-amber-500" : "text-red-500"
                }`}>
                  {g.avg_grade.toFixed(1)}
                </p>
                <p className="text-xs text-slate-500 mt-0.5">{g.document_type}</p>
                <p className="text-xs text-slate-400">{g.count} đánh giá</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity log */}
      {activity && activity.length > 0 && (
        <div className="bg-white rounded-xl border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-100 bg-slate-50/50">
            <h2 className="text-sm font-semibold text-slate-700">Nhật ký hoạt động</h2>
          </div>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-slate-100 text-left bg-slate-50/30">
                <th className="px-5 py-2.5 text-xs font-semibold text-slate-500">Người dùng</th>
                <th className="px-5 py-2.5 text-xs font-semibold text-slate-500">Hành động</th>
                <th className="px-5 py-2.5 text-xs font-semibold text-slate-500">Thời gian</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-50">
              {activity.map((item, i) => (
                <tr key={i} className="hover:bg-slate-50 transition-colors">
                  <td className="px-5 py-3 font-medium text-slate-700">{item.user}</td>
                  <td className="px-5 py-3 text-slate-500">{item.action}</td>
                  <td className="px-5 py-3 text-slate-400">
                    {new Date(item.timestamp).toLocaleString("vi-VN")}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
