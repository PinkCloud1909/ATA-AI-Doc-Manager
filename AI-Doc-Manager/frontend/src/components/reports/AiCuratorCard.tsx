export default function AiCuratorCard() {
  return (
    <div className="bg-tertiary text-on-tertiary p-8 rounded-xl relative overflow-hidden flex flex-col justify-between group">
      <div className="relative z-10">
        <span
          className="material-symbols-outlined text-[32px] mb-4"
          data-icon="bolt"
          style={{}}
        >
          bolt
        </span>
        <h2 className="text-2xl font-bold tracking-tight mb-2" style={{}}>
          Gợi ý từ AI Curator
        </h2>
        <p className="text-sm opacity-80 leading-relaxed" style={{}}>
          Dựa trên xu hướng truy cập, bộ phận Marketing có thể cần tài liệu về
          "Chiến lược nội dung Q3". Bạn có muốn tạo bản nháp ngay?
        </p>
      </div>
      <div className="mt-8 relative z-10">
        <button
          className="bg-white text-tertiary px-6 py-2.5 rounded-lg font-bold text-sm shadow-xl active:scale-95 transition-all"
          style={{}}
        >
          Tạo nhanh bản thảo
        </button>
      </div>
      {/* Abstract BG Decor */}
      <div className="absolute -right-12 -bottom-12 w-48 h-48 bg-white/10 rounded-full blur-3xl group-hover:scale-150 transition-transform duration-700"></div>
      <div className="absolute right-0 top-0 w-24 h-24 bg-white/5 rounded-full blur-2xl"></div>
    </div>
  );
}
