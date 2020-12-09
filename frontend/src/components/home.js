import React, { Component } from "react";
import { withTranslation } from 'react-i18next';
import { withStyles } from '@material-ui/core/styles';
import Container from '@material-ui/core/Container';
import { CodingChallengeList } from './coding-challenge'
import { customClasses } from '../styles'


class Home extends Component {
  constructor(props) {
    super(props);
  }

  render() {

    return (
      <React.Fragment>
        <Container maxWidth={this.props.maxContainer}>
          <CodingChallengeList />
        </Container>
      </React.Fragment>
    )
  }
}

export default withTranslation()(withStyles(customClasses)(Home));
