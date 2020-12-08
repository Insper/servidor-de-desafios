import React, { Component } from "react";
import { withTranslation } from 'react-i18next';
import { AppBar, Button, Container, CssBaseline, Link, Toolbar } from '@material-ui/core';
import 'fontsource-roboto';
import { CodingChallengeList } from './coding-challenge'
import { ThemeProvider, withStyles } from '@material-ui/core/styles';
import { customClasses, theme } from '../styles'
import logoPt from '../img/logo-horizontal-small-pt.png'
import logoDefault from '../img/logo-horizontal-small.png'


class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    const t = this.props.t
    const i18n = this.props.i18n
    const classes = this.props.classes
    const maxContainer = "lg"
    const logoImg = i18n.language === 'pt' ? logoPt : logoDefault
    return (
      <React.Fragment>
        <CssBaseline />
        <ThemeProvider theme={theme}>

          <AppBar position="static">
            <Container maxWidth={maxContainer}>
              <Toolbar disableGutters={true}>
                <div className={classes.appTitle}>
                  <Link href="/" className={classes.homeButton}>
                    <img src={logoImg} alt="Logo" />
                  </Link>
                </div>
                <Button color="inherit" href="/login">Login</Button>
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

