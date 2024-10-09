import { Box, Heading, SimpleGrid, Text } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

function App() {
  const [datasets, setDatasets] = useState([]);

  useEffect(() => {
    // Fetch the JSON data from your API
    fetch('http://127.0.0.1:8000/datasets', {
      method: 'GET',
      headers: {
        'x-key': 'cD_oedsk1urQDiFjdmP09lvVGOsH28gY10fUJXYe5zc'
      }
    })
      .then(response => response.json())
      .then(data => {
        setDatasets(data);
      })
      .catch(error => console.error('Error fetching data:', error));
  }, []);

  const handleCardClick = (datasetName) => {
    alert(`Clicked ${datasetName}`);
    // Perform any action here, like navigation or showing more info
  };

  return (
    <Box p={6}>
      <Heading as="h1" size="xl" mb={6}>
        Dataset List
      </Heading>
      <SimpleGrid columns={[1, 2, 3]} spacing={8}>
        {datasets.map((dataset) => (
          <Box
            key={dataset.id}
            borderWidth="1px"
            borderRadius="lg"
            overflow="hidden"
            p={5}
            shadow="md"
            transition="transform 0.2s"
            _hover={{ transform: 'scale(1.05)', cursor: 'pointer' }}
            onClick={() => handleCardClick(dataset.name)}
          >
            <Heading as="h2" size="md" mb={4}>
              {dataset.name}
            </Heading>
            <Text>Domain: {dataset.domain}</Text>
          </Box>
        ))}
      </SimpleGrid>
    </Box>
  );
}

export default App;
