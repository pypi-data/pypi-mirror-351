# Standard Library Imports
import asyncio

# First-Party Imports
from pipecat.frames.frames import WaitForDTMFFrame
from pipecat.processors.frame_processor import FrameDirection, FrameProcessor

# Define switch_language tool
wait_for_dtmf_tool = {
    "name": "wait_for_dtmf",
    "description": "Wait for the user to press a DTMF digit on the keypad.",
    "parameters": {
        "properties": {},
        "required": [],
    },
}


async def wait_for_dtmf_handler(
    function_name: str,
    tool_call_id: str,
    args: dict,
    llm: FrameProcessor,
    context,
    result_callback: callable,
    timeout: float,
    bot_logger,
):
    bot_logger.info("Waiting for DTMF input...")

    try:
        await llm.push_frame(WaitForDTMFFrame(), FrameDirection.UPSTREAM)
        await result_callback(None)
    except Exception as e:
        bot_logger.error(f"Error waiting for DTMF: {e}")
        await result_callback(
            {
                "status": "error",
                "message": "Looks like there's some error in noting the number entered on keypad",
            }
        )
        return
