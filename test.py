import os
from dotenv import load_dotenv

load_dotenv(override=True)

print(os.getenv("CLIENT_ID"))
print(os.getenv("CLIENT_SECRET"))
print(os.getenv("CODE"))
print(os.getenv("REDIRECT_URI"))