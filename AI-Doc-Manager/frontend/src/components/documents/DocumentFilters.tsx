interface FilterProps {
  searchQuery: string;
  setSearchQuery: (val: string) => void;
  statusFilter: string;
  setStatusFilter: (val: string) => void;
  typeFilter: string;
  setTypeFilter: (val: string) => void;
}

export default function DocumentFilters({
  searchQuery,
  setSearchQuery,
  statusFilter,
  setStatusFilter,
  typeFilter,
  setTypeFilter,
}: FilterProps) {
  return (
    <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
      {/* Tìm kiếm nhanh */}
      <div className="md:col-span-4 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm">
        <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
          Tìm kiếm nhanh
        </label>
        <div className="relative">
          <span className="material-symbols-outlined absolute left-3 top-1/2 -translate-y-1/2 text-neutral-400">
            search
          </span>
          <input
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="w-full bg-surface-container-low border-none rounded-lg pl-10 pr-4 py-2 text-sm focus:ring-2 focus:ring-tertiary/10"
            placeholder="Nhập tên tài liệu hoặc ID..."
            type="text"
          />
        </div>
      </div>

      {/* Trạng thái */}
      <div className="md:col-span-2 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm">
        <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
          Trạng thái
        </label>
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="w-full bg-surface-container-low border-none rounded-lg py-2 text-sm focus:ring-0"
        >
          <option value="Tất cả">Tất cả</option>
          <option value="Draft">Draft</option>
          <option value="Pending">Pending</option>
          <option value="Approved">Approved</option>
        </select>
      </div>

      {/* Loại file */}
      <div className="md:col-span-2 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm">
        <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
          Loại file
        </label>
        <select
          value={typeFilter}
          onChange={(e) => setTypeFilter(e.target.value)}
          className="w-full bg-surface-container-low border-none rounded-lg py-2 text-sm focus:ring-0"
        >
          <option value="Tất cả">Tất cả</option>
          <option value="Runbook">Runbook</option>
          <option value="SOP">SOP</option>
          <option value="Policy">Policy</option>
        </select>
      </div>

      {/* Khu vực Người tạo (Giữ nguyên giao diện) */}
      <div className="md:col-span-4 bg-surface-container-lowest p-4 rounded-xl border border-transparent shadow-sm flex items-end justify-between">
        {/* ... (Giữ nguyên đoạn hiển thị Avatar người tạo) ... */}
        <div className="flex-1">
          <label className="text-[10px] font-bold uppercase tracking-widest text-neutral-400 block mb-2">
            Người tạo
          </label>
          <div className="flex -space-x-2">
            {/* Tạm thời để URL ảnh giả lập từ code gốc, sau này bạn có thể truyền props mảng avatar */}
            <img
              alt="User"
              className="w-8 h-8 rounded-full border-2 border-white object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuB96B6d13snbaUtljFCrFG-bRJMmjwn9pEAYOVfCqzo9_s36Q3cUvrc728mVItCemO0pIFUEDO4KOvL3yPJVzld6bMNzEUoDdXXSFqY_7NEIRrtC-n8r0YHySSDl5qoZ4SZXQCfh9e7VH_SUmVJvmXhu9keXdfgWG0o6aT2hQ2TvRDTD4XDYjVQdAMrjx9BZ0E_Uzr5Qb2aHCFZRGVEMbbfLyMW1PjAHpSN3q-EFP-hjbDwe6NwYsMXOR3QXsNa49iEgAEgd5iT3XK_"
            />
            <img
              alt="User"
              className="w-8 h-8 rounded-full border-2 border-white object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuBobRQTtmH-4YgDppoDNLmBU0y0DRSyaYt7hN2B3yTqD8P9w2Oznxi10X0AmAnmzVQ0lv-aeFZhbq8N96SRUa4JtIiEx-GYMjInWsgjGr7bm41I4tzQSM1YAaKjmhdAbWwOk38dt_Q1RtKF2ikBPBVcM827-zD6tI7DxUGckWo376awYyBv50RIlp2TBga18TOCzoMT5bxH5C0wu75ttB-LFjosezcBrxCxRDluOQ4xxS0L1HsbzhYPGE6fd4Ec-w_OsSOqsafUfmOy"
            />
            <img
              alt="User"
              className="w-8 h-8 rounded-full border-2 border-white object-cover"
              src="https://lh3.googleusercontent.com/aida-public/AB6AXuAnkYGJeqz-gNV9JoV4Bf5Xg8_GIC1HQ7wvlU9rbi-cY1Cfcw4k9IBuXaVDoq8ocL7ye_7Z7HbPeWjWVqwq75J_WtU66k9L3bMArDWWKPoww5NQ8oUBfmcq1vuxNrEg19SwulVKwJJdmXlpmhdLbRlMinwd6ltfzCPsx8Qh91QMmzqTigybziW05yj9qyMTfwl7h5phbrjcaAytwpRM-nssPfG1Qk50dDfqkhCWSQhZKvY8XQwumhQdbQSuYW_HuSCfq60itm56Dw1N"
            />
            <div className="w-8 h-8 rounded-full border-2 border-white bg-surface-container-high flex items-center justify-center text-[10px] font-bold text-on-surface">
              +12
            </div>
          </div>
        </div>
        <button
          onClick={() => {
            setSearchQuery("");
            setStatusFilter("Tất cả");
            setTypeFilter("Tất cả");
          }}
          className="text-tertiary text-sm font-semibold hover:underline"
        >
          Xóa lọc
        </button>
      </div>
    </div>
  );
}
