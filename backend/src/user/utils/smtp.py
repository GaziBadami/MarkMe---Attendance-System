import json
import logging
import requests

from src.config import Config
from src.user.models import UserRoles

templates = {"faculty": """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Welcome to MarkMe</title>
</head>
<body style="margin:0; padding:0; background-color:#f5f7fa; font-family: Arial, sans-serif;">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f5f7fa; padding:40px 0;">
    <tr>
      <td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="480" style="background:#ffffff; border-radius:12px; padding:40px 30px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
          
          <!-- Logo -->
          <tr>
            <td style="padding-bottom:20px;">
              <h1 style="margin:0; font-size:28px; color:#111111; font-weight:600;">MarkMe</h1>
            </td>
          </tr>
          
          <!-- Title -->
          <tr>
            <td style="padding-bottom:10px;">
              <h2 style="margin:0; font-size:22px; color:#111111; font-weight:600;">Your Faculty Account is Ready 🎉</h2>
            </td>
          </tr>

          <!-- Message -->
          <tr>
            <td style="padding:10px 0 25px; color:#555555; font-size:15px; line-height:1.6;">
              <p style="margin:0;">Hello <strong>{firstname}</strong>,</p>
              <p style="margin:10px 0 0;">An Administrator has created a <strong>faculty account</strong> for you in <strong>MarkMe</strong>. You can now log in and start using the platform.</p>
            </td>
          </tr>

          <!-- Credentials -->
          <tr>
            <td>
              <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb; border-radius:8px; overflow:hidden; font-size:14px; text-align:left;">
                <tr>
                  <td style="padding:12px 16px; background:#f9fafb; font-weight:600;">Username</td>
                  <td style="padding:12px 16px;">{email}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px; background:#f9fafb; font-weight:600;">Password</td>
                  <td style="padding:12px 16px;">{password}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA Button -->
          <tr>
            <td style="padding:30px 0;">
              <a href="https://markme.com/login" target="_blank" 
                 style="background-color:#2563eb; color:#ffffff; text-decoration:none; padding:14px 28px; border-radius:8px; font-size:15px; font-weight:600; display:inline-block;">
                Login to MarkMe
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="color:#999999; font-size:12px; line-height:1.5; border-top:1px solid #f0f0f0; padding-top:20px;">
              <p style="margin:0;">© {year} MarkMe. All rights reserved.</p>
              <p style="margin:5px 0 0;">This is an automated email. Please do not reply.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
""",
"student":"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Welcome to MarkMe</title>
</head>
<body style="margin:0; padding:0; background-color:#f5f7fa; font-family: Arial, sans-serif;">
  <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="100%" style="background-color:#f5f7fa; padding:40px 0;">
    <tr>
      <td align="center">
        <table role="presentation" cellpadding="0" cellspacing="0" border="0" width="480" style="background:#ffffff; border-radius:12px; padding:40px 30px; text-align:center; box-shadow:0 2px 10px rgba(0,0,0,0.05);">
          
          <!-- Logo -->
          <tr>
            <td style="padding-bottom:20px;">
              <h1 style="margin:0; font-size:28px; color:#111111; font-weight:600;">MarkMe</h1>
            </td>
          </tr>
          
          <!-- Title -->
          <tr>
            <td style="padding-bottom:10px;">
              <h2 style="margin:0; font-size:22px; color:#111111; font-weight:600;">Your Student Account is Ready 🎓</h2>
            </td>
          </tr>

          <!-- Message -->
          <tr>
            <td style="padding:10px 0 25px; color:#555555; font-size:15px; line-height:1.6;">
              <p style="margin:0;">Hello <strong>{firstname}</strong>,</p>
              <p style="margin:10px 0 0;">We’re excited to welcome you to <strong>MarkMe</strong> 🎉. A <strong>student account</strong> has been created for you by GLS. You can now log in and access your courses, attendance, and more.</p>
            </td>
          </tr>

          <!-- Credentials -->
          <tr>
            <td>
              <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e5e7eb; border-radius:8px; overflow:hidden; font-size:14px; text-align:left;">
                <tr>
                  <td style="padding:12px 16px; background:#f9fafb; font-weight:600;">Username</td>
                  <td style="padding:12px 16px;">{email}</td>
                </tr>
                <tr>
                  <td style="padding:12px 16px; background:#f9fafb; font-weight:600;">Password</td>
                  <td style="padding:12px 16px;">{password}</td>
                </tr>
              </table>
            </td>
          </tr>

          <!-- CTA Button -->
          <tr>
            <td style="padding:30px 0;">
              <a href="https://markme.com/login" target="_blank" 
                 style="background-color:#16a34a; color:#ffffff; text-decoration:none; padding:14px 28px; border-radius:8px; font-size:15px; font-weight:600; display:inline-block;">
                Login to MarkMe
              </a>
            </td>
          </tr>

          <!-- Footer -->
          <tr>
            <td style="color:#999999; font-size:12px; line-height:1.5; border-top:1px solid #f0f0f0; padding-top:20px;">
              <p style="margin:0;">© {year} MarkMe. All rights reserved.</p>
              <p style="margin:5px 0 0;">This is an automated email. Please do not reply.</p>
            </td>
          </tr>

        </table>
      </td>
    </tr>
  </table>
</body>
</html>
"""}

def send_email(receiver: str, subject: str, user: dict, role: str):
    try:
        url = Config.BREVO_URL

        headers = {
            'accept': 'application/json',
            'content-type': 'application/json',
            'api-key': Config.BREVO_API_KEY
            }
        if role == "faculty":
          html_content = templates["faculty"]
        elif role == "student":
            html_content = templates["student"]

        html_content = html_content.format(
              firstname=user.get("firstname"),
              email=user.get("email"),
              password=user.get("password"),
              year=2025
          )

        payload = json.dumps({
            "sender": {
                "email": Config.BREVO_SENDER_EMAIL
            },
            "to": [
                {
                "email": receiver
                }
            ],
            "subject": subject,
            "htmlContent": html_content
        })

        response = requests.request("POST", url, headers=headers, data=payload)

        return True
    except Exception as e:
        logging.exception("=== Brevo Email Error: ===", str(e))
        return False