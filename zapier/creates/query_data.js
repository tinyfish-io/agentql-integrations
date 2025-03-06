const { AGENTQL_HOST_URL, QUERY_DOCS_URL } = require("../constants/host");
const { QUERY_ENDPOINT } = require("../constants/endpoint");
const { ERROR_MESSAGE } = require("../constants/message");

const { generateContainerNodeSample } = require("../utils/util");

const perform = async (z, bundle) => {
  if (bundle.meta.isLoadingSample) {
    const { QueryParser } = require("agentql-js-common");
    try {
      const node = new QueryParser(bundle.inputData.query).parse();
      return {
        data: generateContainerNodeSample(node),
        request_id: "sample-request-id",
        screenshot: "a base64 encoded image",
      };
    } catch (error) {
      throw new z.errors.Error(
        // This message is surfaced to the user
        `Invalid AgentQL query! \n${error.message}. \nPlease see ${QUERY_DOCS_URL} for more information.`,
        "InvalidAgentQLQueryError",
        error.status
      );
    }
  }
  // Create a webhook subscription first
  const webhookUrl = await z.generateCallbackUrl();

  // Make the request to your endpoint with the webhook URL
  const webhookACKResponse = await z.request({
    method: "POST",
    url: `${AGENTQL_HOST_URL}/${QUERY_ENDPOINT}`, // your local endpoint
    headers: {
      "X-API-Key": bundle.authData.apiKey,
      "Content-Type": "application/json",
      "X-TF-Request-Origin": "zapier",
    },
    body: {
      url: bundle.inputData.url,
      query: bundle.inputData.query,
      params: {
        is_screenshot_enabled: bundle.inputData.is_screenshot_enabled,
        mode: bundle.inputData.mode,
      },
      metadata: {
        experimental_stealth_mode_enabled:
          bundle.inputData.experimental_stealth_mode_enabled,
      },
      webhook_url: webhookUrl, // Include the webhook URL in the request
    },
  });

  // Return an initial response - this will be available in bundle.outputData
  // when the callback happens
  const { request, headers, ...response } = webhookACKResponse;
  return response;
};

const performResume = async (z, bundle) => {
  if (bundle.cleanedRequest.error_info) {
    throw new z.errors.Error(
      // This message is surfaced to the user
      ERROR_MESSAGE(
        bundle.cleanedRequest.error_info,
        bundle.cleanedRequest.metadata.request_id
      ),
      "ServiceError",
      bundle.cleanedRequest.status
    );
  }

  // Return the data that was sent to the callback URL
  return {
    data: bundle.cleanedRequest.data,
    request_id: bundle.cleanedRequest.metadata.request_id,
    screenshot: bundle.cleanedRequest.metadata.screenshot,
  };
};

module.exports = {
  key: "query_data",
  noun: "Query",

  display: {
    label: "Extract Data From Web Page",
    description: `Extracts data from a webpage using a query`,
  },

  operation: {
    perform,
    performResume,
    inputFields: [
      {
        key: "url",
        label: "Website URL",
        type: "string",
        required: true,
        helpText: "The URL of the website you want to query data from",
      },
      {
        key: "query",
        label: "AgentQL Query",
        type: "text",
        required: true,
        helpText: `The AgentQL query used to extract data. [Visit our docs for more information.](${QUERY_DOCS_URL})`,
      },
      {
        key: "mode",
        type: "string",
        label: "Extraction Mode",
        required: false,
        choices: {
          fast: "Fast - Recommended for typical use cases",
          standard: "Standard - Better for complex or high-volume data",
        },
        default: "fast",
        helpText:
          "Specifies the extraction mode: standard for complex or high-volume data, or fast for typical use cases.",
      },
      {
        key: "is_screenshot_enabled",
        type: "boolean",
        label: "Capture Screenshot",
        required: false,
        default: "false",
        helpText: "Enable/disable screenshot capture",
      },
      {
        key: "experimental_stealth_mode_enabled",
        type: "boolean",
        label: "Experimental Stealth Mode",
        required: false,
        default: "false",
        helpText:
          "Enable/disable experimental stealth mode. This mode may improve extraction success rates for some websites.",
      },
    ],
    sample: {
      data: {},
      request_id: "sample-request-id",
      screenshot: "a base64 encoded image",
    },
  },
};
