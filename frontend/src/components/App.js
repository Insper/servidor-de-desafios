import React, { Component } from "react";
import { withTranslation } from 'react-i18next';
import { AppBar, Button, Container, CssBaseline, Link, Toolbar } from '@material-ui/core';
import 'fontsource-roboto';
import { CodingChallengeList } from './coding-challenge'
import FitnessCenterIcon from '@material-ui/icons/FitnessCenter';
import { ThemeProvider, withStyles } from '@material-ui/core/styles';
import { customClasses, theme } from '../styles'



class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const t = this.props.t
    const classes = this.props.classes
    const maxContainer = "lg"
    return (
      <React.Fragment>
        <CssBaseline />
        <ThemeProvider theme={theme}>

          <AppBar position="static">
            <Container maxWidth={maxContainer}>
              <Toolbar>
                <div className={classes.appTitle}>
                  <Link href="/" variant="h6" className={classes.homeButton}>
                    <FitnessCenterIcon color="secondary" className={classes.titleIcon} />
                    {t("Python Gym")}
                  </Link>
                </div>
                <Button color="inherit">Login</Button>
              </Toolbar>
            </Container>
          </AppBar>

          <Container maxWidth={maxContainer}>
            <CodingChallengeList />
          </Container>

        </ThemeProvider>
      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(App));

