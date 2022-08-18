import os
import pyotp
import qrcode


# Create the base for the TOTP
base_for_qr_totp = pyotp.random_base32()

# Create the QR code for FreeOTP or Google Authenticator to read
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(pyotp.totp.TOTP(base_for_qr_totp).provisioning_uri(name='pinko@folktales.hu', issuer_name='Private Note'))
qr.make(fit=True)

img = qr.make_image(fill_color="black", back_color="white")

# Save the QR code image to use with FreeOTP or Google Authenticator
img.save("qrcode_new_mfa.png")


salt = os.urandom(32)

save_for_later = f"base for otp qr: {base_for_qr_totp}, salt for key generation: {salt}"

# Save the TOTP base to use in the private note application
with open('random_base.txt', 'w') as f:
    f.write(save_for_later)
