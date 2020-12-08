import chai, { expect } from "chai";
import { extractTags, groupByTag } from "../../models/challenge"


const Tag = (name, slug, order) => {
  return { name: name, slug: slug, order: order }
}


describe("Tag functions", () => {

  it("Empty tag list from empty challenge list", () => {
    let extracted = extractTags([])
    expect(extracted).to.deep.equal([]);
  });

  it("Extracts one tag from challenge list", () => {
    let tags = [Tag('Ultimate Tag', 'ultimate-tag', 1)]
    let extracted = extractTags([
      { title: 'Challenge #1', slug: 'challenge1', tags: tags },
      { title: 'Challenge #2', slug: 'challenge2', tags: tags },
    ])
    expect(extracted).to.deep.equal(tags);
  });

  it("Extracts multiple tags from challenge list and sort by order", () => {
    let tags = [
      Tag('First Tag', 'first-tag', 1),
      Tag('Second Tag', 'second-tag', 2),
      Tag('Third Tag', 'third-tag', 3),
      Tag('Fourth Tag', 'fourth-tag', 4),
    ]
    let extracted = extractTags([
      { title: 'Challenge #1', slug: 'challenge1', tags: [Tag('Fourth Tag', 'fourth-tag', 4), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #2', slug: 'challenge2', tags: [Tag('Second Tag', 'second-tag', 2), Tag('First Tag', 'first-tag', 1)] },
      { title: 'Challenge #3', slug: 'challenge3', tags: [Tag('First Tag', 'first-tag', 1), Tag('Fourth Tag', 'fourth-tag', 4)] },
      { title: 'Challenge #4', slug: 'challenge4', tags: [Tag('Second Tag', 'second-tag', 2), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #5', slug: 'challenge5', tags: [Tag('Second Tag', 'second-tag', 2), Tag('First Tag', 'first-tag', 1), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #6', slug: 'challenge6', tags: [Tag('Third Tag', 'third-tag', 3), Tag('Second Tag', 'second-tag', 2), Tag('Fourth Tag', 'fourth-tag', 4), Tag('First Tag', 'first-tag', 1)] },
    ])
    expect(extracted).to.deep.equal(tags);
  });

  it("Empty challenge group from empty challenge list", () => {
    let challenge = { title: 'Challenge #1', slug: 'challenge1', tags: [] }
    let groups = groupByTag([challenge])
    expect(groups).to.deep.equal({ '': [challenge] });
  });

  it("Groups challenges by tag with highest order", () => {
    let challenges = [
      { title: 'Challenge #1', slug: 'challenge1', tags: [Tag('Fourth Tag', 'fourth-tag', 4), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #2', slug: 'challenge2', tags: [Tag('Second Tag', 'second-tag', 2), Tag('First Tag', 'first-tag', 1)] },
      { title: 'Challenge #3', slug: 'challenge3', tags: [Tag('First Tag', 'first-tag', 1), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #4', slug: 'challenge4', tags: [Tag('Second Tag', 'second-tag', 2), Tag('Third Tag', 'third-tag', 3)] },
      { title: 'Challenge #5', slug: 'challenge5', tags: [Tag('First Tag', 'first-tag', 1)] },
      { title: 'Challenge #6', slug: 'challenge6', tags: [Tag('Third Tag', 'third-tag', 3), Tag('Second Tag', 'second-tag', 2), Tag('Fourth Tag', 'fourth-tag', 4), Tag('First Tag', 'first-tag', 1)] },
    ]
    let groups = groupByTag(challenges)
    let expected = {
      'first-tag': [challenges[4]],
      'second-tag': [challenges[1]],
      'third-tag': [challenges[2], challenges[3]],
      'fourth-tag': [challenges[0], challenges[5]],
    }
    expect(groups).to.deep.equal(expected);
  });

});
