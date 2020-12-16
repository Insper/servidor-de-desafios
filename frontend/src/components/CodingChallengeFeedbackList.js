import React, { forwardRef } from "react"
import { useTranslation } from 'react-i18next'
import Typography from '@material-ui/core/Typography';
import CodingChallengeFeedback from './CodingChallengeFeedback'


const CodingChallengeFeedbackList = forwardRef((props, ref) => {
  const { t } = useTranslation();

  return (
    <React.Fragment>
      <Typography ref={ref} variant="h2" component="h1" gutterBottom={true}>{t("Feedback")}</Typography>

      {props.submissions ? props.submissions.map((submission, idx) =>
        <CodingChallengeFeedback
          key={`submission-${submission.id}`}
          submission={submission}
          onLoadButtonClick={props.onLoadButtonClick}
          expanded={idx === 0} />
      ) : null}

    </React.Fragment>
  )
})

export default CodingChallengeFeedbackList
