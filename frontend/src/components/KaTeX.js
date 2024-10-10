import katex from 'katex';
import 'katex/dist/katex.min.css';
import React from 'react';

const KaTeX = ({ children, block = false, errorColor = '#cc0000' }) => {
    const renderKaTeX = (content) => {
        return content.split(/(\$\$[\s\S]*?\$\$|\$[\s\S]*?\$)/).map((text, index) => {
            if (index % 2 === 1) {
                const isDisplayMode = text.startsWith('$$');
                const formula = isDisplayMode ? text.slice(2, -2) : text.slice(1, -1);
                return (
                    <span
                        key={index}
                        dangerouslySetInnerHTML={{
                            __html: katex.renderToString(formula, {
                                displayMode: isDisplayMode,
                                throwOnError: false,
                                errorColor,
                            }),
                        }}
                    />
                );
            }
            return <span key={index}>{text}</span>;
        });
    };

    return (
        <div className={block ? 'katex-block' : 'katex-inline'}>
            {renderKaTeX(children)}
        </div>
    );
};

export default KaTeX;