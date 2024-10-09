import { Box, ChakraProvider } from '@chakra-ui/react';
import React from 'react';
import { Navigate, Route, BrowserRouter as Router, Routes } from 'react-router-dom';
import DatasetsPage from './pages/DatasetsPage';
import LoginPage from './pages/LoginPage';
import ProblemsPage from './pages/ProblemsPage';

const PrivateRoute = ({ children }) => {
    const apiKey = localStorage.getItem('apiKey');
    return apiKey ? children : <Navigate to="/login" />;
};

function App() {
    return (
        <ChakraProvider>
            <Router>
                <Box minHeight="100vh" bg="gray.50">
                    <Routes>
                        <Route path="/login" element={<LoginPage />} />
                        <Route path="/" element={
                            <PrivateRoute>
                                <DatasetsPage />
                            </PrivateRoute>
                        } />
                        <Route path="/datasets/:datasetId/problems" element={
                            <PrivateRoute>
                                <ProblemsPage />
                            </PrivateRoute>
                        } />
                    </Routes>
                </Box>
            </Router>
        </ChakraProvider>
    );
}

export default App;