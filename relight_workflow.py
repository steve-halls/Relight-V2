#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import requests
from io import BytesIO
from PIL import Image
import io
import cloudinary
import cloudinary.uploader
import os
import time
from requests.exceptions import ConnectionError
from dotenv import load_dotenv

load_dotenv()

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())


# Configure Cloudinary
cloudinary.config( 
    cloud_name='dyzismqqu',
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
)

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    # with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
    #     return response.read()
    url = f"http://{server_address}/view?{url_values}"
    try:
        with urllib.request.urlopen(url) as response:
            return response.read()
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.reason}")
        print(f"Requested URL: {url}")
        raise
    except urllib.error.URLError as e:
        print(f"URL Error: {e.reason}")
        print(f"Requested URL: {url}")
        raise

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images



def upload_file(file, subfolder="", overwrite=False):
    try:
        # Wrap file in formdata so it includes filename
        body = {"image": file}
        data = {}
        
        if overwrite:
            data["overwrite"] = "true"
  
        if subfolder:
            data["subfolder"] = subfolder

        resp = requests.post(f"http://{server_address}/upload/image", files=body,data=data)
        
        if resp.status_code == 200:
            data = resp.json()
            # Add the file to the dropdown list and update the widget value
            path = data["name"]
            if "subfolder" in data:
                if data["subfolder"] != "":
                    path = data["subfolder"] + "/" + path
            
        else:
            print(f"{resp.status_code} - {resp.reason}")
    except Exception as error:
        print(error)
    return path


def upload_image_from_url(image_url, subfolder="", overwrite=False):
    try:
        # Download the image from the URL
        response = requests.get(image_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Create a file-like object from the image content
        image_file = BytesIO(response.content)
        
        # Extract the filename from the URL
        filename = image_url.split("/")[-1]
        
        # Create a tuple that mimics a file object as expected by upload_file
        file = (filename, image_file, 'image/jpeg')  # Assuming JPEG, adjust if needed
        
        # Use the existing upload_file function to upload the image
        path = upload_file(file, subfolder, overwrite)
        
        return path
    
    except requests.exceptions.RequestException as e:
        print(f"Error downloading the image: {e}")
    except Exception as e:
        print(f"Error uploading the image: {e}")
    
    return None


def save_to_cloudinary(image_data, node_id):
    # Convert image data to PIL Image
    image = Image.open(io.BytesIO(image_data))
    
    # Save image to a temporary file
    temp_filename = f"{node_id}_temp.png"
    image.save(temp_filename)
    
    # Upload to Cloudinary
    upload_result = cloudinary.uploader.upload(temp_filename)
    
    # Get the URL of the uploaded image
    image_url = upload_result['secure_url']
    
    # Remove the temporary file
    import os
    os.remove(temp_filename)
    
    return image_url

def wait_for_comfyui(max_retries=30, delay=10):
    print("Waiting for ComfyUI to start...")
    for i in range(max_retries):
        try:
            response = requests.get("http://127.0.0.1:8188/")
            if response.status_code == 200:
                print("ComfyUI is ready!")
                return True
        except ConnectionError:
            print(f"Attempt {i+1}/{max_retries}: ComfyUI not ready yet. Waiting {delay} seconds...")
            time.sleep(delay)
    print("Failed to connect to ComfyUI after multiple attempts")
    return False



if __name__ == "__main__":

    if not wait_for_comfyui():
        print("ComfyUI did not start in time. Exiting.")
        exit(1)


    print("Loading workflow...")
    with open("relight_workflow_api.json", "r", encoding="utf-8") as f:
        workflow_jsondata = f.read()

    jsonwf = json.loads(workflow_jsondata)

    print("Loading images...")
    product_image = upload_image_from_url("https://yudhisteer.github.io/Git/product.png", "", True)
    background_image = upload_image_from_url("https://yudhisteer.github.io/Git/background.png", "", True)

    # #set the seed for our KSampler node
    # jsonwf["3"]["inputs"]["seed"] = 5

    jsonwf["1"]["inputs"]["image"] = product_image
    jsonwf["26"]["inputs"]["image"] = background_image

    print("Websocket...")
    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, jsonwf)

    #Commented out code to display the output images:
    print("Saving image...")
    for node_id in images:
        for image_data in images[node_id]:
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            if node_id == '597':
                image_url = save_to_cloudinary(image_data, node_id)
                print(f"Image uploaded to Cloudinary. URL: {image_url}")
            # print(node_id)
            # image.save(f"{node_id}.png")

        


