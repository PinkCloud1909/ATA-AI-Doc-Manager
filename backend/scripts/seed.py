from app.core.config import get_settings
from app.core.db import session_scope
from app.modules.iam.application.seed import seed_iam_data


def main() -> None:
    settings = get_settings()
    with session_scope() as session:
        result = seed_iam_data(session, settings=settings)
    print(
        "Seed completed",
        f"admin_username={result['admin_username']}",
        f"admin_role={result['admin_role']}",
    )


if __name__ == "__main__":
    main()
