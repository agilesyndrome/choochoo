import React from 'react';
import {TreeView, TreeItem} from '@material-ui/lab';
import {Typography} from "@material-ui/core";
import EditField from "./EditField";


export default function fmtDay(writer, json) {
    const ids = addIds(json);
    console.log(json);
    return (<TreeView defaultExpanded={ids}>{fmtJson(writer)(json)}</TreeView>);
}


function fmtJson(writer) {

    function fmtList(json) {
        if (! Array.isArray(json)) throw 'Expected array';
        const head = json[0], rest = json.slice(1);
        let dom = [], label = [], id = '';
        rest.forEach((row) => {
            if (Array.isArray(row)) {
                if (label.length) {
                    dom.push(<TreeItem key={id} nodeId={id} label={label}/>);
                    label = [];
                }
                dom.push(fmtList(row));
            } else {
                if (! label.length) id = row.id + ',outer';
                label.push(fmtField(writer, row));
            }
        });
        if (label.length) dom.push(<TreeItem key={id} nodeId={id} label={label}/>);
        return <TreeItem key={json.id} nodeId={json.id} label={head.value}>{dom}</TreeItem>;
    }

    return fmtList;
}


function fmtField(writer, json) {
    if (json.type === 'edit') {
        return <EditField key={json.id} writer={writer} json={json}/>
    } else {
        return <Typography key={json.id}>{json.label}={json.value}</Typography>;
    }
}


function addIds(json) {

    /* react docs say keys only need to be unique amongst siblings.
       if that's literally true then this is overkill. */

    function add(base) {
        return (json, index) => {
            const id = (base === undefined) ? `${index}` : `${base},${index}`;
            json.id = id;
            if (Array.isArray(json)) json.map(add(id));
        }
    }

    add()(json, 0);

    let ids = [];

    function list(json) {
        ids.push(json.id);
        if (Array.isArray(json)) json.map(list);
    }

    list(json);

    return ids
}
