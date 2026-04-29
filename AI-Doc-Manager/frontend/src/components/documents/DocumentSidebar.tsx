interface Reviewer {
  name: string;
  role: string;
  avatar: string;
  comment: string;
  statusLabel: string;
}

interface AIAssessment {
  score: string;
  label: string;
  summary: string;
  points: { isPositive: boolean; text: string }[];
}

export interface DocumentDetailData {
  id: string;
  title: string;
  status: string;
  version: string;
  aiAssessment: AIAssessment;
  reviewer?: Reviewer;
}

export default function DocumentSidebar({
  data,
}: {
  data: DocumentDetailData;
}) {
  return (
    <aside className="w-96 flex flex-col gap-6 overflow-y-auto pb-8 pr-2 custom-scrollbar">
      {/* Thẻ Thông tin chung */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15">
        <div className="flex justify-between items-start mb-4">
          <div>
            <span className="text-[10px] font-label uppercase tracking-widest text-on-surface-variant font-semibold">
              Tài Liệu
            </span>
            <h3 className="font-headline font-bold text-lg text-on-surface mt-1">
              {data.title}
            </h3>
          </div>
          <span className="bg-tertiary-container text-on-tertiary px-3 py-1 rounded-full text-xs font-semibold">
            {data.status}
          </span>
        </div>
        <div className="grid grid-cols-2 gap-4 mt-6">
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">
              Mã Số
            </span>
            <span className="font-medium text-sm">{data.id}</span>
          </div>
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">
              Phiên Bản
            </span>
            <span className="font-medium text-sm">{data.version}</span>
          </div>
        </div>
      </div>

      {/* Thẻ Đánh giá AI */}
      <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15">
        <div className="flex items-center gap-2 mb-4">
          <span className="material-symbols-outlined text-tertiary text-[20px]">
            auto_awesome
          </span>
          <h4 className="font-headline font-semibold text-md text-on-surface">
            Đánh Giá AI
          </h4>
        </div>
        <div className="flex items-center gap-6 mb-6">
          <div className="relative w-20 h-20 flex items-center justify-center rounded-full bg-surface-container-low border-4 border-tertiary">
            <span className="font-headline font-bold text-2xl text-on-surface">
              {data.aiAssessment.score}
            </span>
          </div>
          <div className="flex-1">
            <p className="text-sm font-medium text-on-surface">
              {data.aiAssessment.label}
            </p>
            <p className="text-xs text-on-surface-variant mt-1">
              {data.aiAssessment.summary}
            </p>
          </div>
        </div>
        <ul className="space-y-3">
          {data.aiAssessment.points.map((point, index) => (
            <li key={index} className="flex gap-3 text-sm">
              <span
                className={`material-symbols-outlined text-[18px] ${point.isPositive ? "text-[#4caf50]" : "text-[#ff9800]"}`}
              >
                {point.isPositive ? "check_circle" : "warning"}
              </span>
              <span className="text-on-surface-variant">{point.text}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Thẻ Phản hồi từ người duyệt (Chỉ hiện nếu có data) */}
      {data.reviewer && (
        <div className="bg-surface-container-lowest rounded-xl p-6 shadow-sm border border-outline-variant/15">
          <h4 className="font-headline font-semibold text-md text-on-surface mb-4">
            Phản Hồi Từ Người Duyệt
          </h4>
          <div className="flex gap-4">
            <img
              alt={data.reviewer.name}
              className="w-10 h-10 rounded-full bg-surface-container object-cover"
              src={data.reviewer.avatar}
            />
            <div>
              <p className="text-sm font-medium text-on-surface">
                {data.reviewer.name}
              </p>
              <p className="text-xs text-on-surface-variant">
                {data.reviewer.role}
              </p>
              <div className="bg-surface-container-low p-3 rounded-lg mt-2 text-sm text-on-surface-variant relative">
                <p>"{data.reviewer.comment}"</p>
              </div>
              <span className="inline-block mt-2 text-xs font-semibold text-[#ff9800] bg-[#fff3e0] px-2 py-1 rounded">
                {data.reviewer.statusLabel}
              </span>
            </div>
          </div>
        </div>
      )}

      {/* Cụm Nút Hành Động */}
      <div className="flex flex-col gap-3 mt-auto pt-4">
        <button className="w-full bg-tertiary text-on-tertiary py-3 rounded-lg font-medium text-sm hover:bg-tertiary-dim transition-colors shadow-sm">
          Gửi Yêu Cầu Duyệt Lại
        </button>
        <button className="w-full bg-surface-container text-on-surface py-3 rounded-lg font-medium text-sm hover:bg-surface-container-high transition-colors">
          Tải Lên Phiên Bản Mới
        </button>
      </div>
    </aside>
  );
}
