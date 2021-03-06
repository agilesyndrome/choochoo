import React from 'react';
import {Button} from "@material-ui/core";
import {makeStyles} from "@material-ui/styles";


const useStyles = makeStyles(theme => ({
    button: {
        width: '100%',
    },
}));


export default function LinkButton(props) {
    const {href, children, disabled=false, variant='outlined'} = props;
    const classes = useStyles();
    function onClick() {
        window.open(href, '_blank')
    }
    return (<Button variant={variant} onClick={onClick} disabled={disabled} className={classes.button}>
        {children}
    </Button>);
}
