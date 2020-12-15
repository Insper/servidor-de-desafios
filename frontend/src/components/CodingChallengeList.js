import React, { useState, useEffect } from "react";
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import Typography from '@material-ui/core/Typography';
import { extractTags, groupByTag } from "../models/challenge"
import { fetchChallengeList } from '../api/pygym'
import ROUTES from '../routes'

function CodingChallengeList(props) {
  const [tags, setTags] = useState([])
  const [challengeGroups, setChallengeGroups] = useState([])

  useEffect(() => {
    fetchChallengeList()
      .then(res => res.json())
      .then((data) => {
        let tags = extractTags(data)
        let groups = groupByTag(data)
        setChallengeGroups(groups)
        setTags(tags)
      })
      .catch(console.log)
  }, []);

  return (
    <React.Fragment>
      {tags.map(tag =>
        <React.Fragment key={`tag-${tag.slug}`}>
          <Typography variant="h1" component="h2" gutterBottom={true}>{tag.name}</Typography>
          <List component="nav">
            {challengeGroups[tag.slug].map((challenge) =>
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

export default CodingChallengeList

