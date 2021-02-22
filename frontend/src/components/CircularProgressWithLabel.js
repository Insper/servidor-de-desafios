import React from 'react';
import PropTypes from 'prop-types';
import CircularProgress from '@material-ui/core/CircularProgress';
import Typography from '@material-ui/core/Typography';
import Box from '@material-ui/core/Box';

import { useStyles } from '../styles'

export default function CircularProgressWithLabel(props) {
  const { value, maxValue, ...otherProps } = props
  const classes = useStyles()

  return (
    <Box className={classes.centerContent} mt={1} mb={2}>
      <Box position="relative" display="inline-flex">
        <CircularProgress color="secondary" variant="determinate" value={value * 100 / maxValue} {...otherProps} />
        <Box
          top={0}
          left={0}
          bottom={0}
          right={0}
          position="absolute"
          display="flex"
          alignItems="center"
          justifyContent="center"
        >
          <Typography variant="caption" component="div" color="textSecondary">{value}/{maxValue}</Typography>
        </Box>
      </Box>
    </Box>
  );
}

CircularProgressWithLabel.propTypes = {
  value: PropTypes.number.isRequired,
  maxValue: PropTypes.number.isRequired,
};
