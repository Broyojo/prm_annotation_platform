import { Box, Button, Heading, Input, useToast, VStack } from '@chakra-ui/react';
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const LoginPage = () => {
    const [apiKey, setApiKey] = useState('');
    const navigate = useNavigate();
    const toast = useToast();

    const handleSubmit = (e) => {
        e.preventDefault();
        if (apiKey.trim()) {
            localStorage.setItem('apiKey', apiKey);
            navigate('/');
        } else {
            toast({
                title: "Error",
                description: "API Key cannot be empty",
                status: "error",
                duration: 3000,
                isClosable: true,
            });
        }
    };

    return (
        <Box height="100vh" display="flex" alignItems="center" justifyContent="center">
            <form onSubmit={handleSubmit}>
                <VStack spacing={4} align="stretch" width="300px">
                    <Heading as="h1" size="xl" textAlign="center">
                        Login
                    </Heading>
                    <Input
                        placeholder="Enter your API key"
                        value={apiKey}
                        onChange={(e) => setApiKey(e.target.value)}
                    />
                    <Button type="submit" colorScheme="blue">
                        Login
                    </Button>
                </VStack>
            </form>
        </Box>
    );
};

export default LoginPage;