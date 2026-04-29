export default function DocumentStats() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="bg-blue-50/50 p-6 rounded-2xl border border-blue-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-blue-100 flex items-center justify-center text-blue-600">
          <span
            className="material-symbols-outlined"
            style={{ fontVariationSettings: '"FILL" 1' }}
          >
            analytics
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-blue-900">Điểm trung bình</h4>
          <p className="text-2xl font-black text-blue-700">8.2 / 10</p>
        </div>
      </div>
      <div className="bg-green-50/50 p-6 rounded-2xl border border-green-100 flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-green-100 flex items-center justify-center text-green-600">
          <span
            className="material-symbols-outlined"
            style={{ fontVariationSettings: '"FILL" 1' }}
          >
            task_alt
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-green-900">Đã kiểm duyệt</h4>
          <p className="text-2xl font-black text-green-700">
            18{" "}
            <span className="text-xs font-medium text-green-600/70">
              tài liệu
            </span>
          </p>
        </div>
      </div>
      <div className="bg-surface-container-low p-6 rounded-2xl border border-transparent flex items-center gap-4">
        <div className="w-12 h-12 rounded-xl bg-surface-container-high flex items-center justify-center text-on-surface-variant">
          <span
            className="material-symbols-outlined"
            style={{ fontVariationSettings: '"FILL" 1' }}
          >
            history
          </span>
        </div>
        <div>
          <h4 className="text-sm font-bold text-on-surface">
            Cập nhật tháng này
          </h4>
          <p className="text-2xl font-black text-on-surface">
            142{" "}
            <span className="text-xs font-medium text-on-surface-variant/70">
              lần
            </span>
          </p>
        </div>
      </div>
    </div>
  );
}
