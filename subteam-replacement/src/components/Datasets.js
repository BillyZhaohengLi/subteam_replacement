import Dataset from './Dataset'

const Datasets = ({ datasets, onLoad, selectedDataset }) => {

    return (
        <>
            {datasets.map((dataset) => (<Dataset key = {dataset.id} dataset = {dataset} onLoad = {onLoad} selectedDataset = {selectedDataset} />))}
        </>
    )
}

export default Datasets
