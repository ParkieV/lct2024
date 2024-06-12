from fastapi import APIRouter, Depends, HTTPException, status

from app.schemas.organization import OrganizationDTO, OrganizationListDTO
from app.shared.jwt import JWT
from app.persistence.repositories.pg_repository import OrganizationRepository
from app.services.pg_service import PostgresServiceFacade


router = APIRouter(prefix="/organization")


@router.post("/organizations",
             response_model=OrganizationListDTO | None,
             dependencies=[Depends(JWT.check_access_token)],
             summary="Get information about all organizations")
async def get_orgs(*,
                   session=Depends(PostgresServiceFacade.get_async_session),
                   allow_none: bool = True):
    org_repo = OrganizationRepository()

    try:
        result = await org_repo.get_objects(allow_none=allow_none, out_schema=OrganizationDTO, session=session)
        if result:
            return OrganizationListDTO(orgList=result)
        return None
    except HTTPException as err:
        raise err
    except Exception as err:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                            detail=err)
