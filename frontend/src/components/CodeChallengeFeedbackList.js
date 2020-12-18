import React, { forwardRef } from "react"
import { useTranslation } from 'react-i18next'
import Typography from '@material-ui/core/Typography';
import CodeChallengeFeedback from './CodeChallengeFeedback'


const CodeChallengeFeedbackList = forwardRef((props, ref) => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Typography ref={ref} variant="h2" component="h1" gutterBottom={true}>{t("Feedback")}</Typography>

      {props.submissions && props.submissions.length ? props.submissions.map((submission, idx) =>
        <CodeChallengeFeedback
          key={`submission-${submission.id}`}
          submission={submission}
          onLoadButtonClick={props.onLoadButtonClick}
          expanded={idx === 0} />
      ) : <Typography>{t("Waiting for your submission")}</Typography>}

    </React.Fragment>
  )
})

export default CodeChallengeFeedbackList
