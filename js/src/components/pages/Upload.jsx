import React, {useEffect, useState} from 'react';
import {ColumnList, Layout, Loading, MainMenu, ColumnCard, Text, ConfirmedWriteButton} from "../elements";
import {Button, Grid, TextField, IconButton, Box} from "@material-ui/core";
import {makeStyles} from "@material-ui/core/styles";
import {Autocomplete} from "@material-ui/lab";
import ClearIcon from '@material-ui/icons/Clear';


const useStyles = makeStyles(theme => ({
    input: {
        display: 'none',
    },
    center: {
        textAlign: 'center',
    },
    right: {
        textAlign: 'right',
    },
    wide: {
        width: '100%',
    },
    noPadding: {
        padding: '0px',
    },
    baseline: {
        alignItems: 'baseline',
    },
}));



function FileList(props) {

    const {files, onClick} = props;
    const classes = useStyles();

    if (files.length === 0) {
        return <></>;
    } else {
        // don't understand why this is still generating the key warning
        return files.map((file, index) => (<>
            <Grid item xs={11} className={classes.baseline} key={`a${index}`}>
                <Text key={`b${index}`}>{file.name}</Text>
            </Grid>
            <Grid item xs={1} className={classes.baseline} key={`c${index}`}>
                <IconButton onClick={() => onClick(index)} className={classes.noPadding} key={`d${index}`}>
                    <ClearIcon key={`e${index}`}/>
                </IconButton>
            </Grid>
        </>));
    }
}


function FileSelect(props) {

    const {items} = props;
    const classes = useStyles();
    const [files, setFiles] = useState([]);
    const [kit, setKit] = useState([]);

    function addFiles() {
        const input = document.getElementById('upload-input');
        let newFiles = [...files];
        const names = files.map(file => file.name);
        for (let i = 0; i < input.files.length; i++) {
            const newFile = input.files.item(i);
            if (! names.includes(newFile.name)) {
                newFiles.push(newFile);
                names.push(newFile.name);
            }
        }
        setFiles(newFiles);
    }

    function deleteFile(index) {
        let newFiles = [...files];
        newFiles.splice(index, 1);
        setFiles(newFiles);
    }

    return (<>
        <Grid item xs={12}>
            <input accept='*/*' id='upload-input' multiple type='file' onChange={addFiles} className={classes.input}/>
            <label htmlFor='upload-input'>
                <Button variant='outlined' component='span'>Select files</Button>
            </label>
        </Grid>
        <FileList files={files} onClick={deleteFile}/>
        <Grid item xs={12}>
            <Autocomplete multiple options={items.map(item => item.name)} filterSelectedOptions
                          className={classes.wide} size='small'
                          renderInput={params => (<TextField {...params} variant='outlined' label='Kit'/>)}
                          onChange={(event, value) => setKit(value)}/>
        </Grid>
        <Grid item xs={12} className={classes.right}>
            <ConfirmedWriteButton disabled={files.length === 0} label='Upload'>
                The ingest process will take some time.
            </ConfirmedWriteButton>
        </Grid>
    </>);
}


function Columns(props) {

    const {items} = props;

    if (items === null) {
        return <Loading/>;  // undefined initial data
    } else {
        return (<ColumnList>
            <ColumnCard>
                <FileSelect items={items}/>
            </ColumnCard>
        </ColumnList>);
    }
}


export default function Upload(props) {

    const {match} = props;
    const [json, setJson] = useState(null);

    useEffect(() => {
        setJson(null);
        fetch('/api/kit/items')
            .then(response => response.json())
            .then(json => setJson(json));
    }, [1]);

    return (
        <Layout navigation={<MainMenu/>} content={<Columns items={json}/>} match={match} title='Upload'/>
    );
}
