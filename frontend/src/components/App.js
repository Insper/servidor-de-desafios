import React, { Component } from "react";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link
} from "react-router-dom";
import { withTranslation } from 'react-i18next';
import CssBaseline from '@material-ui/core/CssBaseline';
import 'fontsource-roboto';
import { ThemeProvider, withStyles } from '@material-ui/core/styles';
import { customClasses, theme } from '../styles'
import Home from './home'



class App extends Component {
  constructor(props) {
    super(props);
  }

  render() {

    return (
      <React.Fragment>
        <CssBaseline />
        <ThemeProvider theme={theme}>
          <Router>
            <Switch>
              <Route path="/">
                <Home />
              </Route>
            </Switch>
          </Router>
        </ThemeProvider>
      </React.Fragment>
    );
  }
}

export default withTranslation()(withStyles(customClasses)(App));

