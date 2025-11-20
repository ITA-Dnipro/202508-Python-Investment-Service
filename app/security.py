from fastapi import Header, HTTPException, status


def get_current_investor_id(
    user_id: str | None = Header(
        default=None,
        convert_underscores=False,
        alias="user-id"
    ),
    role: str | None = Header(
        default=None,
        convert_underscores=False,
        alias="role"
    ),
) -> int:
    
    if not user_id or not role:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing auth context headers",
        )

    if role.lower() != "investor":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Investor role required",
        )

    try:
        return int(user_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user-id header",
        )
