import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { Button, HStack, Input, Text } from '@chakra-ui/react';
import React, { useEffect, useState } from 'react';

const Pagination = ({
    currentPage,
    totalPages,
    onPageChange,
    editableNumber,
    onEditableNumberChange,
    onEditableNumberSubmit,
    middleElementsCount = 5
}) => {
    const [inputValue, setInputValue] = useState(editableNumber);

    useEffect(() => {
        setInputValue(editableNumber);
    }, [editableNumber]);

    const handleLocalChange = (e) => {
        setInputValue(e.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        onEditableNumberSubmit(inputValue);
    };

    const renderProblemSelectionMenu = () => {
        const items = [];
        const halfMiddle = Math.floor(middleElementsCount / 2);

        // First page
        if (currentPage === 0) {
            items.push(
                <form key="input-start" onSubmit={handleSubmit} style={{ margin: 0 }}>
                    <Input
                        size="sm"
                        width="60px"
                        textAlign="center"
                        value={inputValue}
                        onChange={handleLocalChange}
                    />
                </form>
            );
        } else {
            items.push(
                <Button
                    key={0}
                    size="sm"
                    variant="ghost"
                    onClick={() => onPageChange(0)}
                >
                    1
                </Button>
            );
        }

        // Show ellipsis after first page if needed
        if (currentPage > halfMiddle + 1) {
            items.push(<Text key="ellipsis-start">...</Text>);
        }

        // Middle pages
        const start = Math.max(1, Math.min(currentPage - halfMiddle, totalPages - middleElementsCount - 1));
        const end = Math.min(start + middleElementsCount - 1, totalPages - 2);

        for (let i = start; i <= end; i++) {
            if (i === currentPage) {
                items.push(
                    <form key={`input-${i}`} onSubmit={handleSubmit} style={{ margin: 0 }}>
                        <Input
                            size="sm"
                            width="60px"
                            textAlign="center"
                            value={inputValue}
                            onChange={handleLocalChange}
                        />
                    </form>
                );
            } else {
                items.push(
                    <Button
                        key={i}
                        size="sm"
                        variant="ghost"
                        onClick={() => onPageChange(i)}
                    >
                        {i + 1}
                    </Button>
                );
            }
        }

        // Show ellipsis before last page if needed
        if (currentPage < totalPages - halfMiddle - 2) {
            items.push(<Text key="ellipsis-end">...</Text>);
        }

        // Last page
        if (totalPages > 1) {
            if (currentPage === totalPages - 1) {
                items.push(
                    <form key="input-end" onSubmit={handleSubmit} style={{ margin: 0 }}>
                        <Input
                            size="sm"
                            width="60px"
                            textAlign="center"
                            value={inputValue}
                            onChange={handleLocalChange}
                        />
                    </form>
                );
            } else {
                items.push(
                    <Button
                        key={totalPages - 1}
                        size="sm"
                        variant="ghost"
                        onClick={() => onPageChange(totalPages - 1)}
                    >
                        {totalPages}
                    </Button>
                );
            }
        }

        return items;
    };

    return (
        <HStack spacing={1}>
            <Button
                size="sm"
                onClick={() => onPageChange(currentPage - 1)}
                isDisabled={currentPage === 0}
            >
                <ChevronLeftIcon /> Previous
            </Button>
            {renderProblemSelectionMenu()}
            <Button
                size="sm"
                onClick={() => onPageChange(currentPage + 1)}
                isDisabled={currentPage === totalPages - 1}
            >
                Next <ChevronRightIcon />
            </Button>
        </HStack>
    );
};

export default Pagination;
