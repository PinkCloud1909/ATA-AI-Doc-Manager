export default function StatusChart() {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <div className="lg:col-span-2 bg-surface-container-lowest p-6 rounded-xl">
        <div className="flex justify-between items-center mb-8">
          <div>
            <h2 className="text-lg font-bold text-on-surface">
              Thống kê điểm đánh giá
            </h2>
            <p className="text-xs text-on-surface-variant">
              Số lượng tài liệu phân bổ theo thang điểm 0-10
            </p>
          </div>
          <div className="flex gap-2">
            <button className="px-3 py-1 text-[10px] font-bold bg-surface-container text-on-surface rounded-full">
              30 ngày
            </button>
            <button className="px-3 py-1 text-[10px] font-bold text-on-surface-variant hover:bg-surface-container rounded-full">
              90 ngày
            </button>
          </div>
        </div>
        <div className="h-64 flex items-end gap-2 md:gap-4 px-2">
          <div className="flex-1 group relative">
            <div className="bg-surface-container group-hover:bg-tertiary/20 h-12 rounded-t-sm transition-all duration-300"></div>
            <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-on-surface-variant">
              0-2
            </span>
          </div>
          <div className="flex-1 group relative">
            <div className="bg-surface-container group-hover:bg-tertiary/20 h-24 rounded-t-sm transition-all duration-300"></div>
            <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-on-surface-variant">
              3-4
            </span>
          </div>
          <div className="flex-1 group relative">
            <div className="bg-surface-container-highest group-hover:bg-tertiary/40 h-48 rounded-t-sm transition-all duration-300"></div>
            <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-on-surface-variant">
              5-6
            </span>
          </div>
          <div className="flex-1 group relative">
            <div className="bg-tertiary/80 group-hover:bg-tertiary h-60 rounded-t-sm transition-all duration-300"></div>
            <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-on-surface">
              7-8
            </span>
          </div>
          <div className="flex-1 group relative">
            <div className="bg-primary/60 group-hover:bg-primary h-32 rounded-t-sm transition-all duration-300"></div>
            <span className="absolute -bottom-6 left-1/2 -translate-x-1/2 text-[10px] font-bold text-on-surface-variant">
              9-10
            </span>
          </div>
        </div>
      </div>

      <div className="bg-surface-container-lowest p-6 rounded-xl flex flex-col">
        <h2 className="text-lg font-bold text-on-surface mb-6">
          Trạng thái tài liệu
        </h2>
        <div className="flex-1 flex items-center justify-center relative py-6">
          <svg className="w-40 h-40 transform -rotate-90">
            <circle
              cx="80"
              cy="80"
              fill="transparent"
              r="70"
              stroke="#e3e9ec"
              stroke-dasharray="440"
              stroke-dashoffset="0"
              stroke-width="20"
            ></circle>
            <circle
              cx="80"
              cy="80"
              fill="transparent"
              r="70"
              stroke="#5e5e5e"
              stroke-dasharray="440"
              stroke-dashoffset="44"
              stroke-width="20"
            ></circle>
            <circle
              cx="80"
              cy="80"
              fill="transparent"
              r="70"
              stroke="#0053dc"
              stroke-dasharray="440"
              stroke-dashoffset="154"
              stroke-width="20"
            ></circle>
          </svg>
          <div className="absolute text-center">
            <span className="text-2xl font-black text-on-surface tracking-tighter">
              1,2k
            </span>
            <p className="text-[10px] font-bold text-on-surface-variant uppercase tracking-tighter">
              Tổng số
            </p>
          </div>
        </div>
        <div className="mt-4 space-y-3">
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-tertiary"></span>
              <span className="text-sm text-on-surface-variant">Approved</span>
            </div>
            <span className="text-sm font-bold text-on-surface">65%</span>
          </div>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-primary"></span>
              <span className="text-sm text-on-surface-variant">Pending</span>
            </div>
            <span className="text-sm font-bold text-on-surface">25%</span>
          </div>
          <div className="flex justify-between items-center">
            <div className="flex items-center gap-2">
              <span className="w-3 h-3 rounded-full bg-surface-container-high"></span>
              <span className="text-sm text-on-surface-variant">Draft</span>
            </div>
            <span className="text-sm font-bold text-on-surface">10%</span>
          </div>
        </div>
      </div>
    </div>
  );
}
