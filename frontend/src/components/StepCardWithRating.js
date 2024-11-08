import { CheckIcon, CloseIcon, InfoIcon, WarningIcon } from '@chakra-ui/icons';
import { Box, Button, ButtonGroup, Spinner, Text, useColorModeValue } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';
import KaTeX from './KaTeX';

const StepCardWithRating = ({ step, index, savedRating, onRateStep }) => {
    const [rating, setRating] = useState(savedRating || null);
    const [isSubmitting, setIsSubmitting] = useState(false);

    useEffect(() => {
        setRating(savedRating || null);
    }, [savedRating]);

    const handleRateStep = async (newRating) => {
        if (isSubmitting) return;

        setIsSubmitting(true);
        try {
            await onRateStep(index, newRating);
            setRating(newRating);
        } catch (error) {
            console.error('Error rating step:', error);
        } finally {
            setIsSubmitting(false);
        }
    };

    const bgColor = useColorModeValue('white', 'gray.700');
    const borderColor = useColorModeValue('gray.200', 'gray.600');
    const textColor = useColorModeValue('gray.800', 'white');
    const stepBgColor = useColorModeValue('blue.50', 'blue.900');

    const getRatingButton = (ratingValue, icon, colorScheme) => (
        <Button
            onClick={() => handleRateStep(ratingValue)}
            leftIcon={icon}
            colorScheme={colorScheme}
            size="sm"
            variant={rating === ratingValue ? "solid" : "outline"}
            fontWeight="medium"
            isDisabled={isSubmitting}
        >
            {ratingValue}
        </Button>
    );

    return (
        <Box
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            p={4}
            mb={4}
            bg={bgColor}
            borderColor={borderColor}
            boxShadow="sm"
        >
            <Box
                bg={stepBgColor}
                px={3}
                py={1}
                borderRadius="md"
                fontWeight="bold"
                color={useColorModeValue('blue.700', 'blue.200')}
                display="inline-block"
                mb={2}
            >
                Step {index + 1}
            </Box>
            <Text fontSize="md" mb={4} color={textColor}><KaTeX>{step}</KaTeX></Text>
            <ButtonGroup size="sm" isAttached variant="outline">
                {getRatingButton("Good", <CheckIcon />, "green")}
                {getRatingButton("Neutral", <InfoIcon />, "blue")}
                {getRatingButton("Bad", <CloseIcon />, "red")}
                {getRatingButton("Error", <WarningIcon />, "yellow")}
            </ButtonGroup>
            {isSubmitting && <Spinner size="sm" ml={2} />}
        </Box>
    );
};

export default StepCardWithRating;