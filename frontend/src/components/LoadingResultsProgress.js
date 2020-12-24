// Reference: https://codepen.io/ericadamski/pen/RqjGzz
import React from "react";
import PropTypes from 'prop-types'
import styled, { css, keyframes } from "styled-components";
import { Colors } from "../styles"

const ProgressState = {
  RUNNING: 0,
  ERROR: 1,
  SUCCESS: 2
};

ProgressState.resolve = state => {
  if (typeof state === 'number') return state
  if (typeof state !== 'string') throw "State must be either a string or a number"
  return ProgressState[state.toUpperCase()]
}

const Rotate = keyframes`
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
`;

const Complete = (state, length) => keyframes`
  from {
    stroke-dashoffset: ${length};
    stroke: ${Colors.BLUE2};
  }
  to {
    stroke-dashoffset: 0;
    stroke: ${state === ProgressState.SUCCESS ? Colors.SUCCESS : Colors.DANGER};
  }
`;

const Dash = (length) => keyframes`
  0% { stroke-dashoffset: ${Math.floor(length * 0)}; }
  50% {
    stroke-dashoffset: ${Math.floor(length * 0.1)};
  }
  100% {
    stroke-dashoffset: ${Math.floor(0)};
  }
`;

const Stroke = keyframes`
  100% {
    stroke-dashoffset: 0;
  }
`;

const Circle = styled.circle`
  stroke-dasharray: ${(props) => Math.floor(props.length * 0.9)};
  stroke-dashoffset: 0;
  transform-origin: center;
  animation: ${(props) => Dash(props.length)} ${(props) => props.animDur}
    ease-in-out infinite;
  stroke: ${Colors.BLUE2};
  will-change: animation;

  ${(props) =>
    props.state !== ProgressState.RUNNING &&
    css`
      stroke: ${props.state === ProgressState.SUCCESS ? Colors.SUCCESS : Colors.DANGER};
      stroke-dasharray: ${(props) => props.length};
      animation: ${Complete(props.state, props.length)} 0.7s ease-in-out;
    `};
`;

const BackgroundCircle = styled.circle`
  stroke-dashoffset: 0;
  transform-origin: center;
  stroke: ${(props) =>
    props.state === ProgressState.RUNNING ? Colors.YELLOW2 : Colors.BLUE2};
`;

const Check = styled.path`
  transform-origin: 50% 50%;
  stroke-dasharray: ${(props) => props.length};
  stroke-dashoffset: ${(props) => props.length};
  stroke: ${Colors.SUCCESS};
  animation: ${Stroke} 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
  will-change: animation;
`;

const Cross = styled.path`
  transform-origin: 50% 50%;
  stroke-dasharray: ${(props) => props.length};
  stroke-dashoffset: ${(props) => props.length};
  stroke: ${Colors.DANGER};
  animation: ${Stroke} 0.3s cubic-bezier(0.65, 0, 0.45, 1) 0.8s forwards;
  will-change: animation;
`;

const Wrapper = styled.svg`
  animation: ${Rotate} ${(props) => props.animDur} linear infinite;
  will-change: animation;

  ${(props) =>
    props.state !== ProgressState.RUNNING &&
    css`
      animation: none;
    `};
`;

function LoadingResultsProgress(props) {
  const side = 256;
  const sw = 10;
  const r = 100;
  const length = Math.floor(2 * Math.PI * r);
  const animDur = "1.4s";
  const state = ProgressState.resolve(props.state)

  return (
    <Wrapper
      state={state}
      width={props.size}
      height={props.size}
      viewBox={`0 0 ${side} ${side}`}
      animDur={animDur}
      xmlns="http://www.w3.org/2000/svg"
    >
      <BackgroundCircle
        state={state}
        fill="none"
        strokeWidth={sw}
        cx={Math.floor(side / 2)}
        cy={Math.floor(side / 2)}
        r={r}
      />
      <Circle
        state={state}
        fill="none"
        strokeWidth={sw}
        cx={Math.floor(side / 2)}
        cy={Math.floor(side / 2)}
        r={r}
        length={length}
        animDur={animDur}
      />
      {(state === ProgressState.SUCCESS && (
        <Check
          fill="none"
          length={side / 2}
          strokeWidth={sw}
          d={`M ${side / 2.7} ${side / 2} l ${side / 10} ${side / 11} ${side / 5
            } ${-side / 5}`}
        />)) || (props.state === ProgressState.ERROR && (
          <Cross
            fill="none"
            length={side / 2}
            strokeWidth={sw}
            d={`M ${side / 3} ${side / 3} l ${side / 3} ${side / 3} M ${side / 3} ${2 * side / 3} l  ${side / 3} ${-side / 3}`}
          />))
      }
    </Wrapper>
  );
}

LoadingResultsProgress.propTypes = {
  state: PropTypes.oneOf(PropTypes.number, PropTypes.string),
  size: PropTypes.number,
}

LoadingResultsProgress.defaultProps = {
  state: ProgressState.RUNNING,
  size: 82,
}

export default LoadingResultsProgress
