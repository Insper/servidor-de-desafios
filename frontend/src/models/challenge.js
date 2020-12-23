exports.extractConcepts = (challenges, oldConcepts) => {
  let concepts = []
  if (oldConcepts) concepts = oldConcepts
  for (let challenge of challenges) {
    let concept = challenge.concept
    if (!concepts.some(t => t.slug === concept.slug)) concepts.push(concept)
  }
  concepts.sort((t1, t2) => t1.order - t2.order)
  return concepts
}


exports.groupByConcept = (challenges) => {
  let groups = {}
  for (let challenge of challenges) {
    let concept = challenge.concept
    let slug = concept.slug
    !(slug in groups) && (groups[slug] = [])
    groups[slug].push(challenge)
  }
  return groups
}
