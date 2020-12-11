import React, { Component } from "react"
import { withTranslation } from 'react-i18next';
import { withStyles } from '@material-ui/core/styles';
import { customClasses } from '../styles'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import CircularProgress from '@material-ui/core/CircularProgress'
import Typography from '@material-ui/core/Typography'
import { fetchChallenge } from '../api/pygym'
import MaterialMarkdown from './MaterialMarkdown'

class CodingChallenge extends Component {
  constructor(props) {
    super(props)
    this.state = {}
  }

  componentDidMount() {
    fetchChallenge(this.props.slug)
      .then(res => res.json())
      .then(data => this.setState({ challenge: data }))
      .catch(console.log)
  }

  render() {
    let t = this.props.t;
    const classes = this.props.classes
    const challenge = this.state.challenge
    if (!challenge) return <div className={classes.loadingContainer}><CircularProgress color="secondary" size="10vw" /></div>
    return (
      <React.Fragment>
        <Typography variant="h1" gutterBottom={true}>{challenge.title}</Typography>
        <MaterialMarkdown children={challenge.question} />
      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(CodingChallenge))

