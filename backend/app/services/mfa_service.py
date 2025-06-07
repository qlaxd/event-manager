"""
Service layer for Multi-Factor Authentication (MFA) operations.
"""
import base64
import io
from datetime import datetime

import pyotp
import qrcode
from fastapi import HTTPException, status
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import SecurityUtils
from app.models.auth import MFABackupCode
from app.models.user import User
from app.services.audit_service import log_security_event


class MFAService:
    """
    Encapsulates all business logic for MFA operations.
    """

    @staticmethod
    def _generate_qr_code(user_email: str, secret: str) -> str:
        """
        Generate a data URI for a QR code for MFA setup.
        
        Args:
            user_email: The user's email address.
            secret: The MFA secret key.
        
        Returns:
            A base64 encoded PNG image data URI.
        """
        totp_uri = pyotp.totp.TOTP(secret).provisioning_uri(
            name=user_email, issuer_name="UCC Event Manager"
        )

        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        qr.add_data(totp_uri)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        img_buffer = io.BytesIO()
        img.save(img_buffer, format="PNG")
        img_str = base64.b64encode(img_buffer.getvalue()).decode()

        return f"data:image/png;base64,{img_str}"

    @staticmethod
    async def _create_mfa_backup_codes(
        db: AsyncSession, user: User, codes: list[str]
    ) -> None:
        """
        Create and store hashed MFA backup codes in the database, removing any old ones.
        
        Args:
            db: The async database session.
            user: The user for whom to create backup codes.
            codes: A list of plaintext backup codes.
        """
        stmt = select(MFABackupCode).where(MFABackupCode.user_id == user.id)
        result = await db.execute(stmt)
        for code in result.scalars().all():
            await db.delete(code)

        for code in codes:
            backup_code = MFABackupCode(
                code_hash=SecurityUtils.get_password_hash(code), user_id=user.id
            )
            db.add(backup_code)

        await db.commit()

    @staticmethod
    async def enable_mfa(db: AsyncSession, user: User, password: str, ip_address: str):
        """
        Initiates the MFA enablement process for a user.
        
        Verifies the user's password, generates a new MFA secret, QR code,
        and a set of backup codes.
        """
        if not SecurityUtils.verify_password(password, user.hashed_password):
            await log_security_event(
                db=db,
                event_type="MFA_ENABLE_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "invalid_password"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )

        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled"
            )

        secret = SecurityUtils.generate_mfa_secret()
        qr_code = MFAService._generate_qr_code(user.email, secret)
        backup_codes = SecurityUtils.generate_backup_codes()

        user.mfa_secret = secret
        await db.commit()

        await log_security_event(
            db=db,
            event_type="MFA_ENABLE_INITIATED",
            user_id=user.id,
            ip_address=ip_address,
        )

        return {"secret": secret, "qr_code": qr_code, "backup_codes": backup_codes}

    @staticmethod
    async def verify_mfa_setup(
        db: AsyncSession, user: User, mfa_code: str, ip_address: str
    ):
        """
        Verifies the TOTP code to complete the MFA setup process.
        """
        if user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is already enabled"
            )

        if not user.mfa_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA setup not initiated"
            )

        if not SecurityUtils.verify_mfa_token(user.mfa_secret, mfa_code):
            await log_security_event(
                db=db,
                event_type="MFA_VERIFY_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "invalid_code"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
            )

        user.mfa_enabled = True
        backup_codes = SecurityUtils.generate_backup_codes()
        await MFAService._create_mfa_backup_codes(db, user, backup_codes)

        await db.commit()
        await log_security_event(
            db=db, event_type="MFA_ENABLED", user_id=user.id, ip_address=ip_address
        )

        return {"message": "MFA enabled successfully"}

    @staticmethod
    async def disable_mfa(
        db: AsyncSession, user: User, password: str, mfa_code: str, ip_address: str
    ):
        """
        Disables MFA for a user after verifying password and a valid MFA code.
        """
        if not user.mfa_enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="MFA is not enabled"
            )

        if not SecurityUtils.verify_password(password, user.hashed_password):
            await log_security_event(
                db=db,
                event_type="MFA_DISABLE_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "invalid_password"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password"
            )

        if not SecurityUtils.verify_mfa_token(user.mfa_secret, mfa_code):
            await log_security_event(
                db=db,
                event_type="MFA_DISABLE_FAILURE",
                user_id=user.id,
                ip_address=ip_address,
                details={"reason": "invalid_mfa_code"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid MFA code"
            )

        user.mfa_enabled = False
        user.mfa_secret = None

        stmt = select(MFABackupCode).where(MFABackupCode.user_id == user.id)
        result = await db.execute(stmt)
        for code in result.scalars().all():
            await db.delete(code)

        await db.commit()
        await log_security_event(
            db=db, event_type="MFA_DISABLED", user_id=user.id, ip_address=ip_address
        )

        return {"message": "MFA disabled successfully"}

    @staticmethod
    async def verify_login_code(
        db: AsyncSession, user: User, mfa_code: str, ip_address: str
    ) -> bool:
        """
        Verifies a TOTP or backup code during the login flow.
        If a backup code is used, it is marked as such.
        """
        if user.mfa_secret and SecurityUtils.verify_mfa_token(
            user.mfa_secret, mfa_code
        ):
            return True

        stmt = select(MFABackupCode).where(
            and_(
                MFABackupCode.user_id == user.id, MFABackupCode.used_at.is_(None)
            )
        )
        result = await db.execute(stmt)
        backup_codes = result.scalars().all()

        for backup_code in backup_codes:
            if SecurityUtils.verify_password(mfa_code, backup_code.code_hash):
                backup_code.used_at = datetime.utcnow()
                await db.commit()
                return True

        await log_security_event(
            db=db,
            event_type="MFA_FAILURE",
            user_id=user.id,
            ip_address=ip_address,
            details={"reason": "invalid_mfa_code"},
        )
        return False
