import ProfileSummary from "@/components/profile/ProfileSummary";
import ProfileForm from "@/components/profile/ProfileForm";

export default function ProfilePage() {
  return (
    <div className="flex-1 pt-6 px-6 md:px-12 pb-12 overflow-y-auto">
      <div className="max-w-5xl mx-auto">
        {/* Page Header */}
        <div className="mb-10 mt-4">
          <h2 className="font-headline text-3xl font-extrabold tracking-tight text-on-background mb-2">
            Hồ sơ người dùng
          </h2>
          <p className="font-body text-on-surface-variant text-base">
            Quản lý thông tin cá nhân và cài đặt bảo mật của bạn.
          </p>
        </div>

        {/* Bento Grid Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          <ProfileSummary />
          <ProfileForm />
        </div>
      </div>
    </div>
  );
}
