import { ArrowBackIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Grid, GridItem, Heading, Spinner, useBreakpointValue } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import KaTeX from '../components/KaTeX';
import Pagination from '../components/Pagination';
import StepCardWithRating from '../components/StepCardWithRating';

const ProblemsPage = () => {
    const { datasetId, problemId } = useParams();
    const [problem, setProblem] = useState(null);
    const [totalProblems, setTotalProblems] = useState(0);
    const [loading, setLoading] = useState(false);
    const [datasetName, setDatasetName] = useState('');
    const [editableNumber, setEditableNumber] = useState('');
    const [stepAnnotations, setStepAnnotations] = useState({});
    const navigate = useNavigate();

    const middleElementsCount = useBreakpointValue({ base: 3, md: 5, lg: 7 });

    useEffect(() => {
        fetchDatasetInfo();
        fetchProblem();
        fetchAnnotation();
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

    const fetchAnnotation = async () => {
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/api/datasets/${datasetId}/problems/${problemId}/annotation`,
                {
                    headers: {
                        'x-key': localStorage.getItem('apiKey')
                    }
                }
            );
            if (response.ok) {
                const data = await response.json();
                if (data.annotation) {
                    setStepAnnotations(data.annotation.step_labels);
                } else {
                    setStepAnnotations({}); // Reset if no annotation exists
                }
            } else if (response.status === 403) {
                navigate('/login');
            }
        } catch (error) {
            console.error('Error fetching annotation:', error);
        }
    };


    const handleProblemSelect = (selectedProblemId) => {
        navigate(`/datasets/${datasetId}/problems/${selectedProblemId}`);
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

    const handleStepRating = async (stepIndex, rating) => {
        try {
            const response = await fetch(
                `http://127.0.0.1:8000/api/datasets/${datasetId}/problems/${problemId}/annotation`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-key': localStorage.getItem('apiKey')
                    },
                    body: JSON.stringify({
                        step_index: stepIndex,
                        rating: rating
                    })
                }
            );

            if (response.ok) {
                const data = await response.json();
                setStepAnnotations(data.annotation.step_labels);
            } else if (response.status === 403) {
                navigate('/login');
            }
        } catch (error) {
            console.error('Error updating annotation:', error);
            // You might want to add some error handling UI here
        }
    };

    if (loading) {
        return (
            <Flex justifyContent="center" alignItems="center" height="100vh">
                <Spinner size="xl" />
            </Flex>
        );
    }

    if (!problem) {
        return null; // TODO: send to some 404 page or send to last problem?
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
                    {JSON.parse(problem.model_answer_steps).map((step, index) => (
                        <StepCardWithRating
                            key={index}
                            step={step}
                            index={index}
                            savedRating={stepAnnotations[index]}
                            onRateStep={handleStepRating}
                        />
                    ))}
                </GridItem>
            </Grid>
            <Flex justifyContent="center" alignItems="center" p={4} borderTop="1px" borderColor="gray.200">
                <Pagination
                    currentPage={Number(problemId)}
                    totalPages={totalProblems}
                    onPageChange={handleProblemSelect}
                    editableNumber={editableNumber}
                    onEditableNumberChange={handleEditableNumberChange}
                    onEditableNumberSubmit={handleEditableNumberSubmit}
                    middleElementsCount={middleElementsCount}
                />
            </Flex>
        </Flex>
    );
};

export default ProblemsPage;