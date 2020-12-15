import React from "react"
import { useTranslation } from 'react-i18next'
import Typography from '@material-ui/core/Typography'
import SvgIcon from '@material-ui/core/SvgIcon'
import CheckCircleIcon from '@material-ui/icons/CheckCircle';
import CancelIcon from '@material-ui/icons/Cancel';
import { useStyles } from '../styles'
import { RotateSpinner } from "react-spinners-kit";


function CodingChallengeFeedbackList(props) {
  const { t } = useTranslation();
  const classes = useStyles()
  let result
  let text
  if (props.submission.id === "running") {
    result = <RotateSpinner size={30} color="#E0E0E0" />
    text = <Typography>{t("Running tests")}</Typography>
  }
  else {
    if (props.submission.success) result = <SvgIcon className={classes.success}><CheckCircleIcon /></SvgIcon>
    else result = <SvgIcon className={classes.danger}><CancelIcon /></SvgIcon>
    text = <Typography>{t("fulldate", { date: new Date(props.submission.creation_date) })}</Typography>
  }
  return (
    <React.Fragment>
      {result}
      {text}
    </React.Fragment>
  )
}

export default CodingChallengeFeedbackList
