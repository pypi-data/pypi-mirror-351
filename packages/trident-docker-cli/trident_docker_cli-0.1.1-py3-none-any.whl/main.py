import os
import sys
import yaml
import docker
from typing import Dict
from docker.tls import TLSConfig
from docker.errors import BuildError, APIError, NotFound

def getClient(config: Dict):
    if config.tls !=  'true':
        return docker.DockerClient(base_url=config.tls)
    
    print("Using TLS files ./ca.pem,./client-cert.pem,./client-key.pem is required")
    tls_config = TLSConfig(
        client_cert=('./client-cert.pem', './client-key.pem'),
        ca_cert='./ca.pem',
        verify=True
    )

    return docker.DockerClient(base_url=config.url, tls=tls_config)

def build(config: Dict, client: docker.DockerClient):
    if config.image is None:
        raise RuntimeError("config.image is required")

    try:
        image, logs = client.images.build(
            path='.',
            tag=config.image,
            rm=True,  # 成功后删除中间容器
            nocache=False  # 是否不使用缓存
        )
        print(f"Image {image.id} built successfully.")
    except BuildError as err:
        print(f"Build error: {err}")
    except APIError as err:
        print(f"API error: {err}")

    # 输出构建日志
    for log in logs:
        print(log)

def stop(config: Dict, client: docker.DockerClient):
    if config.container is None:
        raise RuntimeError("config.container is required")

    try:
        container = client.containers.get(config.container)
        container.remove(force=True)
        print(f"Container found: {container.id}")
    except NotFound as e:
        # 如果容器未找到，则进入此块
        print(f"Container not found: {e.explanation}")

def start(config: Dict, client: docker.DockerClient):
    if config.image is None:
        raise RuntimeError("config.image is required")
    if config.container is None:
        raise RuntimeError("config.container is required")

    # 定义容器配置
    config = {
        'image': config.image,  # 替换为你想要使用的镜像名
        'detach': True,     # 在后台运行容器
        'name': config.container,
    }
    # 创建并运行容器
    container = client.containers.run(**config)

    # 输出容器ID（可选）
    print(f"Container {container.id} startup:")

def main():
    if not os.path.exists('./config.yaml'):
        raise RuntimeError("./config.yaml is not found")

    with open('./config.yaml', 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        
    config = config_data.get('database', {})

    if config.url is None:
        raise RuntimeError("env:DOCKER_HOST is required")

    # 连接到远程Docker守护进程
    try:
        client = getClient(config)
        match sys.argv[1]:
            case "build":
                build(client)
            case "stop":
                stop(client)
            case "start":
                start(client)
            case "all":
                stop(client)
                build(client)
                start(client)
            case _:
                print("Usage: python main.py [build|stop|start]")
    finally:
        # 关闭连接
        client.close()


if __name__ == "__main__":
    main()
