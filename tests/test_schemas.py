import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))


from pydantic import ValidationError


from app.schemas.user import UserLogin, UserRegister, UserResponce

try:
    user = UserRegister(email="test@mail.com", password="12345678")
    print("Validation is successful",user)
except ValidationError as e:
    print(e)



try:
    user = UserRegister(email="test@mail.com", password="123")
    print("Validation is successful",user)
except ValidationError as e:
    print(e)

try:
    user = UserRegister(email="non-valid-email", password="123")
    print("Validation is successful",user)
except ValidationError as e:
    print(e)