import Button from './Button'

const Dataset = ({ dataset, onLoad, selectedDataset }) => {
    return (
        <div className = 'dataset'>
            <h3>{dataset.name} <Button color='grey' text='Load' onClick={() => onLoad(dataset.id, selectedDataset)}/></h3>
        </div>
    )
}

export default Dataset
