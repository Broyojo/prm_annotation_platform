import { DownloadIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Heading, SimpleGrid, Spinner, useToast } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import DatasetCard from '../components/DatasetCard';
import LoginPage from './LoginPage';
import origin from './config';

const DatasetsPage = () => {
    const [datasets, setDatasets] = useState([]);
    const [apiKey, setApiKey] = useState(localStorage.getItem('apiKey') || '');
    const [loading, setLoading] = useState(false);
    const [exporting, setExporting] = useState(false);
    const navigate = useNavigate();
    const toast = useToast();

    useEffect(() => {
        if (apiKey) {
            fetchDatasets();
        }
    }, [apiKey]);

    const fetchDatasets = async () => {
        setLoading(true);
        try {
            const response = await fetch(`${origin}/api/datasets`, {
                method: 'GET',
                headers: {
                    'x-key': apiKey
                }
            });
            if (response.ok) {
                const data = await response.json();
                setDatasets(data);
            } else {
                handleLogout();
            }
        } catch (error) {
            console.error('Error fetching data:', error);
            toast({
                title: 'Error',
                description: 'Failed to fetch datasets',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        }
        setLoading(false);
    };

    const handleExport = async () => {
        setExporting(true);
        try {
            const response = await fetch(`${origin}/api/export`, {
                method: 'GET',
                headers: {
                    'x-key': apiKey
                }
            });

            if (!response.ok) {
                throw new Error(`Export failed: ${response.statusText}`);
            }

            // Get the filename from the Content-Disposition header
            const contentDisposition = response.headers.get('Content-Disposition');
            let filename = 'database_export.json';
            if (contentDisposition) {
                const matches = /filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/.exec(contentDisposition);
                if (matches != null && matches[1]) {
                    filename = matches[1].replace(/['"]/g, '');
                }
            }

            // Create blob and download
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.setAttribute('download', filename);
            document.body.appendChild(link);
            link.click();
            link.parentNode.removeChild(link);
            window.URL.revokeObjectURL(url);

            toast({
                title: 'Success',
                description: 'Database exported successfully',
                status: 'success',
                duration: 3000,
                isClosable: true,
            });
        } catch (error) {
            console.error('Export error:', error);
            toast({
                title: 'Export Failed',
                description: error.message || 'Failed to export database',
                status: 'error',
                duration: 5000,
                isClosable: true,
            });
        } finally {
            setExporting(false);
        }
    };

    const handleLogin = (key) => {
        setApiKey(key);
        localStorage.setItem('apiKey', key);
    };

    const handleLogout = () => {
        setApiKey('');
        localStorage.removeItem('apiKey');
        setDatasets([]);
    };

    const handleDatasetClick = (dataset) => {
        navigate(`/datasets/${dataset.id}/problems/0`);
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
            <Flex justifyContent="space-between" alignItems="center" mb={6}>
                <Heading as="h1" size="xl">
                    Dataset List
                </Heading>
                <Flex gap={4}>
                    <Button
                        leftIcon={<DownloadIcon />}
                        colorScheme="blue"
                        onClick={handleExport}
                        isLoading={exporting}
                        loadingText="Exporting..."
                    >
                        Export Database
                    </Button>
                    <Button onClick={handleLogout} colorScheme="red">
                        Logout
                    </Button>
                </Flex>
            </Flex>
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