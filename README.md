# Relight-V2


# Setup Guide: WSL 2, Docker, and NVIDIA Container Toolkit on Windows

This guide provides a step-by-step process to configure WSL 2 on Windows, install Docker, and set up the NVIDIA Container Toolkit to enable GPU acceleration within Docker containers.

## Prerequisites

Before you begin, ensure that you have:
- A Windows 10 or 11 system with the latest updates.
- A compatible NVIDIA GPU with the latest drivers installed.
- [Docker Desktop](https://www.docker.com/products/docker-desktop) installed on your system.

## Step 1: Enable WSL 2

1. **Enable the WSL Feature**  
   Open PowerShell as an administrator and run the following command to enable the Windows Subsystem for Linux (WSL2) feature:
   ```powershell
   dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
   ```
2. **Set WSL 2 as the Default Version**
   Set WSL 2 as the default version by running:

   ```powershell
   wsl --set-default-version 2
   ```
3. **Install a Linux Distribution**
    Download and install a Linux distribution of your choice from the Microsoft Store (e.g., Ubuntu). Once installed, open the distribution and complete the initial setup.

## Step 2: Install Docker Desktop

1. **Download and Install Docker Desktop**
   Download Docker Desktop from the official website and follow the installation instructions.

2. **Enable WSL 2 Integration**
   During installation, make sure to enable the option to use WSL 2 as the backend. After installation, go to Settings > Resources > WSL Integration and enable integration with your installed WSL distributions.

3. **Enable GPU Support**
   Go to Settings > Resources > GPU and enable the option to expose the GPU to Docker containers.

## Step 3: Install NVIDIA Container Toolkit

1. **Open the WSL 2 Terminal**
   Open your Linux distribution terminal within WSL 2.

2. **Add the NVIDIA Docker Repository**
   Add the repository to your system:

   ```ssh
   distribution=$(. /etc/os-release;echo $ID$VERSION_ID)
   curl -s -L https://nvidia.github.io/nvidia-docker/gpgkey | sudo apt-key add -
   curl -s -L https://nvidia.github.io/nvidia-docker/$distribution/nvidia-docker.list | sudo tee /etc/apt/sources.list.d/nvidia-docker.list
   sudo apt-get update
   ```
3. **Install the NVIDIA Container Toolkit**
   Install the toolkit using:

   ```sh
   sudo apt-get install -y nvidia-docker2
   ```

4. **Restart Docker**
   Restart the Docker service:

   ```sh
   sudo systemctl restart docker
   ```

5. **Verify the Installation**
   Verify that the toolkit is working by running:

   ```sh
   docker run --rm --runtime=nvidia --gpus all ubuntu nvidia-smi
   ```

   Your output should resemble the following output:

   ```sh
   +-----------------------------------------------------------------------------------------+
   | NVIDIA-SMI 550.78                 Driver Version: 550.107.02     CUDA Version: 12.4     |
   |-----------------------------------------+------------------------+----------------------+
   | GPU  Name                 Persistence-M | Bus-Id          Disp.A | Volatile Uncorr. ECC |
   | Fan  Temp   Perf          Pwr:Usage/Cap |           Memory-Usage | GPU-Util  Compute M. |
   |                                         |                        |               MIG M. |
   |=========================================+========================+======================|
   |   0  NVIDIA GeForce GTX 1060 6GB    Off |   00000000:01:00.0  On |                  N/A |
   |  0%   40C    P8             13W /  180W |     226MiB /   6144MiB |      0%      Default |
   |                                         |                        |                  N/A |
   +-----------------------------------------+------------------------+----------------------+
                                                                                            
   +-----------------------------------------------------------------------------------------+
   | Processes:                                                                              |
   |  GPU   GI   CI        PID   Type   Process name                              GPU Memory |
   |        ID   ID                                                               Usage      |
   |=========================================================================================|
   +-----------------------------------------------------------------------------------------+
   ```
   
   If everything is set up correctly, you should see a display of your GPU information.

## Running the Project

1. **Set Project Environment Variables**

   First, define the necessary environment variables for your project:

   ```sh
   export CLOUDINARY_CLOUD_NAME=my_cloud_name
   export CLOUDINARY_API_KEY=my_api_key
   export CLOUDINARY_API_SECRET=my_api_secret

2. **Start the Docker Containers**

   Once the environment variables are set, start the project using Docker Compose:

   ```sh
   docker-compose up
   ```
