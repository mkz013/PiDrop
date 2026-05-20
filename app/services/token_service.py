from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired

class TokenService:
    def __init__(self, secret_key, salt="pidrop-upload"):
        self.serializer = URLSafeTimedSerializer(secret_key)
        self.salt = salt

    def generate_upload_token(self, purpose="qr-upload"):
        return self.serializer.dumps({"purpose": purpose}, salt=self.salt)

    def verify_upload_token(self, token, max_age=600):
        try:
            data = self.serializer.loads(token, salt=self.salt, max_age=max_age)
            return True, data
        except SignatureExpired:
            return False, "expired"
        except BadSignature:
            return False, "invalid"