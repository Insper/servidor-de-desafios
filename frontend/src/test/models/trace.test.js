import chai, { expect } from "chai";
import { findLinesWithCode } from "../../models/trace"


describe("Code trace functions", () => {

  it("Ignore lines with comments, empty, or containing only whitespaces", () => {
    const code = `
# Some comment
def add(a, b):  # This should not be ignored
    # This should be ignored
    c = a + b
    return c

print(add(10, 20))

`
    let extracted = findLinesWithCode(code)
    expect(extracted).to.deep.equal([3, 5, 6, 8]);
  });

});
