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
  filename: string;
  creatorName: string;
  status: string;
  version: string;
  averageReviewGrade?: number | null;
  reviewCount: number;
  aiAssessment: AIAssessment;
  reviewer?: Reviewer;
}

export default function DocumentSidebar({
  data,
<<<<<<< Updated upstream
}: {
  data: DocumentDetailData;
}) {
=======
  userRole,
  onApprove,
  onReject,
  isApproving = false,
  isRejecting = false,
}: DocumentSidebarProps) {
  const { t } = useTranslation();
  const [score, setScore] = useState<string>("");
  const [comment, setComment] = useState<string>("");

  const normalizedStatus = data.status.toLowerCase();
  const isDraft =
    normalizedStatus.includes("draft") || normalizedStatus.includes("nháp");
  const isPending =
    normalizedStatus.includes("pending") || normalizedStatus.includes("chờ");
  const isApproved =
    normalizedStatus.includes("approved") || normalizedStatus.includes("duyệt");
  const isRejected =
    normalizedStatus.includes("rejected") || normalizedStatus.includes("từ chối");

  const handleApprove = () => {
    const grade = Number(score);
    if (!Number.isInteger(grade) || grade < 1 || grade > 10 || !comment.trim()) return;
    onApprove?.(grade, comment);
  };

  const handleReject = () => {
    const grade = Number(score);
    if (!Number.isInteger(grade) || grade < 1 || grade > 10 || !comment.trim()) return;
    onReject?.(grade, comment);
  };

  const statusBadgeClass = isApproved
    ? "bg-[#e6f4ea] text-[#1e4620]"
    : isRejected
      ? "bg-[#fce8e6] text-[#c5221f]"
      : isPending
        ? "bg-[#fef7e0] text-[#b06000]"
        : "bg-tertiary-container text-on-tertiary";

>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
            <span className="text-xs text-on-surface-variant block mb-1">
              Mã Số
=======
            <span className="text-xs text-on-surface-variant block mb-1">File</span>
            <span className="font-medium text-sm truncate block" title={data.filename}>
              {data.filename}
>>>>>>> Stashed changes
            </span>
            <span className="font-medium text-sm">{data.id}</span>
          </div>
          <div>
<<<<<<< Updated upstream
            <span className="text-xs text-on-surface-variant block mb-1">
              Phiên Bản
            </span>
=======
            <span className="text-xs text-on-surface-variant block mb-1">Created by</span>
            <span className="font-medium text-sm truncate block">{data.creatorName}</span>
          </div>
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">Review score</span>
            <span className="font-medium text-sm">{data.averageReviewGrade != null ? `${data.averageReviewGrade.toFixed(1)}/10` : "—"} ({data.reviewCount})</span>
          </div>
          <div>
            <span className="text-xs text-on-surface-variant block mb-1">{t.common.version}</span>
>>>>>>> Stashed changes
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
<<<<<<< Updated upstream
          <div className="flex gap-4">
            <img
              alt={data.reviewer.name}
              className="w-10 h-10 rounded-full bg-surface-container object-cover"
              src={data.reviewer.avatar}
            />
=======
          <div className="flex items-center gap-3 mb-3">
            {data.reviewer.avatar ? (
              // eslint-disable-next-line @next/next/no-img-element
              <img
                src={data.reviewer.avatar}
                alt="avatar"
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <div className="w-8 h-8 rounded-full bg-secondary-container flex items-center justify-center text-xs font-bold text-on-secondary-container">
                {data.reviewer.name.charAt(0)}
              </div>
            )}
>>>>>>> Stashed changes
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

<<<<<<< Updated upstream
      {/* Cụm Nút Hành Động */}
      <div className="flex flex-col gap-3 mt-auto pt-4">
        <button className="w-full bg-tertiary text-on-tertiary py-3 rounded-lg font-medium text-sm hover:bg-tertiary-dim transition-colors shadow-sm">
          Gửi Yêu Cầu Duyệt Lại
        </button>
        <button className="w-full bg-surface-container text-on-surface py-3 rounded-lg font-medium text-sm hover:bg-surface-container-high transition-colors">
          Tải Lên Phiên Bản Mới
        </button>
=======
      {/* 4. Action Area by Role & Status */}
      <div className="mt-auto pt-4 shrink-0 flex flex-col gap-6">
        {/* APPROVER UI */}
        {userRole === "approver" && (
          <>
            {isPending ? (
              <div className="bg-surface-container-lowest rounded-xl shadow-sm border border-outline-variant/30 overflow-hidden">
                <div className="bg-surface-container-low px-6 py-3 border-b border-outline-variant/15">
                  <h4 className="font-headline font-semibold text-sm text-on-surface">
                    {t.approvals.title}
                  </h4>
                </div>
                <div className="p-6 space-y-5">
                  <div className="space-y-2">
                    <label
                      className="text-xs font-bold text-on-surface-variant block uppercase tracking-wider"
                      htmlFor="reviewer-score"
                    >
                      Score (1-10)
                    </label>
                    <input
                      id="reviewer-score"
                      type="number"
                      min="1"
                      max="10"
                      step="1"
                      placeholder="1-10"
                      value={score}
                      onChange={(e) => setScore(e.target.value)}
                      className="w-24 bg-surface-container-low border-none rounded-lg text-sm font-bold text-tertiary focus:ring-1 focus:ring-tertiary/30 px-3 py-2 text-center"
                    />
                  </div>
                  <div className="space-y-2">
                    <label
                      className="text-xs font-bold text-on-surface-variant block uppercase tracking-wider"
                      htmlFor="review-comments"
                    >
                      Review comment
                    </label>
                    <textarea
                      id="review-comments"
                      rows={3}
                      value={comment}
                      onChange={(e) => setComment(e.target.value)}
                      placeholder="Explain your assessment of this document..."
                      className="w-full bg-surface-container-low border-none rounded-lg text-sm text-on-surface focus:ring-1 focus:ring-tertiary/30 resize-none custom-scrollbar"
                    />
                  </div>
                  <div className="flex gap-3 pt-2">
                    <button
                      onClick={handleApprove}
                      disabled={isApproving || isRejecting || !score || !comment.trim()}
                      className="flex-1 bg-[#4caf50] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isApproving ? (
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <span className="material-symbols-outlined text-[18px]">check_circle</span>
                      )}
                      {t.documents.detail.approve}
                    </button>
                    <button
                      onClick={handleReject}
                      disabled={isApproving || isRejecting || !score || !comment.trim()}
                      className="flex-1 bg-[#f44336] text-white py-2.5 rounded-lg font-medium text-sm hover:opacity-90 flex items-center justify-center gap-2 shadow-sm disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      {isRejecting ? (
                        <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                      ) : (
                        <span className="material-symbols-outlined text-[18px]">cancel</span>
                      )}
                      {t.documents.detail.reject}
                    </button>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
                <span className="material-symbols-outlined text-on-surface-variant mb-1" style={{ fontSize: "24px" }}>
                  {isDraft ? "edit_document" : isApproved ? "verified" : "block"}
                </span>
                <p className="text-xs text-on-surface-variant font-medium px-4">
                  {isDraft && t.status.draft}
                  {isApproved && t.status.approved}
                  {isRejected && t.status.rejected}
                </p>
              </div>
            )}
          </>
        )}

        {/* EDITOR UI */}
        {userRole === "editor" && (
          <div className="flex flex-col gap-3">
            {(isDraft || isRejected) && (
              <>
                <button className="w-full bg-tertiary text-on-tertiary py-3 rounded-lg font-semibold text-sm hover:bg-tertiary-dim transition-colors shadow-sm flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">send</span>
                  {t.documents.detail.submitForReview}
                </button>
                <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2">
                  <span className="material-symbols-outlined text-[18px]">upload</span>
                  {t.documents.detail.newVersion}
                </button>
              </>
            )}
            {isApproved && (
              <button className="w-full bg-surface-container border border-outline-variant/20 text-on-surface py-3 rounded-lg font-semibold text-sm hover:bg-surface-container-high transition-colors flex items-center justify-center gap-2 shadow-sm">
                <span className="material-symbols-outlined text-[18px]">note_add</span>
                {t.documents.detail.newVersion}
              </button>
            )}
            {isPending && (
              <div className="text-center py-4 bg-surface-container-lowest rounded-xl border border-tertiary/30 bg-tertiary/5">
                <span className="material-symbols-outlined text-tertiary mb-1 animate-pulse" style={{ fontSize: "24px" }}>
                  hourglass_empty
                </span>
                <p className="text-xs text-tertiary font-bold px-4">
                  {t.status.pending_review}
                </p>
              </div>
            )}
          </div>
        )}

        {/* VIEWER UI */}
        {userRole === "viewer" && (
          <div className="text-center py-4 bg-surface-container-low rounded-xl border border-surface-variant border-dashed">
            <span className="material-symbols-outlined text-on-surface-variant mb-1" style={{ fontSize: "24px" }}>
              visibility
            </span>
            <p className="text-xs text-on-surface-variant font-medium">
              Viewer
            </p>
          </div>
        )}
>>>>>>> Stashed changes
      </div>
    </aside>
  );
}
