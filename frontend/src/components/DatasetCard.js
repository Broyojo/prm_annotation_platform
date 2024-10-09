import { Badge, Box, Heading, HStack, Text, VStack } from '@chakra-ui/react';
import React from 'react';

const DatasetCard = ({ dataset, onClick }) => {
    return (
        <Box
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            p={5}
            shadow="md"
            transition="transform 0.2s"
            _hover={{ transform: 'scale(1.05)', cursor: 'pointer' }}
            onClick={() => onClick(dataset)}
        >
            <VStack align="start" spacing={3}>
                <Heading as="h2" size="md">
                    {dataset.name}
                </Heading>
                <Text fontSize="sm" color="gray.600">Domain: {dataset.domain}</Text>
                <HStack spacing={4}>
                    <Badge colorScheme="blue">
                        {dataset.total_problems} Problems
                    </Badge>
                    <Badge colorScheme="green">
                        {dataset.annotated_problems} Annotated
                    </Badge>
                </HStack>
                <Text fontSize="sm" color="gray.500">
                    {((dataset.annotated_problems / dataset.total_problems) * 100).toFixed(1)}% Annotated
                </Text>
            </VStack>
        </Box>
    );
};

export default DatasetCard;