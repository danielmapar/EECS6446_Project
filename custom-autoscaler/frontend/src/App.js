
import './App.css';

import React, { useState, useEffect } from 'react';
import { useForm, Controller } from 'react-hook-form';
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-python";
import "ace-builds/src-noconflict/theme-github";
import "ace-builds/src-noconflict/ext-language_tools"
import axios from 'axios';

import DeploymentsList from './DeploymentsList';

import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import Grid from '@material-ui/core/Grid';
import TextField from '@material-ui/core/TextField';
import AddIcon from '@material-ui/icons/Add';
import SaveIcon from '@material-ui/icons/Save';
import CircularProgress from '@material-ui/core/CircularProgress';

const API_URL = process.env.REACT_APP_API_URL;

const useStyles = makeStyles((theme) => ({
  button: {
    margin: theme.spacing(1),
  },
  top: {
    color: '#1a90ff',
    animationDuration: '550ms',
  },
  circle: {
    strokeLinecap: 'round',
  },
  editorContainer: {
    width: "632px"
  }
}));

function App(props) {
  
  const [deployments, setDeployments] = useState([]);
  const [equation, setEquation] = useState("");
  const [loadTestRunning, setLoadTestRunning] = useState(false);

  useEffect(() => {
    async function fetchDeploymentsData() {
      const deploymentsResult = await axios(
        `${API_URL}/deployments`,
      );
      const data = deploymentsResult.data.result

      if (data === null) setDeployments([])
      else setDeployments([...data.list])
    }

    async function fetchEquationData() {
      const deploymentsResult = await axios(
        `${API_URL}/equation`,
      );
      const data = deploymentsResult.data.result

      const defaultCode = `
# Do not change stout (do not call print)
def scale(last_prediction, current_deployment_cpu_avg, current_num_of_replicas):
  desired_num_of_replicas = 1
  if last_prediction == None:
      last_prediction = 10

  current_prediction = current_deployment_cpu_avg * last_prediction * 2
  
  if current_prediction > 15:
    desired_num_of_replicas = 2
  else:
    desired_num_of_replicas = 1

  return [desired_num_of_replicas, current_prediction]
`;

      if (data === null) setEquation(defaultCode)
      else if (data.equation.length === 0) setEquation(defaultCode)
      else setEquation(data.equation)
    }

    fetchDeploymentsData();
    fetchEquationData();
  }, []);

  const saveDeployments = async (deployments) => await axios.put(`${API_URL}/setDeployments`, {"list": deployments})
  const saveEquation = async (equation) => await axios.put(`${API_URL}/setEquation`, {"equation": equation})
  
  const { register, handleSubmit, control, reset} = useForm();

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
    alert("Autoscaler equation saved!")
  }

  const createLoadTest = async () => {
    setLoadTestRunning(true)
    await axios.post(`${API_URL}/createLoadTest`, {"equation": equation})
    setLoadTestRunning(false)
  }

  if (equation === null || equation === undefined) return <span/>

  if (equation.length === 0) return <span/>

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
      <b>Autoscaler equation:</b>
      <form onSubmit={handleSubmit(onSubmitEquation)}>
        <div className={classes.editorContainer}>
          <Controller
            name="equation"
            control={control}
            defaultValue={equation}
            render={({ field }) => 
            <AceEditor
              {...field}
              mode="python"
              theme="github"
              name="equation-ace"
              width={'632px'}
              wrapEnabled={true}
              tabSize={2}
              setOptions={{
                  enableBasicAutocompletion: true,
                  enableLiveAutocompletion: true,
                  enableSnippets: false,
                  showLineNumbers: true,
                  useSoftTabs: true,
              }}
            />}
          />
        </div>
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
      <br/>
      <Button 
        variant="contained" 
        color="primary" 
        onClick={() => createLoadTest()}
        disabled={loadTestRunning}
      >
        Trigger Load Test
        {loadTestRunning ? <CircularProgress
          variant="indeterminate"
          disableShrink
          className={classes.top}
          classes={{
            circle: classes.circle,
          }}
          size={40}
          thickness={4}
          {...props}
        /> : <></>}
      </Button>
    </Grid>
  );
}

export default App;
