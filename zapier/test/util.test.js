/* globals describe, it, expect, jest */

const { generateContainerNodeSample } = require("../utils/util"); // adjust path as needed

const { QueryParser } = require("agentql-js-common");

describe("generateContainerNodeSample", () => {
  beforeEach(() => {
    // Reset any module state between tests
    jest.clearAllMocks();
  });

  it("should handle a simple IdNode", () => {
    const QUERY = `
    {
      search_btn
      search_text
    }
    `;
    const node = new QueryParser(QUERY).parse();
    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("search_btn");
    expect(typeof result.search_btn).toBe("string");
    expect(result.search_btn).toMatch(/^search_btn_\d+$/);
    expect(result).toHaveProperty("search_text");
    expect(typeof result.search_text).toBe("string");
    expect(result.search_text).toMatch(/^search_text_\d+$/);
  });

  it("should handle context for a simple IdNode", () => {
    const QUERY = `
    {
      search_btn (context)
    }
    `;
    const node = new QueryParser(QUERY).parse();
    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("search_btn");
    expect(typeof result.search_btn).toBe("string");
    expect(result.search_btn).toMatch(/^search_btn_\d+$/);
  });

  it("should handle an IdListNode with multiple items", () => {
    const QUERY = `
    {
      id_list[]
    }
    `;
    const node = new QueryParser(QUERY).parse();
    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("id_list");
    expect(Array.isArray(result.id_list)).toBe(true);
    expect(result.id_list).toHaveLength(3);
    result.id_list.forEach((item) => {
      expect(typeof item).toBe("string");
      expect(item).toMatch(/^id_list_\d+$/);
    });
  });

  it("should handle an IdListNode with multiple items", () => {
    const QUERY = `
    {
      id_list(context)[]
    }
    `;
    const node = new QueryParser(QUERY).parse();
    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("id_list");
    expect(Array.isArray(result.id_list)).toBe(true);
    expect(result.id_list).toHaveLength(3);
    result.id_list.forEach((item) => {
      expect(typeof item).toBe("string");
      expect(item).toMatch(/^id_list_\d+$/);
    });
  });

  it("should handle a ContainerListNode with nested structure", () => {
    const QUERY = `
    {
      container_list[] {
        child_id_1
        child_id_2
      }
    }
    `;
    const node = new QueryParser(QUERY).parse();

    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("container_list");
    expect(Array.isArray(result.container_list)).toBe(true);
    expect(result.container_list).toHaveLength(3);
    result.container_list.forEach((container) => {
      expect(container).toHaveProperty("child_id_1");
      expect(typeof container.child_id_1).toBe("string");
      expect(container.child_id_1).toMatch(/^child_id_1_\d+$/);

      expect(container).toHaveProperty("child_id_2");
      expect(typeof container.child_id_2).toBe("string");
      expect(container.child_id_2).toMatch(/^child_id_2_\d+$/);
    });
  });

  it("should handle nested ContainerNodes", () => {
    const QUERY = `
    {
      nested {
        nested_id
      }
    }
    `;
    const node = new QueryParser(QUERY).parse();

    const result = generateContainerNodeSample(node);
    expect(result).toHaveProperty("nested");
    expect(result.nested).toHaveProperty("nested_id");
    expect(typeof result.nested.nested_id).toBe("string");
    expect(result.nested.nested_id).toMatch(/^nested_id_\d+$/);
  });

  it("should handle complex nested structures", () => {
    const QUERY = `
    {
      items[] {
        id
        name
      }
      nested {
        tags[]
      }
    }
    `;
    const node = new QueryParser(QUERY).parse();

    const result = generateContainerNodeSample(node);
    // Verify container list structure
    expect(result).toHaveProperty("items");
    expect(Array.isArray(result.items)).toBe(true);
    expect(result.items).toHaveLength(3);
    result.items.forEach((item) => {
      expect(item).toHaveProperty("id");
      expect(item).toHaveProperty("name");
      expect(typeof item.id).toBe("string");
      expect(typeof item.name).toBe("string");
    });

    // Verify nested container structure
    expect(result).toHaveProperty("nested");
    expect(result.nested).toHaveProperty("tags");
    expect(Array.isArray(result.nested.tags)).toBe(true);
    expect(result.nested.tags).toHaveLength(3);
    result.nested.tags.forEach((tag) => {
      expect(typeof tag).toBe("string");
      expect(tag).toMatch(/^tags_\d+$/);
    });
  });

  it("complex nested structures", () => {
    const QUERY = `
    {
        drink_category[] {
                category_name
                drink[] {
                    drink_name
                    price
                }
            }
        }
    `;
    const node = new QueryParser(QUERY).parse();
    const result = generateContainerNodeSample(node);

    expect(result).toHaveProperty("drink_category");
    expect(Array.isArray(result.drink_category)).toBe(true);
    expect(result.drink_category).toHaveLength(3);
    result.drink_category.forEach((category) => {
      expect(category).toHaveProperty("category_name");
      expect(typeof category.category_name).toBe("string");
      expect(category.category_name).toMatch(/^category_name_\d+$/);
      expect(category).toHaveProperty("drink");
      expect(Array.isArray(category.drink)).toBe(true);
      expect(category.drink).toHaveLength(3);
      category.drink.forEach((drink) => {
        expect(drink).toHaveProperty("drink_name");
        expect(typeof drink.drink_name).toBe("string");
        expect(drink.drink_name).toMatch(/^drink_name_\d+$/);
        expect(drink).toHaveProperty("price");
        expect(typeof drink.price).toBe("string");
        expect(drink.price).toMatch(/^price_\d+$/);
      });
    });
  });
});
