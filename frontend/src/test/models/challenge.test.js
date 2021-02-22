import chai, { expect } from "chai";
import { extractConcepts, groupByConcept } from "../../models/challenge"


const Concept = (name, slug, order) => {
  return { name: name, slug: slug, order: order }
}


describe("Concept functions", () => {

  it("Empty concept list from empty challenge list", () => {
    let extracted = extractConcepts([])
    expect(extracted).to.deep.equal([]);
  });

  it("Extracts one concept from challenge list", () => {
    let concept = Concept('Ultimate Concept', 'ultimate-concept', 1)
    let extracted = extractConcepts([
      { title: 'Challenge #1', slug: 'challenge1', concept: concept },
      { title: 'Challenge #2', slug: 'challenge2', concept: concept },
    ])
    expect(extracted).to.deep.equal([concept]);
  });

  it("Extracts multiple concepts from challenge list and sort by order", () => {
    let concepts = [
      Concept('First Concept', 'first-concept', 1),
      Concept('Second Concept', 'second-concept', 2),
      Concept('Third Concept', 'third-concept', 3),
      Concept('Fourth Concept', 'fourth-concept', 4),
    ]
    let extracted = extractConcepts([
      { title: 'Challenge #1', slug: 'challenge1', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
      { title: 'Challenge #2', slug: 'challenge2', concept: Concept('Second Concept', 'second-concept', 2) },
      { title: 'Challenge #3', slug: 'challenge3', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
      { title: 'Challenge #4', slug: 'challenge4', concept: Concept('First Concept', 'first-concept', 1) },
      { title: 'Challenge #5', slug: 'challenge5', concept: Concept('Third Concept', 'third-concept', 3) },
      { title: 'Challenge #6', slug: 'challenge6', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
    ])
    expect(extracted).to.deep.equal(concepts);
  });

  it("Extracts multiple concepts from challenge list and sort by order, updating the previous list", () => {
    let prevConcepts = [
      Concept('Zeroth Concept', 'zeroth-concept', 0),
      Concept('Fifth Concept', 'fifth-concept', 5),
    ]
    let concepts = [
      Concept('First Concept', 'first-concept', 1),
      Concept('Second Concept', 'second-concept', 2),
      Concept('Third Concept', 'third-concept', 3),
      Concept('Fourth Concept', 'fourth-concept', 4),
    ]
    let expected = [prevConcepts[0]].concat(concepts).concat([prevConcepts[1]])
    let extracted = extractConcepts([
      { title: 'Challenge #1', slug: 'challenge1', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
      { title: 'Challenge #2', slug: 'challenge2', concept: Concept('Second Concept', 'second-concept', 2) },
      { title: 'Challenge #3', slug: 'challenge3', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
      { title: 'Challenge #4', slug: 'challenge4', concept: Concept('First Concept', 'first-concept', 1) },
      { title: 'Challenge #5', slug: 'challenge5', concept: Concept('Third Concept', 'third-concept', 3) },
      { title: 'Challenge #6', slug: 'challenge6', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
    ], prevConcepts)
    expect(extracted).to.deep.equal(expected);
  });

  it("Groups challenges by concept with highest order", () => {
    let challenges = [
      { title: 'Challenge #1', slug: 'challenge1', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
      { title: 'Challenge #2', slug: 'challenge2', concept: Concept('Second Concept', 'second-concept', 2) },
      { title: 'Challenge #3', slug: 'challenge3', concept: Concept('Third Concept', 'third-concept', 3) },
      { title: 'Challenge #4', slug: 'challenge4', concept: Concept('Third Concept', 'third-concept', 3) },
      { title: 'Challenge #5', slug: 'challenge5', concept: Concept('First Concept', 'first-concept', 1) },
      { title: 'Challenge #6', slug: 'challenge6', concept: Concept('Fourth Concept', 'fourth-concept', 4) },
    ]
    let groups = groupByConcept(challenges)
    let expected = {
      'first-concept': [challenges[4]],
      'second-concept': [challenges[1]],
      'third-concept': [challenges[2], challenges[3]],
      'fourth-concept': [challenges[0], challenges[5]],
    }
    expect(groups).to.deep.equal(expected);
  });

});
