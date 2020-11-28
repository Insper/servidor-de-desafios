import React, { Component } from "react";
import { render } from "react-dom";

class App extends Component {
  constructor(props) {
    super(props);
    this.state = {
      text: "Worked!"
    };
  }

  render() {
    return (
      <p>{this.state.text}</p>
    );
  }
}

export default App;

const container = document.getElementById("app");
render(<App />, container);
