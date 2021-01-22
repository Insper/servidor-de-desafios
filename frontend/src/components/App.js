import React, { useState, useEffect } from "react";
import { useDispatch } from 'react-redux'
import CookieConsent from "react-cookie-consent";
import {
  BrowserRouter as Router,
  Switch,
  Route,
  Link,
} from "react-router-dom";
import { useTranslation } from 'react-i18next'
import clsx from 'clsx'
import AppBar from '@material-ui/core/AppBar'
import Box from '@material-ui/core/Box'
import CssBaseline from '@material-ui/core/CssBaseline'
import IconButton from '@material-ui/core/IconButton'
import MenuIcon from '@material-ui/icons/Menu'
import Toolbar from '@material-ui/core/Toolbar'
import { ThemeProvider } from '@material-ui/core/styles'
import 'fontsource-roboto';
import CodeChallenge from './CodeChallenge'
import TraceChallenge from './TraceChallenge'
import UserOverview from './UserOverview'
import logo from '../img/logo.svg'
import UserButton from './UserButton'
import { getUserData } from '../api/pygym'
import { useStyles, theme } from '../styles'
import ROUTES from '../routes'
import AppDrawer from "./AppDrawer"
import ContentChallenges from "./ContentChallenges"
import ContentPage from "./ContentPage"
import ThanksPage from "./ThanksPage"
import { fetchContents } from '../features/contents/contentsSlice'
import { fetchConcepts } from '../features/concepts/conceptsSlice'

function App(props) {
  const classes = useStyles()
  const { t } = useTranslation()
  const dispatch = useDispatch()

  const [user, setUser] = useState({})
  const [mobileOpen, setMobileOpen] = useState(false)

  useEffect(() => {
    getUserData()
      .then(setUser)
      .catch(console.log)
  }, [])

  useEffect(() => dispatch(fetchContents()), [])
  useEffect(() => dispatch(fetchConcepts()), [])

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen)
  }

  return (
    <React.StrictMode>
      <CssBaseline />
      <ThemeProvider theme={theme}>
        <Router>
          <div className={classes.root}>
            <AppBar position="fixed" className={classes.appBar}>
              <CookieConsent
                location="bottom"
                buttonText={t("I agree")}
              >
                {t("This website uses cookies to enhance the user experience")}.
              </CookieConsent>
              <Toolbar>
                <IconButton
                  color="inherit"
                  aria-label={t("open drawer")}
                  edge="start"
                  onClick={handleDrawerToggle}
                  className={classes.menuButton}
                >
                  <MenuIcon />
                </IconButton>
                <div className={classes.appTitle}>
                  <Link to={ROUTES.home.link()} className={classes.homeButton}>
                    <img src={logo} alt="Logo" className={classes.appLogo} />
                  </Link>
                </div>
                <UserButton user={user} />
              </Toolbar>
            </AppBar>

            <AppDrawer ariaLabel={t("course contents")} mobileOpen={mobileOpen} onClose={handleDrawerToggle} />

            <main className={clsx(classes.content, classes.fillParent)}>
              <div className={classes.toolbar} />
              <Box m={3} className={classes.flexbox}>
                <Switch>
                  <Route exact path={ROUTES.home.path}>
                    <UserOverview user={user} />
                  </Route>
                  <Route path={ROUTES.thanks.path} render={(props) =>
                    <ThanksPage />
                  } />
                  <Route path={ROUTES.challenge.path} render={(props) =>
                    <CodeChallenge slug={props.match.params.slug} />
                  } />
                  <Route path={ROUTES.trace.path} render={(props) =>
                    <TraceChallenge slug={props.match.params.slug} />
                  } />
                  <Route path={ROUTES.contentChallenges.path} render={(props) =>
                    <ContentChallenges slug={props.match.params.slug} />
                  } />
                  <Route path={ROUTES.page.path} render={(props) =>
                    <ContentPage contentSlug={props.match.params.slug} pageSlug={props.match.params.page} />
                  } />
                  {/* Contents must be last so the other routes take priority */}
                  <Route path={ROUTES.content.path} render={(props) =>
                    <ContentPage contentSlug={props.match.params.slug} />
                  } />
                </Switch>
              </Box>
            </main>
          </div>
        </Router>
      </ThemeProvider>
    </React.StrictMode >
  );
}

export default App

