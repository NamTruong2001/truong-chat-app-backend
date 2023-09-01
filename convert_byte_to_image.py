from PIL import Image
from io import BytesIO
import requests
import base64

URL = "https://qldt.hanu.edu.vn/api/sms/w-locthongtinimagesinhvien?"
ma_sv = "1906080013"
query = f"MaSV={ma_sv}"
token = open("token.txt", "r").read()
response = requests.post(url=f"{URL}{query}", headers={
    "Authorization": f"Bearer {token}"
}).json()

data_url = response["data"]["thong_tin_sinh_vien"]["image"]

# data_url = open("quynhanh.txt", "r").read()

# Extract the base64-encoded string from the data URL
base64_string = data_url

# Decode the base64 string to bytes
image_bytes = base64.b64decode(base64_string)

# Create a BytesIO object to read the image bytes as a stream
image_stream = BytesIO(image_bytes)

# Open the image using PIL
image = Image.open(image_stream)

# Now you can display or process the image as needed
image.show()
