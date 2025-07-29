import time

from typing import Callable

import cohesivenet.data_types as data_types
from cohesivenet import ApiException, UrlLib3ConnExceptions
from cohesivenet.async_util import run_parallel, force_async


def retry_call(call_api, args=(), kwargs={}, attempt=0, max_attempts=10, sleep=2):
    """Simply retry wrapper. No backoff, constant retry

    Arguments:
        call_api {callable}

    Keyword Arguments:
        args {tuple}
        kwargs {dict}
        attempt {int} - increment on attempts
        max_attempts {int} - (default: {10})
        sleep {int} - wait between attempts (default: {2})

    Raises:
        e: UrlLib3ConnExceptions

    Returns:
        Any
    """
    try:
        return call_api(*args, **kwargs)
    except UrlLib3ConnExceptions as e:
        attempt = attempt + 1
        if attempt >= max_attempts:
            raise e
        time.sleep(sleep)
        return retry_call(
            call_api,
            args,
            kwargs,
            attempt=attempt,
            max_attempts=max_attempts,
            sleep=sleep,
        )


def gather_results(results):
    """Group results if by success and exception

    Arguments:
        results {List[ExceptionResult or Any]}

    Returns:
        Tuple[List[Any], List[ExceptionResult]]
    """
    succeeded = []
    failed = []
    for result in results:
        if isinstance(result, data_types.ExceptionResult):
            failed.append(result)
        else:
            succeeded.append(result)

    return succeeded, failed


def try_call_client(client, call, *args, should_raise=False, **kwargs):
    """Try call method call(client, *args, **kwargs) catch exception

    Arguments:
        client {VNS3Client}
        call {Callable} - function that accepts client as first arg

    Returns:
        [OperationResult or ExceptionResult]
    """
    try:
        response = call(client, *args, **kwargs)
        return data_types.OperationResult(response, client=client)
    except ApiException as e:
        if should_raise:
            raise e
        return data_types.ExceptionResult(e, client=client)


async def try_call_client_async(client, call, *args, **kwargs):
    """Async call client wrapper

    Arguments:
        client {VNS3Client}
        call {Callable} - function that accepts client as first arg

    Returns:
        [OperationResult or ExceptionResult]
    """
    return await force_async(try_call_client)(client, call, *args, **kwargs)


def try_call_api(api_call, *args, should_raise=False, **kwargs):
    """try_api_call Wrapper for api call to catch errors

    Arguments:
        api_call {callable}

    Returns:
        [OperationResult or ExceptionResult]
    """
    try:
        response = api_call(*args, **kwargs)
        return data_types.OperationResult(response, client=None)
    except ApiException as e:
        if should_raise:
            raise e
        return data_types.ExceptionResult(e, client=None)


async def try_call_api_async(api_call, *args, **kwargs):
    """try_api_call_async Async Wrapper for api call to catch errors

    Arguments:
        api_call {callable}

    Returns:
        [Coroutine -> [OperationResult or ExceptionResult]]
    """
    return await force_async(try_call_api)(api_call, *args, **kwargs)


def __bulk_call_client_sync(
    clients, call_client_func
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult -- [description]
    """
    return gather_results(
        [try_call_client(client, call_client_func) for client in clients]
    )


def __bulk_call_client_parallel(
    clients, call_client_func
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult
    """
    return gather_results(
        run_parallel(
            *(try_call_client_async(client, call_client_func) for client in clients)
        )
    )


def __bulk_call_client(
    clients, call_client_func, parallelize=False
) -> data_types.BulkOperationResult:
    """Bulk operation for clients, call same method for all clients

    Arguments:
        clients {List[VNS3Client]}
        call_client_func {callable} - func: VNS3Client -> response

    Returns:
        data_types.BulkOperationResult
    """
    if parallelize:
        return __bulk_call_client_parallel(clients, call_client_func)
    else:
        return __bulk_call_client_sync(clients, call_client_func)


def __bulk_call_api_sync(bound_api_calls) -> data_types.BulkOperationResult:
    """__bulk_call_api_sync Bulk operation for bound api methods, call synchronously

    Arguments:
        bound_api_calls {List[Callable]}

    Returns:
        data_types.BulkOperationResult -- [description]
    """
    return gather_results([try_call_api(api_call) for api_call in bound_api_calls])


def __bulk_call_api_parallel(bound_api_calls) -> data_types.BulkOperationResult:
    """__bulk_call_api_parallel Bulk operation for bound api methods, called asynchronously

    Arguments:
        bound_api_calls {List[Callable]}

    Returns:
        data_types.BulkOperationResult
    """
    return gather_results(
        run_parallel(*(try_call_api_async(api_call) for api_call in bound_api_calls))
    )


def __bulk_call_api(api_calls, parallelize=False) -> data_types.BulkOperationResult:
    """Bulk operation for bound api method interface

    Arguments:
        api_calls {callable} - bound function that accepts no args.

    Returns:
        data_types.BulkOperationResult
    """
    if parallelize:
        return __bulk_call_api_parallel(api_calls)
    else:
        return __bulk_call_api_sync(api_calls)


def bulk_operation_failed(result: data_types.BulkOperationResult):
    failures = result[1]
    return len(failures) >= 1


def bulk_operation_all_exceptions(
    result: data_types.BulkOperationResult, predicate_func: Callable
):
    """Run Predicate on BulkOperationResult

    Args:
        result (data_types.BulkOperationResult): [description]
        predicate_func (Callable): returns Boolean

    Returns: Boolean
    """
    exceptions = result[1]
    return all([predicate_func(e.exception) for e in exceptions])


def stringify_bulk_result_exception(result: data_types.BulkOperationResult):
    exceptions = result[1]
    return ", ".join(
        [
            "message=%s client=%s"
            % (str(e.exception), "None" if not e.client else e.client.host_uri)
            for e in exceptions
        ]
    )
