import smtplib
import ssl
import math, random


def generateOTP() :
 
    digits = "0123456789"
    OTP = ""
 
    for i in range(4) :
        OTP += digits[math.floor(random.random() * 10)]
 
    return OTP



def send_otp(usr_email):
    """
    This functin ask for designated email which is user's email to send
    the OTP code. 
    """
    context = ssl.create_default_context()
    otp = generateOTP()

    with smtplib.SMTP_SSL("smtp.gmail.com", 465, context=context) as server:
        server.login("cupidyhepta@gmail.com", "ykzt srhc qavt zbnb")
        message = f"""\
        Subject: Sending OTP

        {otp}
        """
        server.sendmail("cupidyhepta@gmail.com", usr_email, message)
    return otp
