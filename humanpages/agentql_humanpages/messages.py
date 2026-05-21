UNSET_AGENTQL_API_KEY_ERROR = (
    "No AgentQL API key provided. Set the `agentql_api_key` argument or the "
    "`AGENTQL_API_KEY` environment variable. "
    "Create an API key at https://dev.agentql.com."
)

UNSET_HUMANPAGES_API_KEY_ERROR = (
    "No Human Pages API key provided. Set the `humanpages_api_key` argument or the "
    "`HUMANPAGES_API_KEY` environment variable. "
    "Get an API key at https://humanpages.ai."
)

NO_HUMANS_AVAILABLE_ERROR = (
    "No humans are currently available for this task on Human Pages. "
    "Try again later or adjust the task description."
)

JOB_CREATION_FAILED_ERROR = "Failed to create a job on Human Pages: {detail}"

JOB_TIMEOUT_ERROR = (
    "The Human Pages job did not complete within the allowed time. "
    "Job ID: {job_id}"
)

AGENTQL_EXTRACTION_FAILED = (
    "AgentQL extraction failed for URL {url}: {detail}. "
    "Falling back to Human Pages."
)

HUMANPAGES_UNAUTHORIZED_ERROR = (
    "Invalid Human Pages API key. "
    "Please provide a valid key from https://humanpages.ai."
)
