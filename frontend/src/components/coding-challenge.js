import React, { Component } from "react";
import { List, ListItem, Typography } from '@material-ui/core';
import { extractTags, groupByTag } from "../models/challenge"

class CodingChallengeList extends Component {
  constructor(props) {
    super(props);
    this.state = {
      tags: [],
      challengeGroups: []
    };
  }

  componentDidMount() {
    fetch('/api/coding')
      .then(res => res.json())
      .then((data) => {
        let tags = extractTags(data)
        let groups = groupByTag(data)
        this.setState({ challengeGroups: groups, tags: tags })
      })
      .catch(console.log)
  }

  render() {
    let t = this.props.t;
    const challengeGroups = this.state.tags.map(tag =>
      <React.Fragment key={`tag-${tag.slug}`}>
        <Typography variant="h1" component="h2">{tag.name}</Typography>
        <List component="nav">
          {this.state.challengeGroups[tag.slug].map((challenge) =>
            <ListItem button component="a" key={`challenge-${challenge.slug}`} href={`/${challenge.slug}`}>
              {challenge.title}
            </ListItem>
          )}
        </List>
      </React.Fragment>
    )
    return (
      <React.Fragment>
        {challengeGroups}
      </React.Fragment>
    );
  }
}

export { CodingChallengeList }

