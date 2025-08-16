# resize_image.py
from fastapi import UploadFile
from PIL import Image, ImageOps
from tempfile import NamedTemporaryFile
from pathlib import Path

async def resize_image(upload_image: UploadFile, size=(400, 400)) -> UploadFile:
    upload_image.file.seek(0)
    with Image.open(upload_image.file) as img:
        img = ImageOps.exif_transpose(img)

        # Converte para RGB se necessário (evita canal alfa virar fundo preto)
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # Redimensiona mantendo proporção e depois pad para tamanho exato
        img = ImageOps.contain(img, size)               # reduz mantendo proporção
        img = ImageOps.pad(img, size, color="white")    # bordas para bater o size exato

        # Salva em arquivo temporário (evita guardar tudo em BytesIO na RAM)
        with NamedTemporaryFile(delete=False, suffix=".jpeg") as tmp:
            img.save(tmp, format="JPEG", quality=85, optimize=True)
            tmp_path = Path(tmp.name)

    # Reabre o arquivo temporário como stream para o UploadFile
    f = tmp_path.open("rb")
    new_name = f"{Path(upload_image.filename).stem}.jpeg"
    return UploadFile(filename=new_name, file=f, headers={"content_type": "image/jpeg"})
