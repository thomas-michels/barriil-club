from fastapi import UploadFile, HTTPException
from PIL import Image, UnidentifiedImageError, ImageFile

MAX_FILE_SIZE_MB = 25
ALLOWED_IMAGE_FORMATS = {"jpeg", "png", "jpg"}
MAX_MEGA_PIXELS = 60


async def validate_image_file(image: UploadFile) -> str:
    image.file.seek(0, 2)  # vai pro fim
    size_bytes = image.file.tell()
    image.file.seek(0)     # volta pro início

    size_mb = size_bytes / (1024 * 1024)
    if size_mb > MAX_FILE_SIZE_MB:
        raise HTTPException(status_code=400, detail=f"File exceeds {MAX_FILE_SIZE_MB} MB limit")

    # 2) Abre direto do stream (sem copiar pra bytes)
    try:
        with Image.open(image.file) as img:
            fmt = (img.format or "").lower()

            # valida formato
            if fmt not in ALLOWED_IMAGE_FORMATS:
                raise HTTPException(status_code=400, detail="Invalid image format")

            # valida megapixels para evitar explosão de memória na decodificação
            w, h = img.size
            mega_pixels = (w * h) / 1_000_000
            if mega_pixels > MAX_MEGA_PIXELS:
                raise HTTPException(status_code=400, detail="Image too large (pixels)")

            # força leitura mínima pra validar integridade (sem img.verify(), que descarta o objeto)
            ImageFile.LOAD_TRUNCATED_IMAGES = False
            img.load()  # carrega os tiles necessários
    except UnidentifiedImageError:
        raise HTTPException(status_code=400, detail="Invalid image format")

    # 3) reposiciona para quem for ler depois
    image.file.seek(0)
    return fmt
