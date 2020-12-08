import React from "react";
import { render } from "react-dom";
import { I18nextProvider } from "react-i18next";
import App from "./components/App";
import i18n from "./i18n";
import './App.css'


const container = document.getElementById("app");

render(
  <I18nextProvider i18n={i18n}>
    <App />
  </I18nextProvider>,
  container
);

