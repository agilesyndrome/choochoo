import React from "react";
import {makeStyles} from "@material-ui/core/styles";


const useStyles = makeStyles(theme => ({
    svg: {
        overflow: 'visible',
        marginRight: theme.spacing(1),
    },
    barBackground: {
        fill: theme.palette.background.default,
        stroke: theme.palette.text.secondary,
    },
    barForeground: {
        fill: theme.palette.text.secondary,
        fillOpacity: 0.2,
        stroke: 'none',
    },
    barLine: {
        stroke: theme.palette.text.secondary,
        strokeWidth: 0.75,
    },
    barText: {
        fontSize: 11,
        fill: theme.palette.text.secondary,
    }
}));



export default function PercentBar(props) {

    const {percent, label, width=50, height=19} = props;
    const classes = useStyles();
    const x = width * percent / 100;
    const text = label ? label : percent.toFixed(0) + ' %';

    return (<svg width={width + 1} height={0} className={classes.svg}>
        <g transform='translate(0.5, -15.5)'>
            <rect width={width} height={height} className={classes.barBackground}/>
            <rect width={x} height={height} className={classes.barForeground}/>
            <text x={3} y={height - 6} className={classes.barText}>{text}</text>
            {/* <line x1={x} x2={x} y1={0} y2={height} className={classes.barLine}/> */}
        </g>
    </svg>);
}
