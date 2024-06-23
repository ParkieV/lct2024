from fastapi import APIRouter, HTTPException, Depends, Query

from api.src.configurations.users import get_user_session
from api.src.services.speech2text import transcribe_audio
from api.src.schemas.schemas import AudioSchema



s2t_router = APIRouter(
    tags=['Speech2Text Endpoints'],
    prefix='/s2t'
)


@s2t_router.post("/transcribe")
def get_audio_transcription(user_input: AudioSchema, user_id: str = Query(...), user_session=Depends(get_user_session)):
    return transcribe_audio(user_input.audio)

