import React, { useState, useEffect } from "react";
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Typography from '@material-ui/core/Typography';
import { extractConcepts, groupByConcept } from "../models/challenge"
import { fetchChallengeList } from '../api/pygym'
import ROUTES from '../routes'

function CodeChallengeList(props) {
  const [concepts, setConcepts] = useState([])
  const [challengeGroups, setChallengeGroups] = useState([])

  useEffect(() => {
    fetchChallengeList()
      .then(res => res.json())
      .then((data) => {
        let concepts = extractConcepts(data)
        let groups = groupByConcept(data)
        setChallengeGroups(groups)
        setConcepts(concepts)
      })
      .catch(console.log)
  }, []);

  return (
    <React.Fragment>
      {concepts.map(concept =>
        <React.Fragment key={`concept-${concept.slug}`}>
          <Typography variant="h1" component="h2" gutterBottom={true}>{concept.name}</Typography>
          <List component="nav">
            {challengeGroups[concept.slug].map((challenge) =>
              <ListItem button component="a" key={`challenge-${challenge.slug}`} href={ROUTES.challenge.link({ slug: challenge.slug })}>
                {challenge.title}
              </ListItem>
            )}
          </List>
        </React.Fragment>
      )}
    </React.Fragment>
  );
}

export default CodeChallengeList

