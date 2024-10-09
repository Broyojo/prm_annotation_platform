import { Box, Heading, Text } from '@chakra-ui/react';
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
            <Heading as="h2" size="md" mb={4}>
                {dataset.name}
            </Heading>
            <Text>Domain: {dataset.domain}</Text>
        </Box>
    );
};

export default DatasetCard;