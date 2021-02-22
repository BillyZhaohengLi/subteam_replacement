import logo from './logo.svg';
import './App.css';
import DatasetSelector from './components/DatasetSelector'
import Button from './components/Button'
import Datasets from './components/Datasets'
import { useState } from 'react'

function App() {
  const [datasets] = useState([{id: 1, name: 'DBLP', nodes: 100, edges: 200, attributes: 10}, 
  {id: 2, name: 'IMDB', nodes: 1000, edges: 2000, attributes: 100}, 
  {id: 3, name: 'BA', nodes: -1, edges: -1, attributes: 10}, 
  {id: 4, name: 'Linkedin', nodes: -1, edges: -1, attributes: 10}, 
  {id: 5, name: 'Facebook', nodes: -1, edges: -1, attributes: 10}, 
  {id: 6, name: 'Twitter', nodes: -1, edges: -1, attributes: 10}, 
  {id: 7, name: 'Steam', nodes: -1, edges: -1, attributes: 10}, ])
  const [selectedDataset, setSelectedDataset] = useState({name: '*none selected*', nodes: ' ', edges: '', attributes: ''})
  const onClick = () => {
    console.log('click')
  }

  const loadDataset = (id, selectedDataset) => {
    console.log(selectedDataset.name)
    datasets.map((dataset) => {if (dataset.id === id) setSelectedDataset({...selectedDataset, name:dataset.name, 
    nodes:('Nodes(n): ' + dataset.nodes), 
    edges:(' Edges(m): ' + dataset.edges), 
    attributes:(' Attributes(l): ' + dataset.attributes)})})
  }

  return (
    <div className="App">
      <h1>Subteam Replacement</h1>
      <h2>Problem Definition & Fast Solution Demo</h2>
      {datasets.length > 0 ? (<DatasetSelector datasets={datasets} onLoad = {loadDataset} selectedDataset={selectedDataset}/>) : ('No datasets in repository')}
      <Button color = 'black' text = 'About this project' className = 'btn' onClick = {onClick}/>
      <Button color = 'black' text = 'Continue' className = 'btn' onClick = {onClick}/>
    </div>
  );
}

export default App;
