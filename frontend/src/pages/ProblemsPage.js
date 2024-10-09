import { Box, Button, Flex, Heading, Spinner, Table, Tbody, Td, Th, Thead, Tr } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';

const ProblemsPage = () => {
    const { datasetId } = useParams();
    const [problems, setProblems] = useState([]);
    const [page, setPage] = useState(1);
    const [totalPages, setTotalPages] = useState(0);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchProblems();
    }, [datasetId, page]);

    const fetchProblems = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}/problems_paginated?page=${page}&page_size=10`, {
                headers: {
                    'x-key': localStorage.getItem('apiKey')
                }
            });
            if (response.ok) {
                const data = await response.json();
                setProblems(data.problems);
                setTotalPages(Math.ceil(data.total / data.page_size));
            } else if (response.status === 403) {
                // If the API key is invalid, redirect to login
                navigate('/login');
            }
        } catch (error) {
            console.error('Error fetching problems:', error);
        }
        setLoading(false);
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
                Problems for Dataset {datasetId}
            </Heading>
            <Table variant="simple">
                <Thead>
                    <Tr>
                        <Th>Question</Th>
                        <Th>Number of Steps</Th>
                        <Th>Is Correct</Th>
                        <Th>Solve Ratio</Th>
                    </Tr>
                </Thead>
                <Tbody>
                    {problems.map((problem) => (
                        <Tr key={problem.id}>
                            <Td>{problem.question}</Td>
                            <Td>{problem.num_steps}</Td>
                            <Td>{problem.is_correct ? 'Yes' : 'No'}</Td>
                            <Td>{problem.solve_ratio?.toFixed(2) || 'N/A'}</Td>
                        </Tr>
                    ))}
                </Tbody>
            </Table>
            <Flex justifyContent="space-between" mt={4}>
                <Button onClick={() => setPage(p => Math.max(1, p - 1))} disabled={page === 1}>
                    Previous
                </Button>
                <Button onClick={() => setPage(p => p + 1)} disabled={page === totalPages}>
                    Next
                </Button>
            </Flex>
        </Box>
    );
};

export default ProblemsPage;