import React from "react";
import { render } from "react-dom";
import { I18nextProvider } from "react-i18next";
import CssBaseline from '@material-ui/core/CssBaseline';
import { ThemeProvider } from '@material-ui/core/styles';
import Login from "./components/login";
import i18n from "./i18n";
import './App.css'
import { theme } from './styles'


const container = document.getElementById("app");

render(
  <I18nextProvider i18n={i18n}>
    <CssBaseline />
    <ThemeProvider theme={theme}>
      <Login />
    </ThemeProvider>
  </I18nextProvider>,
  container
);

