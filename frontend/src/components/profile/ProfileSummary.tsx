"use client";

import { useAuth } from "@/hooks/useAuth";
import { usePermission } from "@/hooks/usePermission";
import { useTranslation } from "@/i18n/LanguageContext";

export default function ProfileSummary() {
  const { t } = useTranslation();
  const { user } = useAuth();
  const perm = usePermission();

  const getInitials = (name?: string) => {
    if (!name) return "U";
    return name.slice(0, 2).toUpperCase();
  };

  return (
    <div className="lg:col-span-4 flex flex-col gap-6">
      {/* Profile Card */}
      <div className="bg-surface-container-lowest rounded-xl p-8 flex flex-col items-center text-center relative overflow-hidden group border border-outline-variant/10">
        {/* Decorative background shape */}
        <div className="absolute top-0 left-0 w-full h-24 bg-gradient-to-b from-surface-container-low to-transparent -z-10"></div>
        <div className="relative mb-6">
          <div className="w-32 h-32 rounded-full object-cover border-4 border-surface-container-lowest shadow-[0_4px_6px_-1px_rgba(43,52,55,0.04),0_10px_15px_-3px_rgba(43,52,55,0.08)] flex items-center justify-center bg-secondary-container text-4xl font-bold text-on-secondary-container">
            {getInitials(user?.username)}
          </div>
          <button className="absolute bottom-1 right-1 w-8 h-8 bg-surface-container-lowest border border-outline-variant/20 rounded-full flex items-center justify-center text-on-surface-variant hover:text-tertiary hover:border-tertiary/30 transition-all shadow-sm">
            <span className="material-symbols-outlined text-[18px]">edit</span>
          </button>
        </div>
        <h3 className="font-headline text-xl font-bold text-on-background mb-1">
          {user?.username || t.profile.notAvailable}
        </h3>
        <span className="inline-flex items-center px-3 py-1 rounded-full bg-tertiary-container/10 text-tertiary text-xs font-semibold tracking-wide uppercase mt-2">
          {perm.canAdmin ? t.admin.adminRole : t.admin.viewerRole}
        </span>
      </div>

      {/* Security Quick Actions */}
      <div className="bg-surface-container-lowest rounded-xl p-6 border border-outline-variant/10">
        <h4 className="font-headline text-sm font-bold text-on-background uppercase tracking-widest mb-4 opacity-70">
          {t.profile.securityQuickActions}
        </h4>
        <div className="space-y-2">
          <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-surface-container-low transition-colors text-left group">
            <div className="flex items-center text-on-background text-sm font-medium">
              <span className="material-symbols-outlined mr-3 text-on-surface-variant group-hover:text-tertiary transition-colors">
                password
              </span>
              {t.profile.changePassword}
            </div>
            <span className="material-symbols-outlined text-on-surface-variant opacity-50 text-[18px]">
              chevron_right
            </span>
          </button>
          <button className="w-full flex items-center justify-between p-3 rounded-lg hover:bg-surface-container-low transition-colors text-left group">
            <div className="flex items-center text-on-background text-sm font-medium">
              <span className="material-symbols-outlined mr-3 text-on-surface-variant group-hover:text-tertiary transition-colors">
                verified_user
              </span>
              {t.profile.twoFactorAuth}
            </div>
            <span className="inline-flex items-center px-2 py-0.5 rounded-full bg-surface-container-high text-on-surface-variant text-[10px] font-bold uppercase tracking-wider">
              {t.profile.notAvailable}
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
