# Unifi Wi-Fi Password Rotation and QR Code Generator

This script automates the process of rotating passwords for public and private Wi-Fi networks managed by a Unifi Controller. It uses the Unifi API to update Wi-Fi passwords, uses qrcode library to generate QR codes for easy access, and updates image files in Google Drive with the generated QR codes.

This specific `main()` implementation manages 2 Unifi sites with the same SSID, and a third with a different SSID. Thus creating and updating two different qr-codes in Google Drive. 

## Features

- **Password Generation**: Generates secure random passwords with customizable prefixes and lengths.
- **Unifi API Integration**: Logs into a Unifi Controller and updates the Wi-Fi passwords.
- **QR Code Generation**: Creates QR codes for the new passwords with optional logo embedding.
- **Google Drive Integration**: Updates an existing image file in Google Drive with the new QR code.

## Requirements

- Python 3.x
- `requests` library
- `qrcode` library
- `Pillow` library
- `google-api-python-client` library
- `google-auth` library
- `python-dotenv` library
- A Unifi Controller with API access
- A Google Service Account with access to Google Drive

## Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/davigugu55/unifi-wifi-password-rotation.git
    cd unifi-wifi-password-rotation
    ```

2. Install the required Python libraries:
    ```sh
    pip install requests qrcode[pil] google-api-python-client google-auth python-dotenv
    ```

3. Create a `.env` file in the project root directory and add the following environment variables:
    ```env
    UNIFI_CONTROLLER_URL=https://your-unifi-controller-url
    UNIFI_USERNAME=your-unifi-username
    UNIFI_PASSWORD=your-unifi-password

    SITE_ID_1=your-site-id-1
    SITE_ID_2=your-site-id-2
    SITE_ID_3=your-site-id-3

    SSID_1=your-ssid-1
    SSID_2=your-ssid-2

    PASSWORD_PREFIX_1=prefix-for-password-1
    PASSWORD_PREFIX_2=prefix-for-password-2

    QR_LOGO_PATH_1=path-to-logo-1.png
    QR_LOGO_PATH_2=path-to-logo-2.png

    OUTPUT_FILE_PATH_1=output-path-1.png
    OUTPUT_FILE_PATH_2=output-path-2.png

    CREDENTIALS_FILE=path-to-google-service-account.json

    GDRIVE_FILE_ID_1=google-drive-file-id-1
    GDRIVE_FILE_ID_2=google-drive-file-id-2
    ```

## Usage

Run the script using Python:

```sh
python rotate-wifi-keys.py
```

The script will:

1. Log into the Unifi Controller.
2. Generate new passwords for the specified SSIDs.
3. Update the passwords in the Unifi Controller.
4. Generate QR codes with the new passwords.
5. Update the QR code images in Google Drive.

## Generated QR-Code Example
![Example QR-Code](/assets/qr-code%20example.png)


## Code Overview

- `generate_password(prefix, length)`: Generates a random password with the specified prefix and length.
- `unifi_login(controller_url, username, password)`: Logs into the Unifi Controller and returns a session.
- `update_wifi_password(session, controller_url, site_id, ssid, new_password)`: Updates the Wi-Fi password for a specified SSID.
- `generate_custom_qr_code(ssid, password, logo_path, file_path)`: Generates a QR code for the specified SSID and password, with an optional logo.
- `update_google_drive_file(credentials_file, file_id, new_file_path)`: Updates an image file in Google Drive with the new QR code.
- `main()`: Main function to execute the password rotation and QR code generation process.

## Acknowledgements

This project uses the following libraries and APIs:

- [requests](https://docs.python-requests.org/)
- [qrcode](https://github.com/lincolnloop/python-qrcode)
- [Pillow](https://python-pillow.org/)
- [Google API Client](https://developers.google.com/api-client-library/python)
- [dotenv](https://github.com/theskumar/python-dotenv)
- [Unifi API](https://ubntwiki.com/products/software/unifi-controller/api)

Feel free to customize the script and `README.md` file according to your specific needs and project details.