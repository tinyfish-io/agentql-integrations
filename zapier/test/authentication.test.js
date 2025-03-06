/* globals describe, it, expect */

const zapier = require("zapier-platform-core");
const App = require("../index");

const appTester = zapier.createAppTester(App);

describe("custom auth", () => {
  it("fails on bad auth", async () => {
    const bundle = {
      authData: {
        apiKey: "bad",
      },
    };

    try {
      await appTester(App.authentication.test, bundle);
    } catch (error) {
      expect(error.message).toContain("The API Key you supplied is incorrect");
      return;
    }
    throw new Error("appTester should have thrown");
  });
});
