export default function SummaryCards() {
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Card 1: Tổng tài liệu */}
      <div className="bg-surface-container-lowest p-6 rounded-xl border border-transparent flex items-center justify-between group hover:bg-surface-container-low transition-colors">
        <div>
          <p className="text-on-surface-variant text-xs font-bold uppercase tracking-widest mb-1">
            Tổng tài liệu
          </p>
          <h3 className="text-3xl font-extrabold text-on-surface tracking-tight">
            1,284
          </h3>
          <p className="text-[10px] text-tertiary mt-2 flex items-center font-bold">
            <span
              className="material-symbols-outlined text-[12px] mr-1"
              data-icon="trending_up"
            >
              trending_up
            </span>
            +12% so với tháng trước
          </p>
        </div>
        <div className="w-12 h-12 rounded-full bg-surface-container flex items-center justify-center text-primary">
          <span
            className="material-symbols-outlined text-[24px]"
            data-icon="folder"
          >
            folder
          </span>
        </div>
      </div>

      {/* Card 2: Đã duyệt */}
      <div className="bg-surface-container-lowest p-6 rounded-xl border border-transparent flex items-center justify-between group hover:bg-surface-container-low transition-colors">
        <div>
          <p className="text-on-surface-variant text-xs font-bold uppercase tracking-widest mb-1">
            Đã duyệt
          </p>
          <h3 className="text-3xl font-extrabold text-on-surface tracking-tight">
            856
          </h3>
          <p className="text-[10px] text-on-success-container mt-2 flex items-center font-bold">
            <span
              className="material-symbols-outlined text-[12px] mr-1"
              data-icon="check_circle"
            >
              check_circle
            </span>
            66.7% Tỉ lệ hoàn tất
          </p>
        </div>
        <div className="w-12 h-12 rounded-full bg-secondary-container flex items-center justify-center text-on-secondary-container">
          <span
            className="material-symbols-outlined text-[24px]"
            data-icon="task_alt"
          >
            task_alt
          </span>
        </div>
      </div>

      {/* Card 3: Đang chờ */}
      <div className="bg-surface-container-lowest p-6 rounded-xl border border-transparent flex items-center justify-between group hover:bg-surface-container-low transition-colors">
        <div>
          <p className="text-on-surface-variant text-xs font-bold uppercase tracking-widest mb-1">
            Đang chờ
          </p>
          <h3 className="text-3xl font-extrabold text-on-surface tracking-tight">
            142
          </h3>
          <p className="text-[10px] text-on-error-container mt-2 flex items-center font-bold">
            <span
              className="material-symbols-outlined text-[12px] mr-1"
              data-icon="schedule"
            >
              schedule
            </span>
            Cần xử lý ngay
          </p>
        </div>
        <div className="w-12 h-12 rounded-full bg-surface-container-high flex items-center justify-center text-primary-dim">
          <span
            className="material-symbols-outlined text-[24px]"
            data-icon="pending"
          >
            pending
          </span>
        </div>
      </div>
    </div>
  );
}
