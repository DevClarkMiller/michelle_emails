import smtplib, os, random
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv() 

PROMPT_PATH = 'prompt.txt'
SMPT_SERVER = 'smtp.gmail.com'
SMPT_PORT = 587
USER = os.getenv('MAIL_USER')
PASS = os.getenv('MAIL_PASS')
TO = os.getenv('MAIL_TO')
SUBJECT = 'Letter From Clark'
PICS_PATH = os.getenv('PICS_PATH')

def create_prompt():
    prompt = ""
    with open(PROMPT_PATH, 'r') as file:
        prompt = file.read() 

    client = OpenAI(api_key=os.getenv('OPENAI_KEY'))
    completion = client.chat.completions.create(
    model="gpt-4o-mini",
    store=True,
    messages=[
        {"role": "user", "content": prompt}
    ])
    return completion.choices[0].message.content

def get_picture():
    # Get details on the files in the directory
    pics = os.listdir(PICS_PATH)
    pic_path = f"{PICS_PATH}/{random.choice(pics)}" # Get random filename
    with open(pic_path, 'rb') as f:
        img = f.read()

    return img
    


def send_letter():
    body = create_prompt()  # Generates an ai love poem
    # body = 'test'

    # HTML content with the embedded image (base64 encoded in HTML)
    html = f'''\
    <html>
    <head></head>
    <body>
        <h1>{SUBJECT}</h1>
        <p>{body}</p>
        <img w="300px" height="650px" src="cid:image1">
    </body>
    </html>
    '''
    
    msg = MIMEMultipart()
    msg["From"] = USER
    msg["To"] = TO
    msg["Subject"] = SUBJECT
    msg.attach(MIMEText(html, 'html'))

    pic_data = get_picture()

    # Create the image attachment (to make sure the image is sent as an attachment)
    image_attachment = MIMEBase('image', 'jpeg')  # Set the MIME type to match your image format
    image_attachment.set_payload(pic_data)  # Set the image data as payload
    encoders.encode_base64(image_attachment)  # Encode it as base64 for email transmission
    image_attachment.add_header('Content-ID', '<image1>')  # Set Content-ID to match the img tag `cid:image1`
    image_attachment.add_header('Content-Disposition', 'inline', filename="image.jpg")  # Inline image with a filename


    # Attach the image to the message
    msg.attach(image_attachment)

    # Connect to the SMTP server and send email
    with smtplib.SMTP(SMPT_SERVER, SMPT_PORT) as server:
        server.starttls()
        server.login(USER, PASS)
        server.sendmail(USER, [TO], msg.as_string())
        print('Email sent!')



if __name__ == '__main__':
    send_letter()