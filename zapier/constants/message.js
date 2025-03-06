const ERROR_MESSAGE = (error_info, request_id) => `
  An error occurred: ${error_info}. Your request id is ${request_id}, please contact support at ${SUPPORT_EMAIL} with this request id for further assistance.
`;

module.exports = {
  ERROR_MESSAGE,
};
