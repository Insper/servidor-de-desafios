import React from "react"
import Typography from '@material-ui/core/Typography'
import List from '@material-ui/core/List'
import ListItem from '@material-ui/core/ListItem'
import { useTranslation } from 'react-i18next'
import CodingChallengeFeedback from './CodingChallengeFeedback'


function CodingChallengeFeedbackList(props) {
  const { t } = useTranslation();
  return (
    <React.Fragment>
      <Typography variant="h2" component="h1" gutterBottom={true}>{t("Feedback")}</Typography>
      <List component="nav">
        {props.submissions ? props.submissions.map((submission) =>
          <ListItem button key={`submission-${submission.id}`}>
            <CodingChallengeFeedback submission={submission} />
          </ListItem>
        ) : null}
      </List>
    </React.Fragment>
  )
}

export default CodingChallengeFeedbackList
