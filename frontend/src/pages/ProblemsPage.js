import { Box, Button, Flex, Grid, GridItem, Heading, Spinner, Text } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import StepCard from '../components/StepCard';

const ProblemsPage = () => {
    const { datasetId } = useParams();
    const [problem, setProblem] = useState(null);
    const [currentProblemIndex, setCurrentProblemIndex] = useState(0);
    const [totalProblems, setTotalProblems] = useState(0);
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    useEffect(() => {
        fetchProblem();
    }, [datasetId, currentProblemIndex]);

    const fetchProblem = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}/problems/${currentProblemIndex}`, {
                headers: {
                    'x-key': localStorage.getItem('apiKey')
                }
            });
            if (response.ok) {
                const data = await response.json();
                setProblem(data.problem);
                setTotalProblems(data.total_problems);
            } else if (response.status === 403) {
                navigate('/login');
            }
        } catch (error) {
            console.error('Error fetching problem:', error);
        }
        setLoading(false);
    };

    const handleNextProblem = () => {
        setCurrentProblemIndex(prev => Math.min(prev + 1, totalProblems - 1));
    };

    const handlePreviousProblem = () => {
        setCurrentProblemIndex(prev => Math.max(prev - 1, 0));
    };

    if (loading) {
        return (
            <Box display="flex" justifyContent="center" alignItems="center" height="100vh">
                <Spinner size="xl" />
            </Box>
        );
    }

    if (!problem) {
        return null;
    }

    return (
        <Grid templateColumns="repeat(2, 1fr)" gap={6} p={6} height="100vh">
            <GridItem overflowY="auto">
                <Heading as="h1" size="xl" mb={6}>
                    Problem {currentProblemIndex + 1} of {totalProblems}
                </Heading>
                <Box mb={6}>
                    <Heading as="h2" size="lg" mb={2}>Question:</Heading>
                    <Text>{problem.question}</Text>
                </Box>
                <Box mb={6}>
                    <Heading as="h2" size="lg" mb={2}>Answer:</Heading>
                    <Text>{problem.answer}</Text>
                </Box>
                <Flex justifyContent="space-between" mt={4}>
                    <Button onClick={handlePreviousProblem} disabled={currentProblemIndex === 0}>
                        Previous Problem
                    </Button>
                    <Button onClick={handleNextProblem} disabled={currentProblemIndex === totalProblems - 1}>
                        Next Problem
                    </Button>
                </Flex>
            </GridItem>
            <GridItem overflowY="auto">
                <Heading as="h2" size="lg" mb={4}>Model Answer Steps:</Heading>
                {JSON.parse(problem.steps).map((step, index) => (
                    <StepCard key={index} step={step} index={index} />
                ))}
            </GridItem>
        </Grid>
    );
};

export default ProblemsPage;