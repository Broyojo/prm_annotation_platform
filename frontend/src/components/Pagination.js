import { ChevronLeftIcon, ChevronRightIcon } from '@chakra-ui/icons';
import { Button, HStack, Input, Text } from '@chakra-ui/react';
import React from 'react';

const Pagination = ({
    currentPage,
    totalPages,
    onPageChange,
    editableNumber,
    onEditableNumberChange,
    onEditableNumberSubmit,
    middleElementsCount = 5
}) => {
    const renderProblemSelectionMenu = () => {
        const items = [];

        const addButton = (index) => {
            if (index === currentPage) {
                items.push(
                    <form key={index} onSubmit={onEditableNumberSubmit}>
                        <Input
                            size="sm"
                            width="60px"
                            textAlign="center"
                            value={editableNumber}
                            onChange={onEditableNumberChange}
                            onBlur={onEditableNumberSubmit}
                        />
                    </form>
                );
            } else {
                items.push(
                    <Button
                        key={index}
                        size="sm"
                        variant="ghost"
                        onClick={() => onPageChange(index)}
                    >
                        {index + 1}
                    </Button>
                );
            }
        };

        const addEllipsis = (key) => {
            items.push(<Text key={key}>...</Text>);
        };

        addButton(0);

        if (currentPage > Math.floor(middleElementsCount / 2) + 1) addEllipsis('start');

        const halfMiddle = Math.floor(middleElementsCount / 2);
        const start = Math.max(1, Math.min(currentPage - halfMiddle, totalPages - middleElementsCount - 1));
        const end = Math.min(start + middleElementsCount - 1, totalPages - 2);

        for (let i = start; i <= end; i++) {
            addButton(i);
        }

        if (currentPage < totalPages - Math.floor(middleElementsCount / 2) - 2) addEllipsis('end');

        if (totalPages > 1) addButton(totalPages - 1);

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