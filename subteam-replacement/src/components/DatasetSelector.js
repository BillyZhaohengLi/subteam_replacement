import PropTypes from 'prop-types'
import Datasets from './Datasets'

const DatasetSelector = ({ datasets, onLoad, selectedDataset }) => {

    return (
        <div>
            <h2>Select a dataset: {selectedDataset.name}</h2>
            <h3><span>&nbsp;&nbsp;</span>{selectedDataset.nodes}{selectedDataset.edges}{selectedDataset.attributes}<span>&nbsp;&nbsp;</span></h3>
            <div className = 'container'>
                <Datasets datasets={datasets} onLoad={onLoad} selectedDataset={selectedDataset}/>
            </div>
        </div>
    )
}

export default DatasetSelector
