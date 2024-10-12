import React from 'react';
import 'katex/dist/katex.min.css';
import Latex from "react-latex-next";

interface LatexProps {
  text: string;
  x: number;
  y: number;
}

export const LatexText: React.FC<LatexProps> = ({ text, x, y }) => {
  return (
    <div className="absolute" style={{ left: x, top: y }}>
      <Latex>$${text}$$</Latex>
    </div>
  );
};