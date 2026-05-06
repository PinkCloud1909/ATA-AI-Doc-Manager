import ActivityFeed from "@/components/activities/ActivityFeed";

export default function ActivitiesPage() {
  return (
    <div className="flex-1 overflow-y-auto p-6 lg:p-10 scroll-smooth">
      <div className="max-w-5xl mx-auto">
        {/* Page Header */}
        <div className="mb-10">
          <h2 className="font-headline text-[32px] font-extrabold text-on-surface tracking-tight leading-tight">
            Hoạt động gần đây
          </h2>
          <p className="text-on-surface-variant mt-2 text-sm max-w-2xl">
            Theo dõi và quản lý mọi thay đổi, cập nhật và thảo luận trong hệ
            thống tri thức của bạn.
          </p>
        </div>

        {/* Gọi component danh sách đã tách ở trên */}
        <ActivityFeed />
      </div>
    </div>
  );
}
