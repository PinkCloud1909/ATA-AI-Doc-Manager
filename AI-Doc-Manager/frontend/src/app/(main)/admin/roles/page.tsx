const roles = [
  ["Administrator", "Full platform access"],
  ["QA Manager", "Approve and return controlled documents"],
  ["Reviewer", "Review assigned documents and add comments"],
  ["Viewer", "Read approved documents"]
];

export default function RolesPage() {
  return (
    <>
      <section className="page-header">
        <div>
          <h2>Roles</h2>
          <p>Permission groups used by approval and review workflows.</p>
        </div>
      </section>

      <section className="panel">
        <ul className="list">
          {roles.map(([name, description]) => (
            <li key={name}>
              <div>
                <strong>{name}</strong>
                <p className="muted">{description}</p>
              </div>
              <button className="button secondary" type="button">
                Edit
              </button>
            </li>
          ))}
        </ul>
      </section>
    </>
  );
}
