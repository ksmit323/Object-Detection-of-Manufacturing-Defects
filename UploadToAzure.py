"""
Troubleshooting:
Make sure to add a container and provide the correct name.  It CANNOT be "$logs"
    - Go to "Containers" in the left-hand menu
    - Click "Containers"
    - Add a name, give public access and click "Create"

Make sure to give yourself permissions to your account
    - Go to Access Control (IAM) from the left-hand menu
    - Click on "Role assignments" tab
    - Click "Add"
    - Scroll down to "Storage Data Owner" or "Storage Data Contributor"
    - Click one of these and hit "Next".  Continue through the instructions

If using a SAS token, you will need to add the IP address from whatever board you are using to the permissions
when creating the SAS token. 
"""

from azure.storage.blob import BlobServiceClient
import cv2
import json
from datetime import datetime


class AzureBlobUploader():

    def __init__(self, ip_address):

        # BLOB account information
        account_name = "polarisnnetresults"
        account_key = "Q+OWFsrWK7BRwj/HAi9omIj3VH9Vt63d9WNeGVe3wYeQ1W5j1tLH5UznXfbU7+rhU0IJKecHE6pH+ASt+uCOBA=="

        # VIN number.  TO be set at the time of running neural networok
        self.vin = ""

        #***** Change the container name to the correct IP address *******
        self.container_name = ip_address

        # Create the container client
        connection_string = f"DefaultEndpointsProtocol=https;AccountName={account_name};AccountKey={account_key};EndpointSuffix=core.windows.net"
        self.blob_service_client = BlobServiceClient.from_connection_string(connection_string)
        self.container_client = self.blob_service_client.get_container_client(self.container_name)


    def get_folder_name(self, file_name):
        """Returns the folder name for the given VIN and file name"""
        return f"{self.vin}/{file_name}"


    def upload_blob_to_azure(self, content, file_name):
        """Uploads a file to Azure"""
        blob_client = self.container_client.get_blob_client(self.get_folder_name(file_name))
        blob_client.upload_blob(content)
    

    def generate_error_report(self, e):
        """Creates and uploads an error report to Azure if there is an error"""

        # Create error message
        first_line = str(e).split("\n", 1)[0] # Just need the first line of the error message
        error_message = f"[ERROR] Failed to upload results to Azure: {first_line}"  

        # Upload to Azure, print to console      
        self.upload_blob_to_azure(error_message, f"Error Report_{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")   
        print(error_message)
        print("[INFO] Error report has been uploaded to Azure")
    

    def upload_images(self, object, frame):
        """Converts a frame to an image and uploads to Azure"""
        try:
            # Convert frame to an image
            retval, jpeg_image = cv2.imencode(".jpg", frame) # Ignore retval, it's just a boolean.
            image = jpeg_image.tobytes()

            # Upload image to Azure folder
            blob_name = self.get_folder_name(f"{datetime.now()}_{object}")
            self.upload_blob_to_azure(image, blob_name)
            print("[SUCCESS] Successfully uploaded image to Azure")
            
        except Exception as e:
            self.generate_error_report(e)


    def upload_results(self, date, model_no, max_ci_dict, has_passed):
        """Uploads results to Azure as a JSON"""

        results = {
            "Date": date,
            "VIN": self.vin,
            "Model Number": model_no,
            "Max CI": max_ci_dict,
            "Pass or Fail": has_passed
        }
        json_results = json.dumps(results, indent=2)
        
        try:
            self.upload_blob_to_azure(json_results, f"Inspection Results__{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print("[SUCCESS] Successfully uploaded inspection results to Azure")

        except Exception as e:
            self.generate_error_report(e)
