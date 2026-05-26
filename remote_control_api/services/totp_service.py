# -*- coding: utf-8 -*-
import hmac
import hashlib
import time
import base64
import struct

class TOTPService:
    """
    RFC 6238 및 RFC 4226 국제 표준에 기반한 pure-Python TOTP (Time-Based One-Time Password) 인증 엔진입니다.
    외부 라이브러리(pyotp 등)의 패키지 의존성이 전혀 없어, 100% 무중단 안정성과 환경 독립성을 지닙니다.
    """
    @staticmethod
    def _base32_decode(secret: str) -> bytes:
        """Base32 시크릿 문자열을 파싱하며, 생략된 패딩(=)을 동적으로 보정하여 디코딩합니다."""
        # 공백 제거 및 대문자 정형화
        secret = secret.strip().replace(" ", "").upper()
        # 8의 배수로 패딩 맞추기
        missing_padding = len(secret) % 8
        if missing_padding:
            secret += "=" * (8 - missing_padding)
        return base64.b32decode(secret)

    @classmethod
    def generate_totp_code(cls, secret: str, time_step: int = 30) -> str:
        """주어진 secret base32 key에 대해 현재 시간(또는 주어진 시간) 기준의 6자리 OTP 코드를 실시간 생성합니다."""
        key = cls._base32_decode(secret)
        # 30초 단위 카운터 계산
        counter = int(time.time() / time_step)
        # 8바이트 Big-Endian 정수 패킹
        msg = struct.pack(">Q", counter)
        
        # HMAC-SHA1 서명 연산
        digest = hmac.new(key, msg, hashlib.sha1).digest()
        
        # dynamic truncation (동적 절삭)
        offset = digest[-1] & 0x0F
        code_bytes = digest[offset:offset + 4]
        code_int = struct.unpack(">I", code_bytes)[0] & 0x7FFFFFFF
        
        # 6자리 포맷팅
        otp = code_int % 1_000_000
        return f"{otp:06d}"

    @classmethod
    def verify_totp_code(cls, secret: str, code: str, window: int = 1) -> bool:
        """
        제공받은 6자리 일회용 비밀번호(code)가 현재 시각 기준 유효한지 대조 검증합니다.
        네트워크 지연이나 클라이언트 기기 시간 비동기화를 극대화 방어하기 위해 window(기본값 1스텝 = +-30초)를 보정 적용합니다.
        """
        if not code or len(code) != 6 or not code.isdigit():
            return False

        current_time = int(time.time())
        
        # 허용 오차 윈도우 범위(-window ~ +window) 만큼 순회하며 타임스텝 검사
        for offset_step in range(-window, window + 1):
            target_time = current_time + (offset_step * 30)
            counter = int(target_time / 30)
            msg = struct.pack(">Q", counter)
            key = cls._base32_decode(secret)
            
            # 해시 비교
            digest = hmac.new(key, msg, hashlib.sha1).digest()
            offset = digest[-1] & 0x0F
            code_bytes = digest[offset:offset + 4]
            code_int = struct.unpack(">I", code_bytes)[0] & 0x7FFFFFFF
            otp = code_int % 1_000_000
            
            # 비교 일치 시 참 반환
            if f"{otp:06d}" == code:
                return True
                
        return False
