# **Installation and Usage of Singularity on Linux for Docker Image Conversion**

## 1. Installation

### 1.1 Singularity

To install Singularity on a Linux system (Ubuntu example), execute the following commands:

```bash
sudo apt update
sudo apt install -y singularity-container
```

To verify the installation:

```bash
singularity --version
```

But it usually not works very well. So here is also another way to do install the singularityCE software. You can find if from the link below:
[guides on singularity install](https://docs.sylabs.io/guides/3.8/admin-guide/installation.html#id1)

- You need to install some dependencies first.
- Install go.
- Download SingularityCE.
- Compile Singularity with make command.

### 1.2 Docker

You can download docker desktop on Linux, which is the easiest way to use docker.

#### Build the image

To build the docker image: clone the repository, and use  command below.

```bash
git clone https://github.com/COMS7900/HW.git
cd docker_my
docker compose up -d
```

This will use the `docker compose.yaml` file, open a container and create an image. Also you can use the `docker file` with command below, which just gives you an image tag `mymage:latest`

```bash
docker build -t myimage:latest .
```

#### Push image to Docker hub

1. Use docker desktop
2. Login docker in your terminal. Re-tag the image with your docker username in it.

```bash
docker login
docker tag myapp:latest <your-dockerhub-username>/myapp:latest
docker push <your-dockerhub-username>/myapp:latest
```

## **2. Pulling a Docker Image and Converting to SIF**

To download a Docker image from Docker Hub and convert it into a Singularity Image Format (SIF) file, use the following command:

```
singularity pull myimage.sif docker://myusername/myapp:latest
```

- `docker://your_image:latest` specifies the Docker Hub image (`your_image:latest` or any tag you put).
- `myimage.sif` is the resulting Singularity container file.

## **3. Running the Singularity Container**

### **3.1 Launching an Interactive Shell**

To start an interactive session within the Singularity container:

```
singularity shell myimage.sif
```

Once inside, standard shell commands can be executed:

```
Singularity> ls /
Singularity> exit
```

### **3.2 Executing the Container**

To execute a specific command inside the Singularity container:

```
singularity exec myimage.sif 
```

### **3.3 Running the Default Entrypoint**

If the original Docker image contains an `ENTRYPOINT`, it can be executed with:

```
singularity run myimage.sif
```

## 4. Summary of Key Commands

### **4.1 Installation**

Use command if you can. Or otherwise, follow the instructions on the guide file.

### 4.2 Image Conversion

```
singularity pull myimage.sif docker://myusername/myapp:latest
```

### **4.3 Container Execution**

```
singularity shell myimage.sif
singularity exec myimage.sif <command>
singularity run myimage.sif
```

### **4.4 Directory Binding**

```
singularity exec --bind <host_path>:<container_path> myimage.sif <command>
```

This workflow ensures the proper installation and usage of Singularity for containerized execution of Docker images in HPC environments.
