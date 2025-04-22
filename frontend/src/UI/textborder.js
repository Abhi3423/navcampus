import React from 'react';

function Textborder({ text, CustomBold }) {
    return (
        <div className="relative">
            <span className="absolute text-blue">{text}</span>
            <span className={`text-white ${CustomBold}`}>{text}</span>
        </div>
    );
}

export default Textborder;

