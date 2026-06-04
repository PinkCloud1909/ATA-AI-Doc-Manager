const users = [
  ["admin", "Administrator", "Active"],
  ["qa.manager", "QA Manager", "Active"],
  ["ops.reviewer", "Operations Reviewer", "Invited"],
];

export default function UsersPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Users</h2>
          <p>Manage account access for document workflows.</p>
        </div>
        <button className="button" type="button">
          Add user
        </button>
      </section>

      <section className="panel">
        <table className="table">
          <thead>
            <tr>
              <th>Username</th>
              <th>Role</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            {users.map(([username, role, status]) => (
              <tr key={username}>
                <td>{username}</td>
                <td>{role}</td>
                <td>{status}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </section>
    </>
  );
}
