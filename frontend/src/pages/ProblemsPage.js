import { ArrowBackIcon, ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Grid, GridItem, Heading, HStack, Input, Spinner, Text } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import KaTeX from '../components/KaTeX';
import StepCardWithRating from '../components/StepCardWithRating';

const ProblemsPage = () => {
    const { datasetId, problemId } = useParams();
    const [problem, setProblem] = useState(null);
    const [totalProblems, setTotalProblems] = useState(0);
    const [loading, setLoading] = useState(false);
    const [datasetName, setDatasetName] = useState('');
    const [editableNumber, setEditableNumber] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchDatasetInfo();
        fetchProblem();
    }, [datasetId, problemId]);

    useEffect(() => {
        setEditableNumber(String(Number(problemId) + 1));
    }, [problemId]);

    const fetchDatasetInfo = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/datasets/${datasetId}`, {
                headers: {
                    'x-key': localStorage.getItem('apiKey')
                }
            });
            if (response.ok) {
                const data = await response.json();
                setDatasetName(data.name);
            } else if (response.status === 403) {
                navigate('/login');
            }
        } catch (error) {
            console.error('Error fetching dataset info:', error);
        }
    };

    const fetchProblem = async () => {
        setLoading(true);
        try {
            const response = await fetch(`http://127.0.0.1:8000/api/datasets/${datasetId}/problems/${problemId}`, {
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

    const handleProblemSelect = (selectedProblemId) => {
        navigate(`/datasets/${datasetId}/problems/${selectedProblemId}`);
    };

    const handleNextProblem = () => {
        if (Number(problemId) < totalProblems - 1) {
            handleProblemSelect(Number(problemId) + 1);
        }
    };

    const handlePreviousProblem = () => {
        if (Number(problemId) > 0) {
            handleProblemSelect(Number(problemId) - 1);
        }
    };

    const handleBackToDatasetsPage = () => {
        navigate('/');
    };

    const handleEditableNumberChange = (e) => {
        setEditableNumber(e.target.value);
    };

    const handleEditableNumberSubmit = (e) => {
        e.preventDefault();
        const newProblemId = Number(editableNumber) - 1;
        if (newProblemId >= 0 && newProblemId < totalProblems) {
            handleProblemSelect(newProblemId);
        } else {
            setEditableNumber(String(Number(problemId) + 1));
        }
    };

    const renderProblemSelectionMenu = () => {
        const currentProblem = Number(problemId);
        const items = [];

        const addButton = (index) => {
            if (index === currentProblem) {
                items.push(
                    <form key={index} onSubmit={handleEditableNumberSubmit}>
                        <Input
                            size="sm"
                            width="60px"
                            textAlign="center"
                            value={editableNumber}
                            onChange={handleEditableNumberChange}
                            onBlur={handleEditableNumberSubmit}
                        />
                    </form>
                );
            } else {
                items.push(
                    <Button
                        key={index}
                        size="sm"
                        variant="ghost"
                        onClick={() => handleProblemSelect(index)}
                    >
                        {index + 1}
                    </Button>
                );
            }
        };

        const addEllipsis = (key) => {
            items.push(<Text key={key}>...</Text>);
        };

        // Always add the first problem
        addButton(0);

        if (currentProblem > 3) addEllipsis('start');

        // Add 5 problems in the middle
        const start = Math.max(1, Math.min(currentProblem - 2, totalProblems - 6));
        const end = Math.min(start + 4, totalProblems - 2);

        for (let i = start; i <= end; i++) {
            addButton(i);
        }

        if (currentProblem < totalProblems - 4) addEllipsis('end');

        // Always add the last problem
        if (totalProblems > 1) addButton(totalProblems - 1);

        return items;
    };

    if (loading) {
        return (
            <Flex justifyContent="center" alignItems="center" height="100vh">
                <Spinner size="xl" />
            </Flex>
        );
    }

    if (!problem) {
        return null;
    }

    return (
        <Flex flexDirection="column" height="100vh" overflow="hidden">
            <Box p={4} borderBottom="1px" borderColor="gray.200">
                <Button
                    onClick={handleBackToDatasetsPage}
                    mb={2}
                    leftIcon={<ArrowBackIcon />}
                    size="sm"
                >
                    Back to Datasets
                </Button>
                <Heading as="h1" size="lg">
                    {datasetName} - Problem {Number(problemId) + 1}
                </Heading>
            </Box>
            <Grid templateColumns="repeat(2, 1fr)" gap={4} flex="1" minHeight={0}>
                <GridItem overflowY="auto" p={4} borderRight="1px" borderColor="gray.200">
                    <Box mb={4}>
                        <Heading as="h2" size="md" mb={2}>Question:</Heading>
                        <KaTeX>{problem.question}</KaTeX>
                    </Box>
                    <Box>
                        <Heading as="h2" size="md" mb={2}>Answer:</Heading>
                        <KaTeX>{problem.answer}</KaTeX>
                    </Box>
                </GridItem>
                <GridItem overflowY="auto" p={4}>
                    <Heading as="h2" size="md" mb={4}>Model Answer Steps:</Heading>
                    {JSON.parse(problem.steps).map((step, index) => (
                        <StepCardWithRating key={index} step={step} index={index} />
                    ))}
                </GridItem>
            </Grid>
            <Flex justifyContent="center" alignItems="center" p={4} borderTop="1px" borderColor="gray.200">
                <HStack spacing={1}>
                    <Button
                        size="sm"
                        onClick={handlePreviousProblem}
                        isDisabled={Number(problemId) === 0}
                    >
                        <ChevronLeftIcon /> Previous Problem
                    </Button>
                    {renderProblemSelectionMenu()}
                    <Button
                        size="sm"
                        onClick={handleNextProblem}
                        isDisabled={Number(problemId) === totalProblems - 1}
                    >
                        Next Problem <ChevronRightIcon />
                    </Button>
                </HStack>
            </Flex>
        </Flex>
    );
};

export default ProblemsPage;