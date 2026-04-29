export default function ActivityTable() {
  return (
    <div className="xl:col-span-2 bg-surface-container-lowest p-6 rounded-xl">
      <div className="flex justify-between items-center mb-6">
        <h2 className="text-lg font-bold text-on-surface">Hoạt động gần đây</h2>
        <button className="text-tertiary text-xs font-bold hover:underline">
          Xem tất cả
        </button>
      </div>
      <div className="space-y-4">{/* Các thẻ div chứa activity item */}</div>
    </div>
  );
}
