import { Box, Heading, SimpleGrid, Spinner } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DatasetCard from '../components/DatasetCard';
import LoginPage from './LoginPage';

const DatasetsPage = () => {
    const [datasets, setDatasets] = useState([]);
    const [apiKey, setApiKey] = useState(localStorage.getItem('apiKey') || '');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        if (apiKey) {
            setLoading(true);
            fetch('http://127.0.0.1:8000/datasets', {
                method: 'GET',
                headers: {
                    'x-key': apiKey
                }
            })
                .then(response => response.json())
                .then(data => {
                    setDatasets(data);
                    setLoading(false);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    setLoading(false);
                });
        }
    }, [apiKey]);

    const handleLogin = (key) => {
        setApiKey(key);
        localStorage.setItem('apiKey', key);
    };

    const handleDatasetClick = (dataset) => {
        navigate(`/datasets/${dataset.id}/problems`);
    };

    if (!apiKey) {
        return <LoginPage onLogin={handleLogin} />;
    }

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
                <Spinner size="xl" />
            </Box>
        );
    }

    return (
        <Box p={6}>
            <Heading as="h1" size="xl" mb={6}>
                Dataset List
            </Heading>
            <SimpleGrid columns={[1, 2, 3]} spacing={8}>
                {datasets.map((dataset) => (
                    <DatasetCard
                        key={dataset.id}
                        dataset={dataset}
                        onClick={() => handleDatasetClick(dataset)}
                    />
                ))}
            </SimpleGrid>
        </Box>
    );
};

export default DatasetsPage;