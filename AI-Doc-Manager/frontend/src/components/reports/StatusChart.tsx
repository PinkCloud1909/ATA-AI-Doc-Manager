export default function StatusChart() {
  return (
    <div className="w-full bg-surface-container-lowest p-6 lg:p-8 rounded-xl border border-outline-variant/15 shadow-sm">
      <div className="flex justify-between items-center mb-8">
        <div>
          <h2 className="text-lg font-bold text-on-surface">
            Thống kê điểm đánh giá AI
          </h2>
          <p className="text-xs text-on-surface-variant mt-1">
            Số lượng tài liệu phân bổ theo thang điểm 0-10
          </p>
        </div>
      </div>

      <div className="h-64 flex items-end gap-3 md:gap-6 px-2 lg:px-8">
        <div className="flex-1 group relative">
          <div className="bg-surface-container group-hover:bg-tertiary/20 h-12 rounded-t-md transition-all duration-300"></div>
          <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-on-surface-variant">
            0-2
          </span>
        </div>
        <div className="flex-1 group relative">
          <div className="bg-surface-container group-hover:bg-tertiary/20 h-24 rounded-t-md transition-all duration-300"></div>
          <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-on-surface-variant">
            3-4
          </span>
        </div>
        <div className="flex-1 group relative">
          <div className="bg-surface-container-highest group-hover:bg-tertiary/40 h-48 rounded-t-md transition-all duration-300"></div>
          <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-on-surface-variant">
            5-6
          </span>
        </div>
        <div className="flex-1 group relative">
          <div className="bg-tertiary/80 group-hover:bg-tertiary h-60 rounded-t-md transition-all duration-300 shadow-sm"></div>
          <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-tertiary">
            7-8
          </span>
        </div>
        <div className="flex-1 group relative">
          <div className="bg-primary/60 group-hover:bg-primary h-32 rounded-t-md transition-all duration-300"></div>
          <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-xs font-bold text-on-surface-variant">
            9-10
          </span>
        </div>
      </div>
    </div>
  );
}
