import { Sidebar } from "@/components/layout/Sidebar";

export default function MainLayout({
  children
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <div className="app-shell">
      <Sidebar />
      <main className="content">
        <header className="topbar">
          <div>
            <h1>Document operations</h1>
            <p>Review, approve, search, and generate controlled documents.</p>
          </div>
          <a className="button secondary" href="/login">
            Sign in
          </a>
        </header>
        <div className="workspace">{children}</div>
      </main>
    </div>
  );
}
