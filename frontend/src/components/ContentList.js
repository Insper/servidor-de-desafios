import React, { useState, useEffect } from "react";
import { useTranslation } from 'react-i18next';
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Typography from '@material-ui/core/Typography';
import { extractConcepts, groupByConcept } from "../models/challenge"
import { getChallengeList, getTraceList } from '../api/pygym'
import ROUTES from '../routes'

function ContentList(props) {
  const [concepts, setConcepts] = useState([])
  const [challengeGroups, setChallengeGroups] = useState([])
  const [traceGroups, setTraceGroups] = useState([])
  const { t } = useTranslation()

  useEffect(() => {
    getChallengeList()
      .then((data) => {
        let updatedConcepts = extractConcepts(data, concepts)
        let groups = groupByConcept(data)
        setChallengeGroups(groups)
        setConcepts(updatedConcepts)
      })
      .catch(console.log)
    getTraceList()
      .then((data) => {
        let updatedConcepts = extractConcepts(data, concepts)
        let groups = groupByConcept(data)
        setTraceGroups(groups)
        setConcepts(updatedConcepts)
      })
  }, []);

  return (
    <>
      {concepts.map(concept =>
        <React.Fragment key={`concept-${concept.slug}`}>
          <Typography variant="h1" component="h2" gutterBottom={true}>{concept.name}</Typography>
          {Array.isArray(challengeGroups[concept.slug]) && challengeGroups[concept.slug].length ?
            <>
              <Typography variant="h3">{t("Code Challenges")}</Typography>
              <List component="nav">
                {challengeGroups[concept.slug].map((challenge) =>
                  <ListItem button component="a" key={`challenge-${challenge.slug}`} href={ROUTES.challenge.link({ slug: challenge.slug })}>
                    {challenge.title}
                  </ListItem>
                )}
              </List>
            </>
            : null}
          {Array.isArray(traceGroups[concept.slug]) && traceGroups[concept.slug].length ?
            <>
              <Typography variant="h3">{t("Trace Challenges")}</Typography>
              <List component="nav">
                {traceGroups[concept.slug].map((challenge) =>
                  <ListItem button component="a" key={`trace-${challenge.slug}`} href={ROUTES.trace.link({ slug: challenge.slug })}>
                    {challenge.title}
                  </ListItem>
                )}
              </List>
            </>
            : null}
        </React.Fragment>
      )}
    </>
  );
}

export default ContentList

