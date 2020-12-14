exports.extractTags = (challenges) => {
  let tags = []
  for (let challenge of challenges) {
    let tag = challenge.tag
    if (!tags.some(t => t.slug === tag.slug)) tags.push(tag)
  }
  tags.sort((t1, t2) => t1.order - t2.order)
  return tags
}


exports.groupByTag = (challenges) => {
  let groups = {}
  for (let challenge of challenges) {
    let tag = challenge.tag
    let slug = tag.slug
    !(slug in groups) && (groups[slug] = [])
    groups[slug].push(challenge)
  }
  return groups
}
