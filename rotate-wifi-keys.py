import requests
import random
import string
import qrcode
from PIL import ImageDraw, ImageFont, Image
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload
from google.cloud import storage
from google.oauth2.service_account import Credentials
from dotenv import load_dotenv
import os

# Change the working directory to the script's directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load .env
load_dotenv()

# Generate Random Password
def generate_password(prefix, length):
    random_suffix = ''.join(random.choices(string.ascii_letters + string.digits, k=length - len(prefix)))
    return prefix + random_suffix

# Unifi Login
def unifi_login(controller_url, username, password):
    login_url = f'{controller_url}/api/login'
    login_data = {'username': username, 'password': password}
    
    session = requests.Session()
    response = session.post(login_url, json=login_data, verify=False)
    
    if response.status_code == 200:
        print('Login successful')
        return session
    else:
        print('Login failed')
        return None

# Update Wi-Fi Password
def update_wifi_password(session, controller_url, site_id, ssid, new_password):
    wlan_url = f'{controller_url}/api/s/{site_id}/rest/wlanconf'
    wlan_response = session.get(wlan_url, verify=False)
    wlan_configs = wlan_response.json()['data']

    wlan_id = None
    for wlan in wlan_configs:
        if wlan['name'] == ssid:
            wlan_id = wlan['_id']
            break

    if wlan_id:
        update_url = f'{controller_url}/api/s/{site_id}/rest/wlanconf/{wlan_id}'
        update_data = {'x_passphrase': new_password}
        update_response = session.put(update_url, json=update_data, verify=False)
        
        if update_response.status_code == 200:
            print(f'Password updated to: {new_password}')
            return True
        else:
            print('Failed to update password')
            return False
    else:
        print('WLAN not found')
        return False

# Generate QR Code
def generate_custom_qr_code(ssid, password, logo_path=None, file_path='wifi_qr_code.png'):
    qr_data = f"WIFI:T:WPA;S:{ssid};P:{password};;"
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=20,
        border=2,
    )
    qr.add_data(qr_data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="#263154", back_color="#d3dbed").convert("RGBA")

    if logo_path:
        logo = Image.open(logo_path)
        logo = logo.reduce(5)
        
        # Calculate the position to place the logo
        pos = ((img.size[0] - logo.size[0]) // 2, (img.size[1] - logo.size[1]) // 2)
        img.paste(logo, pos, logo)

    # Add the password below the QR code
    draw = ImageDraw.Draw(img)
    
    # Use a system font, adjust the path to the font you have on your system
    font_path = "assets/timesbd.ttf"
    font = ImageFont.truetype(font_path, 80)
    
    text = f"Senha: {password}"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Create a new image to add text below the QR code
    new_img_height = img.size[1] + text_height + 10
    new_img = Image.new('RGBA', (img.size[0], new_img_height), "#d3dbed")
    new_img.paste(img, (0, 0))

    # Position the text in the center
    text_x = (new_img.size[0] - text_width) // 2
    text_y = img.size[1] - 30
    draw = ImageDraw.Draw(new_img)
    draw.text((text_x, text_y), text, font=font, fill="#263154")

    new_img.save(file_path)
    print(f'QR Code saved to {file_path}')
    return file_path

# Update Google Drive Image File
def update_google_drive_file(credentials_file, file_id, new_file_path):

    SCOPES = ['https://www.googleapis.com/auth/drive']

    # creds, _ = google.auth.default(scopes=SCOPES)
    # Create credentials using the service account file
    creds = Credentials.from_service_account_file(credentials_file, scopes=SCOPES)

    try:
        # create drive api client
        service = build("drive", "v3", credentials=creds)
        media = MediaFileUpload(
            new_file_path, mimetype="image/png", resumable=True
        )
        # pylint: disable=maybe-no-member
        file = (
            service.files()
            .update(fileId=file_id, supportsAllDrives=True, body={}, media_body=media, fields="id", )
            .execute()
        )
        print(f'File ID: {file.get("id")}')

    except HttpError as error:
        print(f"An error occurred: {error}")

    return file.get("id")

def update_gcs_bucket_file(credentials_file, bucket_name, source_file_name, destination_blob_name):
    # Set the environment variable for the credentials file
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_file

    # Initialize a storage client
    client = storage.Client()

    # Get the bucket
    bucket = client.bucket(bucket_name)

    # Get the blob (file) in the bucket
    blob = bucket.blob(destination_blob_name)

    # Upload the new file to the bucket, replacing the existing one
    blob.upload_from_filename(source_file_name)

    print(f'File {source_file_name} uploaded to {destination_blob_name} in bucket {bucket_name}.')

# Main
def main():

    session = unifi_login(os.getenv('UNIFI_CONTROLLER_URL'), os.getenv('UNIFI_USERNAME'), os.getenv('UNIFI_PASSWORD'))
    if session:
        new_password_1 = generate_password(os.getenv('PASSWORD_PREFIX_1'), 10) # Generates a password of 10 characters with the given prefix
        if update_wifi_password(session, os.getenv('UNIFI_CONTROLLER_URL'), os.getenv('SITE_ID_1'), os.getenv('SSID_1'), new_password_1):
            update_wifi_password(session, os.getenv('UNIFI_CONTROLLER_URL'), os.getenv('SITE_ID_2'), os.getenv('SSID_1'), new_password_1)
            qr_code_path_1 = generate_custom_qr_code(os.getenv('SSID_1'), new_password_1, os.getenv('QR_LOGO_PATH_1'), os.getenv('OUTPUT_FILE_PATH_1'))
            # update_google_drive_file(os.getenv('CREDENTIALS_FILE'), os.getenv('GDRIVE_FILE_ID_1'), os.getenv('OUTPUT_FILE_PATH_1'))
            update_gcs_bucket_file(os.getenv('CREDENTIALS_FILE'), os.getenv('GCS_BUCKET_ID'), os.getenv('OUTPUT_FILE_PATH_1'), os.getenv('OUTPUT_FILE_PATH_1'))

        new_password_2 = generate_password(os.getenv('PASSWORD_PREFIX_2'), 11) # Generates a password of 11 characters with the given prefix
        if update_wifi_password(session, os.getenv('UNIFI_CONTROLLER_URL'), os.getenv('SITE_ID_3'), os.getenv('SSID_2'), new_password_2):
            qr_code_path_2 = generate_custom_qr_code(os.getenv('SSID_2'), new_password_2, os.getenv('QR_LOGO_PATH_2'), os.getenv('OUTPUT_FILE_PATH_2'))
            # update_google_drive_file(os.getenv('CREDENTIALS_FILE'), os.getenv('GDRIVE_FILE_ID_2'), os.getenv('OUTPUT_FILE_PATH_2'))
            update_gcs_bucket_file(os.getenv('CREDENTIALS_FILE'), os.getenv('GCS_BUCKET_ID'), os.getenv('OUTPUT_FILE_PATH_2'), os.getenv('OUTPUT_FILE_PATH_2'))


if __name__ == '__main__':
    main()