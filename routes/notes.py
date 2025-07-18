# ...existing code...

@router.get(
    "/",
    response_model=list[schemas.NoteOut],
    summary="Барлық ескертпелерді алу",
    description="Аутентификацияланған қолданушының барлық ескертпелерін қайтарады (кэш қолданылады).",
    responses={
        200: {
            "description": "Ескертпелер тізімі сәтті қайтарылды",
            "content": {
                "application/json": {
                    "example": [
                        {"id": 1, "text": "Сабаққа дайындалу", "created_at": "2024-05-01T12:00:00Z"},
                        {"id": 2, "text": "Жаттығу жасау", "created_at": "2024-05-02T09:00:00Z"}
                    ]
                }
            }
        },
        401: {"description": "Авторизация қажет"}
    },
)
async def get_notes(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    redis: Redis = Depends(get_redis),
):
    cache_key = f"notes:{current_user.id}:list"
    cached = await redis.get(cache_key)
    if cached:
        notes = json.loads(cached)
    else:
        result = await db.execute(
            select(Note).where(Note.owner_id == current_user.id).limit(10)
        )
        notes = result.scalars().all()
        serialized = [schemas.NoteOut.from_orm(note).model_dump() for note in notes]
        await redis.set(cache_key, json.dumps(serialized, default=str), ex=300)
        notes = serialized

    # Мынау — өзгеріс: қосымша хабарлама қайтарылады
    return {
        "message": "Бұл жаңа деплойдан кейінгі жауап!",
        "notes": notes
    }

# ...existing code...