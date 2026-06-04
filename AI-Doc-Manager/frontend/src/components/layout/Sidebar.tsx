import Link from "next/link";

const navItems = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/documents", label: "Documents" },
  { href: "/documents/upload", label: "Upload" },
  { href: "/approvals", label: "Approvals" },
  { href: "/chat", label: "Chat" },
  { href: "/generate", label: "Generate" },
  { href: "/reports", label: "Reports" },
  { href: "/admin/users", label: "Users" },
  { href: "/admin/roles", label: "Roles" }
];

export function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="brand">
        <strong>AI Doc Manager</strong>
        <span>Operational workspace</span>
      </div>
      <nav className="nav-list" aria-label="Primary navigation">
        {navItems.map((item) => (
          <Link className="nav-link" href={item.href} key={item.href}>
            {item.label}
          </Link>
        ))}
      </nav>
    </aside>
  );
}
