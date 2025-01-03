import { ArrowBackIcon, ExternalLinkIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Grid, GridItem, Heading, Spinner, useBreakpointValue } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import KaTeX from '../components/KaTeX';
import Pagination from '../components/Pagination';
import StepCardWithRating from '../components/StepCardWithRating';
import origin from './config';

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

    const GUIDELINES_URL = 'https://docs.google.com/document/d/e/2PACX-1vSkzqp8P8dzWEzDcvkKjbxXIw4cl7SdnwAQTteRHGBbfA_uGfIKFnajU-tcm0lwrixG0_eBrVZYCZvr/pub';

    const getIssueUrl = () => {
        const baseUrl = 'https://github.com/TheDuckAI/prm/issues/new';
        const params = new URLSearchParams({
            assignees: '',
            labels: 'formatting issue',
            projects: '',
            template: 'problem-formatting-issue.md',
            title: `Formatting Issue for ${datasetName} [Problem ${Number(problemId) + 1}]`
        });
        return `${baseUrl}?${params.toString()}`;
    };

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
            const response = await fetch(`${origin}/api/datasets/${datasetId}`, {
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
            const response = await fetch(`${origin}/api/datasets/${datasetId}/problems/${problemId}`, {
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
                `${origin}/api/datasets/${datasetId}/problems/${problemId}/annotation`,
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
                    setStepAnnotations({});
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

    const handleEditableNumberSubmit = (value) => {
        const newProblemId = Number(value) - 1;
        if (newProblemId >= 0 && newProblemId < totalProblems) {
            handleProblemSelect(newProblemId);
        } else {
            setEditableNumber(String(Number(problemId) + 1));
        }
    };

    const handleStepRating = async (stepIndex, rating) => {
        try {
            const response = await fetch(
                `${origin}/api/datasets/${datasetId}/problems/${problemId}/annotation`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-key': localStorage.getItem('apiKey')
                    },
                    body: JSON.stringify([{
                        step_index: stepIndex,
                        rating: rating
                    }])
                }
            );

            if (response.ok) {
                const data = await response.json();
                // no need to update since it is only a single step update
                // setStepAnnotations(data.annotation.step_labels);
            } else if (response.status === 403) {
                navigate('/login');
            }
        } catch (error) {
            console.error('Error updating annotation:', error);
        }
    };

    const handleStepCopy = async (stepIndex, rating) => {
        let numSteps = JSON.parse(problem.model_answer_steps).length;

        let stepRatings = [];
        for (let i = stepIndex + 1; i < numSteps; i++) {
            stepRatings.push({
                step_index: i,
                rating: rating,
            });
        }

        try {
            const response = await fetch(
                `${origin}/api/datasets/${datasetId}/problems/${problemId}/annotation`,
                {
                    method: 'PUT',
                    headers: {
                        'Content-Type': 'application/json',
                        'x-key': localStorage.getItem('apiKey')
                    },
                    body: JSON.stringify(stepRatings)
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
        }
    }

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
                <Flex justifyContent="space-between" alignItems="center" mb={2}>
                    <Button
                        onClick={handleBackToDatasetsPage}
                        leftIcon={<ArrowBackIcon />}
                        size="sm"
                    >
                        Back to Datasets
                    </Button>
                    <Flex gap={2}>
                        <Button
                            as="a"
                            href={getIssueUrl()}
                            target="_blank"
                            rel="noopener noreferrer"
                            size="sm"
                            colorScheme="red"
                        >
                            Report Formatting Issue
                        </Button>
                        <Button
                            as="a"
                            href={GUIDELINES_URL}
                            target="_blank"
                            rel="noopener noreferrer"
                            rightIcon={<ExternalLinkIcon />}
                            size="sm"
                            colorScheme="blue"
                        >
                            Annotation Guidelines
                        </Button>
                    </Flex>
                </Flex>
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
                            onStepCopy={handleStepCopy}
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
                    onEditableNumberSubmit={handleEditableNumberSubmit}
                    middleElementsCount={middleElementsCount}
                />
            </Flex>
        </Flex>
    );
};

export default ProblemsPage;