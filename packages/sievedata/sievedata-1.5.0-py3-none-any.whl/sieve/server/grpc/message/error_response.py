import traceback
from ...proto import worker_pb2


class InternalInputException(Exception):
    pass


class WorkerNotSetupException(Exception):
    pass


def get_error_response(e: Exception, bill_handler, internal_bill_handler):
    """Check if e is system exit in case we want to exit the process and raise an exception"""

    print("Prediction failed", str(e))
    override_cost_dollars = bill_handler.reset()
    internal_cost_dollars = internal_bill_handler.reset()
    o = traceback.format_exc()
    return worker_pb2.PredictionResponse(
        status=worker_pb2.Status.STATUS_FAILED,
        error=str(o),
        data=b"",
        stop=True,
        metadata=worker_pb2.PredictionMetadata(
            override_cost_dollars=override_cost_dollars,
            internal_cost_dollars=internal_cost_dollars,
        ),
    )


def get_fatal_response(e: Exception, bill_handler, internal_bill_handler):
    """Check if e is system exit in case we want to exit the process and raise an exception"""

    print("Prediction failed", str(e))
    override_cost_dollars = bill_handler.reset()
    internal_cost_dollars = internal_bill_handler.reset()
    o = traceback.format_exc()
    return worker_pb2.PredictionResponse(
        status=worker_pb2.Status.STATUS_FAILED,
        error=str(o),
        data=b"",
        stop=True,
        fatal=True,
        metadata=worker_pb2.PredictionMetadata(
            override_cost_dollars=override_cost_dollars,
            internal_cost_dollars=internal_cost_dollars,
        ),
    )
