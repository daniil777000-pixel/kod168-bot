import qrcode
from io import BytesIO
import os

def generate_qr(kod_id: str) -> bytes:
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(kod_id)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    
    return buffer.getvalue()

def save_qr(kod_id: str, save_path: str = "qr_codes/"):
    os.makedirs(save_path, exist_ok=True)
    qr_data = generate_qr(kod_id)
    file_path = os.path.join(save_path, f"{kod_id}.png")
    with open(file_path, "wb") as f:
        f.write(qr_data)
    return file_path
