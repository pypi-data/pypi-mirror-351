from cohesivenet import util, Logger, VNS3Client, CohesiveSDKException


def create_firewall_policy(client: VNS3Client, firewall_rules, state={}):
    """Create group of firewall rules

    Arguments:
        client {VNS3Client}
        firewall_rules {List[CreateFirewallRuleRequest]} - [{
            'position': int,
            'rule': str
        }, ...]

    Keyword Arguments:
        state {dict} - State to format rules with. (can call client.state)

    Returns:
        Tuple[List[str], List[str]] - success, errors
    """
    successes = []
    errors = []
    Logger.debug(
        "Creating firewall policy.",
        host=client.host_uri,
        rule_count=len(firewall_rules),
    )
    for i, rule_args in enumerate(firewall_rules):
        rule, err = util.format_string(rule_args["rule"], state)
        if err:
            errors.append(err)
            continue

        rule_args.update(rule=rule)
        client.firewall.post_create_firewall_rule(**rule_args)
        successes.append(
            'Rule "%s" inserted at position %d' % (rule, rule_args["position"])
        )
    return successes, errors


def __construct_proposed_firewall_list(rule_args_list, state=None):
    _state = state or {}
    errors = []
    new_firewall = []
    for rule_args in rule_args_list:
        rule, err = util.format_string(rule_args["rule"], _state)
        if err:
            errors.append(err)
            continue

        position = rule_args.get("position", -1)
        if position == -1:
            new_firewall.append(rule)
        elif type(position) is int:
            new_firewall.insert(position, rule)
        else:
            errors.append("Rule position %s invalid. [RULE='%s']" % (position, rule))

    return new_firewall, errors


def __firewall_resp_to_list(firewall_raw_response):
    return [
        rule_tuple[0].strip()
        for rule_tuple in sorted(
            firewall_raw_response.response, key=lambda r: int(r[1])
        )
    ]


def assert_rule_policy(client: VNS3Client, rules, should_fix=False):
    """Assert rule policy contains expected rules

    Arguments:
        client {VNS3Client}
        rules {List[dict]}

    Keyword Arguments:
        should_fix {bool} - if false, raise Error, else, update firewall

    Raises:
        CohesiveSDKException - raised if invalid firewall rules provided
        AssertionError - raised if should_fix=False and provided rules dont match VNS3

    Returns:
        List[str] - ordered list of firewall rules
    """
    current_firewall = __firewall_resp_to_list(client.firewall.get_firewall_rules())
    new_firewall, errors = __construct_proposed_firewall_list(rules, state=client.state)
    if errors:
        raise CohesiveSDKException(
            "Invalid firewall rules provided. Errors=%s" % (errors)
        )

    if current_firewall == new_firewall:
        Logger.info("Current firewall is correct. No-op.", host=client.host_uri)
        return current_firewall

    Logger.info(
        "Firewall configuration drift. Expected: %s != %s."
        % (new_firewall, current_firewall),
        host=client.host_uri,
    )

    if not should_fix:
        raise AssertionError(
            "Firewalls did not match for VNS3 @ %s. Current firewall %s != %s."
            % (client.host_uri, current_firewall, new_firewall)
        )

    # operations: insert, delete
    OP_INS = "insert"
    OP_DEL = "delete"
    firewall_edits = []
    for i, rule in enumerate(new_firewall):
        if len(current_firewall) <= i:
            operation = OP_INS
        elif current_firewall[i] == rule:
            continue
        else:
            # current firewall rule is incorrect.
            # now, minimize operations to get correct
            # if can insert OR delete, prefer delete
            # ie. if next rule is the correct rule, del this rule
            operation = (
                OP_DEL
                if len(current_firewall) > i + 1 and current_firewall[i + 1] == rule
                else OP_INS
            )

        firewall_edits.append("%s:%s" % (operation, i))
        if operation == OP_INS:
            client.firewall.post_create_firewall_rule(**{"rule": rule, "position": i})
            current_firewall.insert(i, rule)
        else:  # operation == OP_DEL:
            client.firewall.delete_firewall_rule_by_position(i)
            del current_firewall[i]

    Logger.debug(
        "%s network operations required to fix firewall: %s"
        % (len(firewall_edits), firewall_edits),
        host=client.host_uri,
    )

    return __firewall_resp_to_list(client.firewall.get_firewall_rules())
