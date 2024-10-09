import { ArrowBackIcon } from '@chakra-ui/icons';
import { Box, Button, Flex, Grid, GridItem, Heading, Spinner } from '@chakra-ui/react';
import MarkdownIt from 'markdown-it';
import mk from 'markdown-it-katex';
import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import StepCardWithRating from '../components/StepCardWithRating';

const md = new MarkdownIt();
md.use(mk);

const ProblemsPage = () => {
    const { datasetId } = useParams();
    const [problem, setProblem] = useState(null);
    const [currentProblemIndex, setCurrentProblemIndex] = useState(0);
    const [totalProblems, setTotalProblems] = useState(0);
    const [loading, setLoading] = useState(false);
    const [datasetName, setDatasetName] = useState('');
    const navigate = useNavigate();

    useEffect(() => {
        fetchDatasetInfo();
        fetchProblem();
    }, [datasetId, currentProblemIndex]);

    const fetchDatasetInfo = async () => {
        try {
            const response = await fetch(`http://127.0.0.1:8000/datasets/${datasetId}`, {
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

    const handleBackToDatasetsPage = () => {
        navigate('/');
    };

    const renderMarkdown = (content) => {
        return { __html: md.render(content) };
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
        <Box p={6}>
            <Button
                onClick={handleBackToDatasetsPage}
                mb={4}
                leftIcon={<ArrowBackIcon />}
            >
                Back to Datasets
            </Button>
            <Heading as="h1" size="xl" mb={6}>
                {datasetName} - Problem {currentProblemIndex + 1} of {totalProblems}
            </Heading>
            <Grid templateColumns="repeat(2, 1fr)" gap={6} height="calc(100vh - 100px)">
                <GridItem overflowY="auto">
                    <Box mb={6}>
                        <Heading as="h2" size="lg" mb={2}>Question:</Heading>
                        <Box dangerouslySetInnerHTML={renderMarkdown(problem.question)} fontSize="inherit" lineHeight="inherit" />
                    </Box>
                    <Box mb={6}>
                        <Heading as="h2" size="lg" mb={2}>Answer:</Heading>
                        <Box dangerouslySetInnerHTML={renderMarkdown(problem.answer)} />
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
                        <StepCardWithRating key={index} step={step} index={index} />
                    ))}
                </GridItem>
            </Grid>
        </Box>
    );
};

export default ProblemsPage;
