import React, { Component } from "react"
import { withTranslation } from 'react-i18next';
import { withStyles } from '@material-ui/core/styles';
import { customClasses } from '../styles'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import CircularProgress from '@material-ui/core/CircularProgress'
import Box from '@material-ui/core/Box';
import ButtonGroup from '@material-ui/core/ButtonGroup';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper'
import { fetchChallenge, postChallenge, fetchSubmissionList } from '../api/pygym'
import MaterialMarkdown from './MaterialMarkdown'
import Editor from "@monaco-editor/react";
import { FillSpinner as Loader } from "react-spinners-kit";
import CodingChallengeFeedbackList from "./CodingChallengeFeedbackList"

class CodingChallenge extends Component {
  constructor(props) {
    super(props)
    this.state = {
      submissions: [],
    }
    this.editorRef = React.createRef();
    this.handleEditorDidMount = this.handleEditorDidMount.bind(this)
    this.postSolution = this.postSolution.bind(this)
  }

  componentDidMount() {
    fetchChallenge(this.props.slug)
      .then(res => res.json())
      .then(data => this.setState({ challenge: data }))
      .catch(console.log)

    fetchSubmissionList(this.props.slug)
      .then(res => res.json())
      .then(data => this.setState({ submissions: data }))
      .catch(console.log)
  }

  handleEditorDidMount(_, editor) {
    this.editorRef.current = editor
  }

  postSolution() {
    this.setState({
      submissions: [{ id: "running" }].concat(this.state.submissions)
    })

    postChallenge(this.props.slug, this.editorRef.current.getValue())
      .then(res => res.json())
      .then(data => {
        let submissions = [data].concat(this.state.submissions.slice(1))
        this.setState({ submissions: submissions })
      })
      .catch(data => {
        let submissions = [{ id: "error" }].concat(this.state.submissions.slice(1))
        this.setState({ submissions: submissions })
        console.log(data)
      })
  }

  render() {
    let t = this.props.t;
    const classes = this.props.classes
    const challenge = this.state.challenge
    const functionName = (challenge && challenge.function_name) ? <Typography paragraph={true}>{t("The name of your function must be ")} <SyntaxHighlighter language="python" customStyle={{ padding: "0.1em" }} PreTag={"span"} style={prism}>{challenge.function_name}</SyntaxHighlighter></Typography> : ''
    if (!challenge) return <div className={classes.loadingContainer}><CircularProgress color="secondary" size="10vw" /></div>
    return (
      <React.Fragment>

        <Grid container>
          <Grid item className={classes.gridItem} md={6}>
            <Typography variant="h2" component="h1" gutterBottom={true}>{challenge.title}</Typography>
            <MaterialMarkdown children={challenge.question} />
            {functionName}
          </Grid>

          <Grid className={`${classes.flexbox} ${classes.gridItem}`} container item md={6}>
            <Paper className={`${classes.flexbox} ${classes.fillParent}`} elevation={3}>
              <Box className={classes.fillParent} mt={2} mb={2}>
                <Editor
                  // height="80vh" // By default, it fully fits with its parent
                  theme={"light"}
                  editorDidMount={this.handleEditorDidMount}
                  language={"python"}
                  loading={<Loader />}
                  value={""}
                  options={{ lineNumbers: "on", wordWrap: "on" }}
                />
              </Box>
            </Paper>
            <Box mt={2}>
              <ButtonGroup fullWidth={true}>
                <Button variant="contained" color="primary" onClick={this.postSolution}>
                  {t("Submit")}
                </Button>
              </ButtonGroup>
            </Box>
          </Grid>

          <Grid className={classes.gridItem} item md={12}>
            <Box mt={2}>
              <CodingChallengeFeedbackList submissions={this.state.submissions} />
            </Box>
          </Grid>
        </Grid>

      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(CodingChallenge))

