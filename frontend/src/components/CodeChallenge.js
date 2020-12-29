import React, { useState, useEffect, useRef } from "react";
import { useTranslation } from 'react-i18next';
import { useStyles } from '../styles'
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { prism } from 'react-syntax-highlighter/dist/esm/styles/prism';
import CircularProgress from '@material-ui/core/CircularProgress'
import Box from '@material-ui/core/Box';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import Typography from '@material-ui/core/Typography'
import Paper from '@material-ui/core/Paper'
import Snackbar from '@material-ui/core/Snackbar';
import InsertDriveFileIcon from '@material-ui/icons/InsertDriveFile';
import SendIcon from '@material-ui/icons/Send';
import { DropzoneDialog } from 'material-ui-dropzone';
import { fetchChallenge, postChallenge, fetchSubmissionList, fetchSubmissionCode } from '../api/pygym'
import MaterialMarkdown from './MaterialMarkdown'
import Editor from "@monaco-editor/react";
import LoadingResultsProgress from './LoadingResultsProgress'
import CodeChallengeFeedbackList from "./CodeChallengeFeedbackList"
import Alert from "./Alert"

function CodeChallenge(props) {
  const { t } = useTranslation()
  const classes = useStyles()
  const [challenge, setChallenge] = useState({})
  const [submissions, setSubmissions] = useState([])
  const [previousCode, setPreviousCode] = useState("")
  const [fileDialogOpen, setFileDialogOpen] = useState(false)
  const [submitEnabled, setSubmitEnabled] = useState(false)
  const [snackbarOpen, setSnackbarOpen] = useState(false)
  const [passedTests, setPassedTests] = useState(false)
  const editorRef = useRef()
  const feedbackListRef = useRef()

  useEffect(() => {
    fetchChallenge(props.slug)
      .then(res => res.json())
      .then(setChallenge)
      .catch(console.log)

    fetchSubmissionList(props.slug)
      .then(res => res.json())
      .then(setSubmissions)
      .catch(console.log)
  }, []);

  const handleEditorDidMount = (_, editor) => {
    editorRef.current = editor
    setSubmitEnabled(true)
  }

  const handleCodeFileUpload = (file) => {
    const reader = new FileReader()
    reader.addEventListener('load', (event) => {
      editorRef.current.setValue(event.target.result)
    })
    reader.readAsText(file)
  }

  const postSolution = () => {
    setSubmitEnabled(false)
    setPassedTests(false)
    setSubmissions([{ id: "running" }].concat(submissions))
    feedbackListRef.current.scrollIntoView()

    postChallenge(props.slug, editorRef.current.getValue())
      .then(res => res.json())
      .then(data => {
        if (data.success) setPassedTests(true)
        setSubmissions([data].concat(submissions))
      })
      .catch(data => {
        setSubmissions([{ id: "error" }].concat(submissions))
        console.log(data)
      })
      .finally(() => {
        setSnackbarOpen(true)
        setSubmitEnabled(true)
      })
  }

  const loadFile = () => {
    setFileDialogOpen(true)
  }

  const loadSubmissionCode = (submissionId) => {
    fetchSubmissionCode(props.slug, submissionId)
      .then(res => res.json())
      .then(data => {
        if (data.code) {
          setPreviousCode(data.code)
          if (editorRef.current) editorRef.current.setValue(data.code)
        }
      })
      .catch(console.log)
  }

  const handleCloseSnackbar = (event, reason) => {
    if (reason === 'clickaway') {
      return;
    }

    setSnackbarOpen(false)
  }

  if (submissions && submissions[0] && !previousCode) {
    loadSubmissionCode(submissions[0].id)
  }

  const functionName = (challenge && challenge.function_name) ? <Typography paragraph={true}>{t("The name of your function must be ")} <SyntaxHighlighter language="python" customStyle={{ padding: "0.1em" }} PreTag={"span"} style={prism}>{challenge.function_name}</SyntaxHighlighter></Typography> : ''
  if (!challenge) return <div className={classes.loadingContainer}><CircularProgress color="secondary" size="10vw" /></div>

  return (
    <Box mb={3}>
      <Grid container>
        <Snackbar open={snackbarOpen} autoHideDuration={5000} onClose={handleCloseSnackbar}>
          <Alert onClose={handleCloseSnackbar} severity={passedTests ? "success" : "error"}>{passedTests ? t("Passed all tests") : t("Failed some test")}!</Alert>
        </Snackbar>

        <Grid item className={classes.gridItem} md={6}>
          <Typography variant="h2" component="h1" gutterBottom={true}>{challenge.title}</Typography>
          <MaterialMarkdown children={challenge.question} />
          {functionName}
        </Grid>

        <Grid className={`${classes.flexbox} ${classes.gridItem}`} container item md={6}>
          <Paper className={`${classes.flexbox} ${classes.fillParent}`} elevation={3}>
            <Box className={classes.editor} mt={2} mb={2}>
              <Editor
                // height="80vh" // By default, it fully fits with its parent
                theme={"light"}
                editorDidMount={handleEditorDidMount}
                language={"python"}
                loading={<LoadingResultsProgress strokeWeight={3} />}
                value={previousCode}
                options={{ lineNumbers: "on", wordWrap: "on" }}
              />
            </Box>
          </Paper>
          <Box mt={2}>
            <Button variant="contained" color="primary" disabled={!submitEnabled} onClick={loadFile} fullWidth={true} startIcon={<InsertDriveFileIcon />}>
              {t("Load file")}
            </Button>

            <DropzoneDialog
              acceptedFiles={['.py']}
              dialogTitle={t("Upload code")}
              dropzoneText={t("Drag and drop a file here or click")}
              cancelButtonText={t("Cancel")}
              submitButtonText={t("Submit")}
              getFileLimitExceedMessage={(filesLimit) => `${t("Maximum allowed number of files exceeded")} .${t("Only {{filesLimit}} allowed", { filesLimit: filesLimit })}`}
              getFileAddedMessage={(fileName) => t("{{fileName}} successfully added", { fileName: fileName })}
              getFileRemovedMessage={(fileName) => t("File {{fileName}} removed", { fileName: fileName })}
              getDropRejectMessage={(rejectedFile) => t("File {{rejectedFileName}} was rejected", { rejectedFileName: rejectedFile.name })}
              maxFileSize={1000000}
              filesLimit={1}
              multiple={false}
              open={fileDialogOpen}
              onClose={() => setFileDialogOpen(false)}
              onSave={(files) => {
                files.map(handleCodeFileUpload)
                setFileDialogOpen(false);
              }}
              showPreviews={false}
            />

          </Box>
          <Box mt={2}>
            <Button variant="contained" disabled={!submitEnabled} color="primary" onClick={postSolution} fullWidth={true} endIcon={<SendIcon />}>
              {t("Submit")}
            </Button>
          </Box>
        </Grid>

        <Grid className={classes.gridItem} item md={12}>
          <Box mt={2}>
            <CodeChallengeFeedbackList ref={feedbackListRef} submissions={submissions} onLoadButtonClick={loadSubmissionCode} />
          </Box>
        </Grid>
      </Grid>
    </Box>
  );
}

export default CodeChallenge

