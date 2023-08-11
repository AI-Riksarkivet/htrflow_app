FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
#RUN apt-get update && apt-get install -y git ninja-build libglib2.0-0 libsm6 libxrender-dev libxext6 libgl1-mesa-glx \

# mim openmmlabs installs (quick fix..)
RUN mim install mmengine 
RUN mim install mmcv 
RUN mim install mmdet 
RUN mim install mmocr

# Set up a new user named "user" with user ID 1000
RUN useradd -m -u 1000 user
# Switch to the "user" user
USER user

# for localrun
ENV AM_I_IN_A_DOCKER_CONTAINER Yes

# Set home to the user's home directory
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH

# Set the working directory to the user's home directory
WORKDIR $HOME/app

# Copy the current directory contents into the container at $HOME/app setting the owner to the user
COPY --chown=user . $HOME/app

CMD ["python", "app/app.py"]