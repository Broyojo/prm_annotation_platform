import { Box, Button, Heading, SimpleGrid, Spinner } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DatasetCard from '../components/DatasetCard';

const DatasetsPage = () => {
    const [datasets, setDatasets] = useState([]);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchDatasets();
    }, []);

    const fetchDatasets = async () => {
        setLoading(true);
        try {
            const response = await fetch('http://127.0.0.1:8000/datasets', {
                method: 'GET',
                headers: {
                    'x-key': localStorage.getItem('apiKey')
                }
            });
            if (response.ok) {
                const data = await response.json();
                setDatasets(data);
            } else if (response.status === 403) {
                // If the API key is invalid, redirect to login
                navigate('/login');
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
        setLoading(false);
    };

    const handleDatasetClick = (dataset) => {
        navigate(`/datasets/${dataset.id}/problems`);
    };

    const handleLogout = () => {
        localStorage.removeItem('apiKey');
        navigate('/login');
    };

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
            <Button onClick={handleLogout} mt={4}>Logout</Button>
        </Box>
    );
};

export default DatasetsPage;