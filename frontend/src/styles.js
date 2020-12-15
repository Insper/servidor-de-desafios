import { createMuiTheme, makeStyles, responsiveFontSizes } from '@material-ui/core/styles';

// Python color pallete (https://www.schemecolor.com/python-logo-colors.php#:~:text=The%20Python%20Logo%20Colors%20with,and%20Granite%20Gray%20(%23646464).):
const BLUE1 = '#4B8BBE'
const BLUE2 = '#306998'
const YELLOW1 = '#FFE873'
const YELLOW2 = '#FFD43B'
const GRAY1 = '#646464'
const GRAY2 = '#E0E0E0'
const SUCCESS = '#39C27C'
const DANGER = '#FF665C'


let theme = createMuiTheme({
  palette: {
    primary: {
      main: BLUE2,
      light: BLUE1,
    },
    secondary: {
      main: YELLOW2,
      light: YELLOW1,
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
    display: "flex"
  },
  loginLogo: {
    maxHeight: "30vh"
  },
  loginBack: {
    backgroundColor: GRAY2,
    display: "flex",
    flexDirection: "column",
    alignItems: "center"
  },
  centerVerticalContent: {
    display: "flex",
    flexDirection: "column",
    alignItems: "center",
    gap: "2em",
  },
  blankLink: {
    textDecoration: "none",
    display: "block",
  },
  appLogo: {
    maxWidth: "20em",
  },
  loadingContainer: {
    margin: "8em",
    display: "flex",
    justifyContent: "center",
  },
  centeredImg: {
    display: "block",
    marginLeft: "auto",
    marginRight: "auto",
  },
  flexbox: {
    display: "flex",
    flexDirection: "column",
  },
  fillParent: {
    flexGrow: 1,
  },
  gridItem: {
    paddingLeft: theme.spacing(3),
    paddingRight: theme.spacing(3),
  },
  success: {
    color: SUCCESS,
  },
  danger: {
    color: DANGER,
  }
}

const useStyles = makeStyles(customClasses)


export { customClasses, useStyles, theme }
