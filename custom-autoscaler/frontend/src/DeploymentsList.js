import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import List from '@material-ui/core/List';
import ListItem from '@material-ui/core/ListItem';
import ListItemSecondaryAction from '@material-ui/core/ListItemSecondaryAction';
import ListItemText from '@material-ui/core/ListItemText';
import IconButton from '@material-ui/core/IconButton';
import DeleteForeverIcon from '@material-ui/icons/DeleteForever';
import ListSubheader from '@material-ui/core/ListSubheader';
import Divider from '@material-ui/core/Divider';
import Alert from '@material-ui/lab/Alert';

const useStyles = makeStyles((theme) => ({
  root: {
    width: '100%',
    maxWidth: 300,
    backgroundColor: theme.palette.background.paper,
  },
  nested: {
    paddingLeft: theme.spacing(4),
  },
}));

export default function DeploymentsList(props) {

  const classes = useStyles();
  const deployments = props.data;

  if (deployments.length === 0) return <Alert severity="warning">No deployments - Please add at least one!</Alert>

  return (
    <List subheader={<ListSubheader>Monitored Deployments</ListSubheader>} className={classes.root}>
      {deployments.map((value, index) => {

        return (
          <span key={`list-item-${index}`}>
            <ListItem role={undefined} dense button >
              <ListItemText primary={value} />
              <ListItemSecondaryAction>
                <IconButton edge="end" aria-label="comments" onClick={() => props.remove(index)}>
                  <DeleteForeverIcon />
                </IconButton>
              </ListItemSecondaryAction>
            </ListItem>
            <Divider key={`divider-${index}`}/>
          </span>
        );
      })}
    </List>
  );
}