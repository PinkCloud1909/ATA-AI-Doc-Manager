export default function LoginPage() {
  return (
    <main className="workspace">
      <section className="page-header">
        <div>
          <h2>Sign In</h2>
          <p>Use your document-management account to access the workspace.</p>
        </div>
      </section>
      <section className="panel">
        <form className="form">
          <div className="field">
            <label htmlFor="username">Username</label>
            <input id="username" autoComplete="username" placeholder="admin" />
          </div>
          <div className="field">
            <label htmlFor="password">Password</label>
            <input id="password" autoComplete="current-password" type="password" />
          </div>
          <button className="button" type="button">
            Sign in
          </button>
        </form>
      </section>
    </main>
  );
}
