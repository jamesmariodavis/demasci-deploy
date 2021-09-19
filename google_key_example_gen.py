import json
import os

# defined in Dockerfile
# when run in prod this variable is not set
GOOGLE_KEY_FILE_PATH = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS', None)

google_key_dict = {
    "type": "service_account",
    "project_id": "project-id-123",
    "private_key_id": "123abc",
    "private_key": "xxx",
    "client_email": "admin-123@project-id-123.iam.gserviceaccount.com",
    "client_id": "123",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/xxx"
}

if __name__ == '__main__':
    print('\nRunning example gcloud key generation.')
    if GOOGLE_KEY_FILE_PATH is None:
        err_str = 'Variable GOOGLE_APPLICATION_CREDENTIALS not set. Possibly using on prod image.'
        raise Exception(err_str)
    if not os.path.exists(GOOGLE_KEY_FILE_PATH):
        msg_str = ("Creating example google credentials at {}.\n"
                   "Replace with valid credentials to use Google Cloud features.\n"
                   "See README.\n").format(GOOGLE_KEY_FILE_PATH)
        print(msg_str)
        with open(GOOGLE_KEY_FILE_PATH, 'w', encoding='utf8') as f:
            json.dump(obj=google_key_dict, fp=f, indent=0)
    else:
        print('Key found at {}\n'.format(GOOGLE_KEY_FILE_PATH))
