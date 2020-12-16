import React, { useState } from "react"
import { useTranslation } from 'react-i18next'
import PropTypes from 'prop-types';
import Accordion from '@material-ui/core/Accordion';
import AccordionActions from '@material-ui/core/AccordionActions';
import AccordionSummary from '@material-ui/core/AccordionSummary';
import AccordionDetails from '@material-ui/core/AccordionDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import Typography from '@material-ui/core/Typography'
import Box from '@material-ui/core/Box'
import Button from '@material-ui/core/Button'
import Tabs from '@material-ui/core/Tabs';
import Tab from '@material-ui/core/Tab';
import Paper from '@material-ui/core/Paper'
import Divider from '@material-ui/core/Divider';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import SvgIcon from '@material-ui/core/SvgIcon'
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import ErrorIcon from '@material-ui/icons/Error';
import { useStyles } from '../styles'
import { RotateSpinner } from "react-spinners-kit";


function ListTabPanel(props) {
  const { children, value, index, label, ...other } = props;

  let content
  if (value === index) content = (
    <List aria-label={label}>
      {children}
    </List>
  )

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {content}
    </div>
  );
}

ListTabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired,
  label: PropTypes.string,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

function CodingChallengeFeedbackList(props) {
  const { t } = useTranslation();
  const classes = useStyles()
  const [selectedTab, setSelectedTab] = useState(0)
  const [expanded, setExpanded] = useState(props.expanded)

  const handleLoadButtonClick = () => {
    if (props.onLoadButtonClick) props.onLoadButtonClick(props.submission.id)
  }

  const handleTabChange = (event, newValue) => {
    setSelectedTab(newValue);
  };


  const resultIconSize = 30
  let result
  let text
  let loadButton
  let details
  if (props.submission.id === "running") {
    result = <RotateSpinner size={resultIconSize} color="#E0E0E0" />
    text = <Typography>{t("Running tests")}</Typography>
  }
  else if (props.submission.id === "error") {
    result = <SvgIcon><ErrorIcon /></SvgIcon>
    text = <Typography>{t("An error occurred in the server")}</Typography>
  }
  else {
    if (props.submission.success) result = <SvgIcon className={classes.success}><CheckCircleIcon /></SvgIcon>
    else result = <SvgIcon className={classes.danger}><CancelIcon /></SvgIcon>
    text = <Typography>{`${t("Submission sent")} ${t("fulldate", { date: new Date(props.submission.creation_date) })}`}</Typography>
    loadButton = <Button size="small" color="primary" onClick={handleLoadButtonClick}>{t("Load this submission")}</Button>
    details = (
      <AccordionDetails>
        <Paper className={classes.fillParent}>
          <Tabs
            value={selectedTab}
            onChange={handleTabChange}
            indicatorColor="primary"
            centered
          >
            <Tab label={t("Stacktraces")} {...a11yProps(0)} />
            <Tab label={t("Console output")} {...a11yProps(1)} />
          </Tabs>
          <ListTabPanel className={classes.contentHolder} label="stacktraces" value={selectedTab} index={0}>
            {props.submission.stacktraces.map((stacktrace, idx) => (
              <ListItem key={`stacktrace-${props.submission.id}-${idx}`}>
                <Box className={classes.fillParent}>
                  {stacktrace.split("\n").map((line, idx2) => (
                    <Typography className={classes.sourceCode} component="pre" key={`stacktrace-${props.submission.id}-${idx}-${idx2}`}>{line}</Typography>)
                  )}
                  <Divider />
                </Box>
              </ListItem>)
            )}
          </ListTabPanel>
          <ListTabPanel className={classes.contentHolder} label="stdouts"
            value={selectedTab} index={1}>
            <ListItem>
              <Typography>{props.submission.stdouts}</Typography>
            </ListItem>
          </ListTabPanel>
        </Paper>
      </AccordionDetails>
    )
  }

  const headerId = `feedback${props.submission.id}-header`
  const contendId = `feedback${props.submission.id}-content`

  return (
    <Accordion expanded={expanded} onChange={(event, isExpanded) => setExpanded(isExpanded)}>
      <AccordionSummary
        expandIcon={<ExpandMoreIcon />}
        aria-controls={contendId}
        id={headerId}>
        <Box width={resultIconSize} height={resultIconSize} className={classes.centerContent}>
          {result}
        </Box>
        {text}
      </AccordionSummary>
      {details}
      <AccordionActions>
        {loadButton}
      </AccordionActions>
    </Accordion>
  )
}

export default CodingChallengeFeedbackList
