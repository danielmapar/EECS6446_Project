
import './App.css';

import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import axios from 'axios';

import DeploymentsList from './DeploymentsList';

import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import AddIcon from '@material-ui/icons/Add';
import SaveIcon from '@material-ui/icons/Save';

const API_URL = process.env.REACT_APP_API_URL;

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
  textField: {
    width: '100ch',
  }
}));

function App() {
  
  const [deployments, setDeployments] = useState([]);
  const [equation, setEquation] = useState("");

  useEffect(() => {
    async function fetchDeploymentsData() {
      const deploymentsResult = await axios(
        `${API_URL}/deployments`,
      );
      setDeployments([...deploymentsResult.data.result.list])
    }

    async function fetchEquationData() {
      const deploymentsResult = await axios(
        `${API_URL}/equation`,
      );
      setEquation(deploymentsResult.data.result.equation)
    }

    fetchDeploymentsData();
    fetchEquationData();
  }, []);

  const saveDeployments = async (deployments) => await axios.put(`${API_URL}/setDeployments`, {"list": deployments})
  const saveEquation = async (equation) => await axios.put(`${API_URL}/setEquation`, {"equation": equation})
  
  const { register, handleSubmit, reset} = useForm();

  const classes = useStyles();

  const removeDeployment = async (index) => {
    const newDeployments = [...deployments];
    newDeployments.splice(index, 1);
    setDeployments(newDeployments);
    await saveDeployments(newDeployments);
  }

  const onSubmitNewDeployment = async (data) => {
    const newDeployments = [...deployments, data.newDeployment];
    setDeployments(newDeployments);
    await saveDeployments(newDeployments);
    reset();
  };

  const onSubmitEquation = async (data) => {
    setEquation(data.equation)
    await saveEquation(data.equation);
    reset();
  }

  const createLoadTest = async () => {
    await axios.post(`${API_URL}/createLoadTest`, {"equation": equation})
  }

  return (
    <Grid
      container
      spacing={0}
      direction="column"
      alignItems="center"
      justify="center"
      style={{ minHeight: '100vh' }}
    >
      <h1>Custom Pod Autoscaler</h1>

      <DeploymentsList data={deployments} remove={removeDeployment} />
      <br/>
      <form onSubmit={handleSubmit(onSubmitNewDeployment)}>
        <TextField 
          {...register('newDeployment')}
          name="newDeployment"
          label="Deployment Name" 
          variant="outlined" 
        />
        <Button
          variant="contained"
          color="primary"
          className={classes.button}
          type="submit"
          endIcon={<AddIcon />}
        >
          Add
        </Button>
      </form>
      <br />
      <hr />
      <form onSubmit={handleSubmit(onSubmitEquation)}>
        <TextField 
          className={classes.textField}
          {...register('equation')}
          name="equation"
          label="Autoscaler Equation" 
          variant="outlined" 
        />
        <br />
        <Button
          variant="contained"
          color="primary"
          className={classes.button}
          type="submit"
          endIcon={<SaveIcon />}
        >
          Save
        </Button>
      </form>
      <div>Active autoscaler equation:</div>
       <br/> 
      <div>
        <b style={{textAlign: "center"}}>{equation}</b>
      </div>
      <br/>
      <Button variant="contained" color="primary" onClick={() => createLoadTest()}>
        Trigger Load Test
      </Button>
    </Grid>
  );
}

export default App;
