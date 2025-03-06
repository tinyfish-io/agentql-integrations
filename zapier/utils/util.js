let COUNTER = 0;

// Generate sample data based on the input query from user
const generateContainerNodeSample = (node) => {
  const {
    ContainerListNode,
    IdListNode,
    IdNode,
    ContainerNode,
  } = require("agentql-js-common");
  const result = {};
  for (const child of node.children) {
    // Check most specific types (child classes) first
    if (child instanceof IdListNode) {
      // For list of IDs (like job_categories[])
      const idList = [];
      for (let i = 0; i < 3; i++) {
        idList.push(generateIdNodeSample(child));
      }
      result[child.name] = idList;
    } else if (child instanceof ContainerListNode) {
      // For list of containers (like jobs[])
      const containerList = [];
      for (let i = 0; i < 3; i++) {
        containerList.push(generateContainerNodeSample(child));
      }
      result[child.name] = containerList;
    } else if (child instanceof IdNode) {
      result[child.name] = generateIdNodeSample(child);
    } else if (child instanceof ContainerNode) {
      // For nested containers (like header{})
      result[child.name] = generateContainerNodeSample(child);
    }
  }
  return result;
};

const generateIdNodeSample = (child) => {
  return child.name + "_" + COUNTER++;
};

module.exports = {
  generateContainerNodeSample,
};
