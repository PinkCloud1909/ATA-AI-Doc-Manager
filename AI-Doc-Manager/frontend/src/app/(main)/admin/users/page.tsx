"use client";

import { useMemo, useState } from "react";

type UserRole = "Viewer" | "Editor" | "Approver";
type UserStatus = "Active" | "Inactive";

interface ManagedUser {
  id: string;
  name: string;
  email: string;
  role: UserRole;
  createdAt: string;
  status: UserStatus;
  avatarUrl?: string;
  initials: string;
}

const initialUsers: ManagedUser[] = [
  {
    id: "usr-001",
    name: "Nguyễn Văn An",
    email: "an.nguyen@example.com",
    role: "Viewer",
    createdAt: "12/10/2023",
    status: "Active",
    initials: "NA",
  },
  {
    id: "usr-002",
    name: "Trần Thị Bình",
    email: "binh.tran@example.com",
    role: "Editor",
    createdAt: "05/09/2023",
    status: "Active",
    initials: "TB",
  },
  {
    id: "usr-003",
    name: "Lê Hoàng Cường",
    email: "cuong.le@example.com",
    role: "Approver",
    createdAt: "22/11/2023",
    status: "Inactive",
    initials: "LC",
  },
  {
    id: "usr-004",
    name: "Phạm Thị Dung",
    email: "dung.pham@example.com",
    role: "Viewer",
    createdAt: "01/12/2023",
    status: "Active",
    initials: "PD",
  },
  {
    id: "usr-005",
    name: "Đỗ Minh Khang",
    email: "khang.do@example.com",
    role: "Editor",
    createdAt: "16/01/2024",
    status: "Active",
    initials: "DK",
  },
  {
    id: "usr-006",
    name: "Vũ Thu Hà",
    email: "ha.vu@example.com",
    role: "Approver",
    createdAt: "08/02/2024",
    status: "Active",
    initials: "VH",
  },
];

const totalUsers = 1284;
const baseRoleCounts: Record<UserRole, number> = {
  Viewer: 856,
  Editor: 242,
  Approver: 186,
};

const roles: UserRole[] = ["Viewer", "Editor", "Approver"];

const roleStyles: Record<UserRole, string> = {
  Viewer: "bg-surface-container text-on-surface-variant",
  Editor: "bg-secondary-container text-on-secondary-container",
  Approver: "bg-tertiary-container text-on-tertiary",
};

const roleDots: Record<UserRole, string> = {
  Viewer: "bg-outline-variant",
  Editor: "bg-secondary-dim",
  Approver: "bg-tertiary",
};

function StatCard({
  label,
  value,
  dotClass,
}: {
  label: string;
  value: number;
  dotClass?: string;
}) {
  return (
    <section className="border border-outline-variant/10 bg-white p-6 shadow-sm">
      <div className="mb-8 flex items-center gap-3">
        {dotClass && <span className={`h-2.5 w-2.5 rounded-full ${dotClass}`} />}
        <p className="text-sm font-bold uppercase tracking-wide text-on-surface-variant">
          {label}
        </p>
      </div>
      <p className="text-4xl font-black tracking-tight text-on-surface">
        {value.toLocaleString("en-US")}
      </p>
    </section>
  );
}

