from cohesivenet import util, VNS3Client


def segment_overlay_clients(
    client: VNS3Client, groups=None, number_groups=None, group_ratios=None
):
    """segment_overlay_clients Segment clientpacks into sets

    Arguments:
        client {VNS3Client}

    Keyword Arguments:
        groups {List[str]} - Segment into len(groups) groups, each element being the name of group (default: {None})
        number_groups {int} - Segment into number_groups, names being 'group_x' (default: {None})
        group_ratios {Dict[str, float]} - segment by ratio of overlay size, key being the name of the group (default: {None})

    Returns:
        dict - {
            group_name<str>: clientpacks<List[str]>,
        }
    """
    assert (
        groups or number_groups or group_ratios
    ), "groups (List[str]) or number_groups (int) or group_ratios (Dict[str, flaot]) must be provided"
    clients = list(client.overlay_network.get_clientpacks().response.keys())

    if groups:
        partitions = util.partition_list_groups(clients, len(groups))
        return {group_name: partitions[i] for i, group_name in enumerate(groups)}
    elif number_groups:
        partitions = util.partition_list_groups(clients, number_groups)
        return {
            "group_%d" % (i + 1): partitions[i]
            for i, partition in enumerate(partitions)
        }
    else:
        ratios = list(group_ratios.values())
        partitions = util.partition_list_ratios(clients, ratios)
        return {group: partitions[str(ratio)] for group, ratio in group_ratios.items()}
