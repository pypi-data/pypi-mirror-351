from agents import RunContextWrapper, Agent, function_tool
from agents.mcp import MCPServer

from ci_agents.factory import AgentFactory
from ci_agents.log_config import logger
from ci_agents.types import AnalysisContext, InfraIssueAIResponse
from hooks.agent_hook_log import global_log_hook


def infra_agent_instructions(context: RunContextWrapper[AnalysisContext], agent: Agent[AnalysisContext]) -> str:
    failure_log = context.context.failure_log
    failed_thread_log = context.context.failed_thread_log
    device_log = context.context.device_log
    appium_log = context.context.appium_log
    test_id = context.context.test_id
    system_prompt = f"""
    #Role:
    You are a mobile E2E automation expert specializing in analyzing CI automation failure reports. Your expertise lies in diagnosing whether a failure is caused by the infrastructure issues (e.g.device issue, driver issue, network issues).

    #Tasks:
    Your goal is to determine whether a CI test report failure is caused by infrastructure issue by analyzing logs
    • A failure is considered infrastructure-related if there are error logs indicating:
      - device_issue (unavailable, disconnected, etc.)
      - driver_issue (initialization failures, session problems, installation failures, etc.)
      - network_issue (connectivity problems with devices, etc.)

    #Data Provided:
    You will receive the following logs to aid in analysis:
    • test_id: {test_id}
    • failure_log - Key error stack trace from the automation framework:
      {failure_log}
    • failed_thread_log - Detailed log of the failure event:
    • {failed_thread_log}
    • device_log - Record all devices information(such as device_host, device_udid, device_record) during the test:
      {device_log}
    • appium_log (Optional) -appium error logs
      {appium_log}

    #Analysis Steps

    1.Analyze device_log:Check if it contains multiple device_udid
    2.Detect failed_thread_log: if NoSuchElementException/AssertionError in failed_thread_log,this issue is not driver issue
    3:If device/driver issues detected
        3.1.ONLY call report_appium_error_log_fetch with test_id to get appium error log, this can be called only once
        3.2.Analysis appium error log
    4:Analyze all logs:
        If multiple devices, need determine which device has the problem 
    5. If you suspect it's not an infrastructure issue:
        5.1.You MUST call fetch_failed_step_images()
        5.2.If failed step images urls is NOT empty, ONLY call extract_image_file_from_url with image urls               
    6.Analyze the extracted images and describe what you see in output
        if system alert that is related to the device being detected, this is infrastructure issue
    7 Only use two MCP tools if needed:
      - report_appium_error_log_fetch (for getting appium logs)
      - extract_image_file_from_url (for extracting images)       
    8.Confirm your analysis and provide a detailed explanation of the failure.

    """
    requirement = """
    #Output Requirements:
    ##Case 1: If failure_type is infrastructure issue , return with json format:
    {
       "root_cause_insight": "Clearly explain the exact root cause of the failure.",
       "action_insight": {
          "device_udid": "The UDID of the device that failed",
          "device_host": "The host where the device is connected",
          "detail_log": "Relevant log excerpts supporting the analysis",
          "error_type": "The type of infrastructure error,must be one of: device_issue, driver_issue, app_issue, or network_issue",
        },
       "failed_by_infra": true
    }
    Notes:
    • "rootCauseInsight" should clearly explain the reason for the failure based on log analysis.
    • "actionInsight" must include actual extracted information from logs.

    ##Case 2: If failure_type is not infrastructure issue, return with json format:
    {
       "root_cause_insight": "Explain why the failure is not due to an infrastructure issue.",
       "failed_by_infra": false
    }
    """
    return system_prompt + requirement


class InfraAgentFactory(AgentFactory):

    def __init__(self, mcp: MCPServer = None):
        super().__init__()
        self.mcp = mcp

    def get_agent(self) -> Agent[AnalysisContext]:
        # dynamic_fetch_appium_log = self.create_dynamic_fetch_appium_log()
        fetch_failed_step_images = self.create_fetch_failed_step_images()

        # Filter out None MCP servers        ??????
        # mcp_servers = [server for server in [self.mcp] if server is not None]

        infra_agent = Agent[AnalysisContext](
            name="infra_agent",
            model="gpt-4o",
            instructions=infra_agent_instructions,
            mcp_servers=[self.mcp],
            output_type=InfraIssueAIResponse,
            hooks=global_log_hook,
            tools=[fetch_failed_step_images]
        )
        return infra_agent

    # def create_dynamic_fetch_appium_log(self):
    #     @function_tool
    #     def dynamic_fetch_appium_log(context: RunContextWrapper[AnalysisContext]) -> str:
    #         """
    #         Fetches Appium logs related to the test ID.
    #         """
    #         logger.info("dynamic_fetch_appium_log function called! Fetching appium logs...")
    #         beats_metadata = context.context.beats_metadata
    #         current_test_id = context.context.test_id
    #         if not current_test_id:
    #             return "Unable to get test ID."
    #         try:
    #             appium_log = beats_metadata.get_appium_error_log_data(current_test_id)
    #             return appium_log
    #         except Exception as e:
    #             return f"Error occurred while fetching Appium logs: {str(e)}"
    #
    #     return dynamic_fetch_appium_log

    def create_fetch_failed_step_images(self):
        @function_tool
        def fetch_failed_step_images(context: RunContextWrapper[AnalysisContext]) -> str:
            """
            Fetches URLs to screenshots from the failed test step.
            """
            logger.info("fetch_failed_step_images function called! Retrieving failed step screenshots...")
            beats_metadata = context.context.beats_metadata
            current_test_id = context.context.test_id
            device_record_metadata = context.context.device_record_metadata
            if not current_test_id:
                return "Unable to get test ID."

            try:
                device_info = device_record_metadata.get_device_info(current_test_id)
                formatted_urls = ""
                failed_step = beats_metadata.case_meta_data(current_test_id)['failed_step']
                if not failed_step['current_step_image_file_urls']:
                    return "No screenshot images found for the failed step."

                image_urls = failed_step['current_step_image_file_urls']
                if image_urls:
                    device_info_list = list(device_info.items()) if device_info else []
                    url_device_pairs = []

                    for i, url in enumerate(image_urls):
                        if i < len(device_info_list):
                            udid, host = device_info_list[i]
                            url_device_pairs.append(f"Screenshot URL: {url} (Device UDID: {udid}, Host: {host})")
                        else:
                            url_device_pairs.append(f"Screenshot URL: {url} (No device info available)")

                    formatted_urls = "\n".join(url_device_pairs)
                return formatted_urls

            except Exception as e:
                return f"Error occurred while fetching failed step images: {str(e)}"

        return fetch_failed_step_images
