import { createMuiTheme, responsiveFontSizes } from '@material-ui/core/styles';

/*
Python color pallete (https://www.schemecolor.com/python-logo-colors.php#:~:text=The%20Python%20Logo%20Colors%20with,and%20Granite%20Gray%20(%23646464).):
  #4B8BBE - blue 1
  #306998 - blue 2
  #FFE873 - yellow 1
  #FFD43B - yellow 2
  #646464 - gray
*/


let theme = createMuiTheme({
  palette: {
    primary: {
      main: '#4B8BBE',
    },
    secondary: {
      main: '#FFE873',
    },
  },
});
theme = responsiveFontSizes(theme);


const customClasses = {
  titleIcon: {
    marginRight: "10px"
  },
  appTitle: {
    flexGrow: 1
  },
  homeButton: {
    color: "inherit",
    "&:active": { textDecoration: "none" },
    "&:hover": { textDecoration: "none" },
    "&: visited": { textDecoration: "none" }
  },
}


export { customClasses, theme }
