import time

from cohesivenet import CohesiveSDKException, VNS3Client


def wait_for_images_ready(client, import_uuids=None, interval=1.0, timeout=120.0):
    """Wait for images to be Ready. Defaults to waiting for all.

    Arguments:
        client {VNS3Client}

    Keyword Arguments:
        import_uuids {List[str]} - list of import uuids to filter on
        timeout {float}

    Raises:
        CohesiveSDKException

    Returns:
        Bool
    """
    if not import_uuids:
        return True

    start_time = time.time()
    resp_data = client.network_edge_plugins.get_container_system_images()
    images = resp_data.response.images
    if not images:
        if import_uuids is not None:
            raise CohesiveSDKException("No container images found.")
        return True

    if all([i.get("status") == "Ready" for i in images]):
        return True

    time.sleep(interval)
    while time.time() - start_time < timeout:
        resp_data = client.network_edge_plugins.get_container_system_images()
        images = resp_data.response.images
        if all(
            [
                i.get("status") == "Ready"
                for i in images
                if i.get("import_id") in import_uuids
            ]
        ):
            return True
        time.sleep(interval)

    raise CohesiveSDKException(
        "Timeout: Images failed to enter ready state [timeout=%s seconds, host=%s]"
        % (timeout, client.host_uri)
    )


def get_image_id_from_import(client, import_id):
    """Fetch Image ID given import uuid

    Arguments:
        client {VNS3Client}
        import_id {str}

    Returns:
        str - image ID
    """
    resp_data = client.network_edge_plugins.get_container_system_images(uuid=import_id)
    images = resp_data.response.images
    if not images:
        raise CohesiveSDKException("Couldnt find image for import id %s" % import_id)

    image = images[0]
    return image.get("id")


def search_images(client, image_name):
    """Search plugin images by name

    Arguments:
        client {VNS3Client}
        image_name {str}

    Raises:
        CohesiveSDKException

    Returns:
        ContainerImage
    """
    resp_data = client.network_edge_plugins.get_container_system_images()
    images = resp_data.response.images
    if images is None:
        raise CohesiveSDKException("Container system is not running")
    non_null_images = list(filter(None, images))
    if len(non_null_images) == 0:
        return None

    for image in non_null_images:
        if image.get("image_name").lower() == image_name.lower():
            return image
    return None


def search_containers(client: VNS3Client, image_id=None):
    """Search running plugins for one of image_id

    Arguments:
        client {VNS3Client}
        image_id {str}
    """
    if not any([image_id]):
        return []

    containers_resp = (
        client.network_edge_plugins.get_container_system_running_containers()
    )
    containers = containers_resp.response.containers
    if containers is None:
        raise CohesiveSDKException("Container system is not running")
    if len(containers) == 0:
        return []

    matches = []
    for container in containers:
        if image_id is not None:
            if image_id == container.get("image"):
                matches.append(container)
    return matches