export default function UsersPage() {
  const [users, setUsers] = useState(initialUsers);
  const [searchQuery, setSearchQuery] = useState("");
  const [roleFilter, setRoleFilter] = useState<UserRole | "All">("All");
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [bulkRole, setBulkRole] = useState<UserRole>("Viewer");
  const [isBulkOpen, setIsBulkOpen] = useState(false);

  const displayedUsers = useMemo(() => {
    const normalizedQuery = searchQuery.trim().toLowerCase();

    return users.filter((user) => {
      const matchesSearch =
        !normalizedQuery ||
        user.name.toLowerCase().includes(normalizedQuery) ||
        user.email.toLowerCase().includes(normalizedQuery);
      const matchesRole = roleFilter === "All" || user.role === roleFilter;

      return matchesSearch && matchesRole;
    });
  }, [users, searchQuery, roleFilter]);

  const visibleIds = displayedUsers.map((user) => user.id);
  const allVisibleSelected =
    visibleIds.length > 0 && visibleIds.every((id) => selectedIds.includes(id));

  const roleCounts = useMemo(() => {
    const visibleDeltas = roles.reduce(
      (acc, role) => ({ ...acc, [role]: 0 }),
      {} as Record<UserRole, number>,
    );

    for (const user of initialUsers) visibleDeltas[user.role] -= 1;
    for (const user of users) visibleDeltas[user.role] += 1;

    return roles.reduce(
      (acc, role) => ({
        ...acc,
        [role]: baseRoleCounts[role] + visibleDeltas[role],
      }),
      {} as Record<UserRole, number>,
    );
  }, [users]);

  const toggleUser = (id: string) => {
    setSelectedIds((current) =>
      current.includes(id)
        ? current.filter((selectedId) => selectedId !== id)
        : [...current, id],
    );
  };

  const toggleAllVisible = () => {
    setSelectedIds((current) => {
      if (allVisibleSelected) {
        return current.filter((id) => !visibleIds.includes(id));
      }

      return Array.from(new Set([...current, ...visibleIds]));
    });
  };

  const assignRole = (ids: string[], role: UserRole) => {
    setUsers((current) =>
      current.map((user) => (ids.includes(user.id) ? { ...user, role } : user)),
    );
  };

  const applyBulkRole = () => {
    if (selectedIds.length === 0) return;
    assignRole(selectedIds, bulkRole);
    setSelectedIds([]);
    setIsBulkOpen(false);
  };

  return (
    <div className="mx-auto w-full max-w-7xl px-4 py-8 md:px-8">
      <div className="mb-12">
        <h1 className="text-4xl font-black tracking-tight text-on-surface md:text-5xl">
          Quản lý phân quyền người dùng
        </h1>
        <p className="mt-4 text-lg text-on-surface-variant">
          Xem và quản lý vai trò truy cập của thành viên trong hệ thống.
        </p>
      </div>

      <div className="mb-12 grid grid-cols-1 gap-6 md:grid-cols-2 xl:grid-cols-4">
        <StatCard label="Tổng số người dùng" value={totalUsers} />
        <StatCard label="Viewer" value={roleCounts.Viewer} dotClass={roleDots.Viewer} />
        <StatCard label="Editor" value={roleCounts.Editor} dotClass={roleDots.Editor} />
        <StatCard
          label="Approver"
          value={roleCounts.Approver}
          dotClass={roleDots.Approver}
        />
      </div>

      <div className="mb-8 flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div className="flex flex-col gap-4 sm:flex-row">
          <label className="flex h-12 w-full items-center gap-3 bg-surface-container-low px-4 text-on-surface-variant sm:w-[420px]">
            <span className="material-symbols-outlined text-[22px]">search</span>
            <input
              value={searchQuery}
              onChange={(event) => setSearchQuery(event.target.value)}
              className="w-full border-none bg-transparent text-base text-on-surface placeholder:text-on-surface-variant focus:ring-0"
              placeholder="Tìm kiếm theo tên hoặc email..."
              type="search"
            />
          </label>

          <label className="relative h-12 min-w-48 bg-surface-container-low">
            <select
              value={roleFilter}
              onChange={(event) => setRoleFilter(event.target.value as UserRole | "All")}
              className="h-full w-full appearance-none border-none bg-transparent px-5 pr-11 text-base font-medium text-on-surface focus:ring-0"
            >
              <option value="All">Tất cả vai trò</option>
              {roles.map((role) => (
                <option key={role} value={role}>
                  {role}
                </option>
              ))}
            </select>
            <span className="material-symbols-outlined pointer-events-none absolute right-4 top-1/2 -translate-y-1/2 text-[22px] text-on-surface-variant">
              expand_more
            </span>
          </label>
        </div>

        <button
          type="button"
          onClick={() => setIsBulkOpen(true)}
          className="inline-flex h-12 items-center justify-center gap-3 bg-primary px-6 text-sm font-bold text-on-primary shadow-sm transition-colors hover:bg-primary-dim disabled:cursor-not-allowed disabled:opacity-50"
          disabled={selectedIds.length === 0}
        >
          <span className="material-symbols-outlined text-[21px]">group_add</span>
          Gán vai trò hàng loạt
          {selectedIds.length > 0 && (
            <span className="rounded-full bg-white/20 px-2 py-0.5 text-xs">
              {selectedIds.length}
            </span>
          )}
        </button>
      </div>

      <section className="overflow-hidden border border-outline-variant/10 bg-white shadow-sm">
        <div className="overflow-x-auto">
          <table className="w-full min-w-[980px] text-left">
            <thead className="border-b border-outline-variant/10 bg-surface-bright text-sm uppercase tracking-wide text-on-surface-variant">
              <tr>
                <th className="w-20 px-8 py-6">
                  <input
                    aria-label="Chọn tất cả người dùng đang hiển thị"
                    checked={allVisibleSelected}
                    onChange={toggleAllVisible}
                    type="checkbox"
                    className="h-5 w-5 rounded border-outline-variant text-tertiary focus:ring-tertiary"
                  />
                </th>
                <th className="px-4 py-6 font-bold">Người dùng</th>
                <th className="px-4 py-6 font-bold">Email</th>
                <th className="px-4 py-6 font-bold">Vai trò</th>
                <th className="px-4 py-6 font-bold">Ngày tạo</th>
                <th className="px-4 py-6 font-bold">Trạng thái</th>
                <th className="px-4 py-6 font-bold">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-outline-variant/10">
              {displayedUsers.map((user) => (
                <tr key={user.id} className="transition-colors hover:bg-surface-bright">
                  <td className="px-8 py-5">
                    <input
                      aria-label={`Chọn ${user.name}`}
                      checked={selectedIds.includes(user.id)}
                      onChange={() => toggleUser(user.id)}
                      type="checkbox"
                      className="h-5 w-5 rounded border-outline-variant text-tertiary focus:ring-tertiary"
                    />
                  </td>
                  <td className="px-4 py-5">
                    <div className="flex items-center gap-4">
                      {user.avatarUrl ? (
                        <img
                          src={user.avatarUrl}
                          alt=""
                          className="h-10 w-10 rounded-full object-cover"
                        />
                      ) : (
                        <div className="flex h-10 w-10 items-center justify-center rounded-full bg-secondary-container text-sm font-bold text-on-secondary-container">
                          {user.initials}
                        </div>
                      )}
                      <span className="max-w-44 text-base font-semibold text-on-surface">
                        {user.name}
                      </span>
                    </div>
                  </td>
                  <td className="px-4 py-5 text-base text-on-surface-variant">
                    {user.email}
                  </td>
                  <td className="px-4 py-5">
                    <span
                      className={`inline-flex min-w-20 justify-center rounded-full px-3 py-1 text-xs font-bold uppercase tracking-wide ${roleStyles[user.role]}`}
                    >
                      {user.role}
                    </span>
                  </td>
                  <td className="px-4 py-5 text-base text-on-surface-variant">
                    {user.createdAt}
                  </td>
                  <td className="px-4 py-5">
                    <span className="inline-flex items-center gap-2 text-sm font-medium text-on-surface">
                      <span
                        className={`h-2 w-2 rounded-full ${
                          user.status === "Active" ? "bg-emerald-500" : "bg-outline-variant"
                        }`}
                      />
                      {user.status}
                    </span>
                  </td>
                  <td className="px-4 py-5">
                    <label className="sr-only" htmlFor={`role-${user.id}`}>
                      Đổi vai trò của {user.name}
                    </label>
                    <select
                      id={`role-${user.id}`}
                      value={user.role}
                      onChange={(event) =>
                        assignRole([user.id], event.target.value as UserRole)
                      }
                      className="border-outline-variant/40 bg-white text-sm font-semibold text-on-surface focus:border-tertiary focus:ring-tertiary"
                    >
                      {roles.map((role) => (
                        <option key={role} value={role}>
                          {role}
                        </option>
                      ))}
                    </select>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex flex-col gap-4 border-t border-outline-variant/10 px-8 py-6 text-base text-on-surface-variant sm:flex-row sm:items-center sm:justify-between">
          <span>
            Hiển thị 1 đến {displayedUsers.length} trong {totalUsers.toLocaleString("en-US")}
          </span>
          <div className="flex items-center gap-4">
            <button
              type="button"
              className="material-symbols-outlined p-2 text-outline transition-colors hover:text-on-surface"
              aria-label="Trang trước"
            >
              chevron_left
            </button>
            <button
              type="button"
              className="material-symbols-outlined p-2 text-on-surface transition-colors hover:text-tertiary"
              aria-label="Trang sau"
            >
              chevron_right
            </button>
          </div>
        </div>
      </section>

      {isBulkOpen && (
        <div className="fixed inset-0 z-[90] flex items-center justify-center bg-black/30 p-4 backdrop-blur-sm">
          <div className="w-full max-w-md bg-white p-6 shadow-2xl">
            <div className="mb-5 flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold text-on-surface">
                  Gán vai trò hàng loạt
                </h2>
                <p className="mt-1 text-sm text-on-surface-variant">
                  Áp dụng vai trò mới cho {selectedIds.length} người dùng đã chọn.
                </p>
              </div>
              <button
                type="button"
                onClick={() => setIsBulkOpen(false)}
                className="material-symbols-outlined p-1 text-on-surface-variant hover:text-on-surface"
                aria-label="Đóng"
              >
                close
              </button>
            </div>

            <label className="mb-6 block">
              <span className="mb-2 block text-sm font-semibold text-on-surface">
                Vai trò mới
              </span>
              <select
                value={bulkRole}
                onChange={(event) => setBulkRole(event.target.value as UserRole)}
                className="w-full border-outline-variant/40 bg-white text-on-surface focus:border-tertiary focus:ring-tertiary"
              >
                {roles.map((role) => (
                  <option key={role} value={role}>
                    {role}
                  </option>
                ))}
              </select>
            </label>

            <div className="flex justify-end gap-3">
              <button
                type="button"
                onClick={() => setIsBulkOpen(false)}
                className="px-4 py-2 text-sm font-semibold text-on-surface hover:bg-surface-container"
              >
                Hủy
              </button>
              <button
                type="button"
                onClick={applyBulkRole}
                className="bg-tertiary px-4 py-2 text-sm font-bold text-on-tertiary hover:bg-tertiary-dim"
              >
                Áp dụng
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
