import React, { useState, useRef, useCallback, useEffect } from "react";

interface BoxCoordinates {
  startX: number;
  startY: number;
  endX: number;
  endY: number;
}

interface DragBoxProps {
  isActive?: boolean;
  children?: React.ReactNode;
  setCoords: React.Dispatch<React.SetStateAction<number[]>>;
}

export const DragBox: React.FC<DragBoxProps> = ({ isActive, children, setCoords }) => {
  const [isDrawing, setIsDrawing] = useState(false);
  const [box, setBox] = useState<BoxCoordinates | null>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  const startDrawing = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isActive) return;
    if (containerRef.current) {
      const { left, top } = containerRef.current.getBoundingClientRect();
      const startX = e.clientX - left;
      const startY = e.clientY - top;
      setBox({ startX, startY, endX: startX, endY: startY });
      setIsDrawing(true);
    }
  };

  const draw = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!isDrawing || !containerRef.current || !isActive) return;
    const { left, top } = containerRef.current.getBoundingClientRect();
    const endX = e.clientX - left;
    const endY = e.clientY - top;
    setBox((prevBox) => (prevBox ? { ...prevBox, endX, endY } : null));
  };

  const stopDrawing = () => {
    if (box) {
      setCoords([Math.min(box.startX, box.endX), Math.min(box.startY, box.endY), Math.abs(box.endX - box.startX), Math.abs(box.endY - box.startY)]);
    }
    setIsDrawing(false);
  };

  useEffect(() => {
    if (!isActive) {
      setBox(null);
      setIsDrawing(false);
    }
  }, [isActive]);

  const boxStyle = box
    ? {
        left: `${Math.min(box.startX, box.endX)}px`,
        top: `${Math.min(box.startY, box.endY)}px`,
        width: `${Math.abs(box.endX - box.startX)}px`,
        height: `${Math.abs(box.endY - box.startY)}px`,
      }
    : {};

  return (
    <div
      ref={containerRef}
      className="relative w-full h-full"
      onMouseDown={startDrawing}
      onMouseMove={draw}
      onMouseUp={stopDrawing}
      onMouseLeave={stopDrawing}
    >
      <div className={isActive ? "select-none" : ""}>{children}</div>
      {box && <div className="absolute border-2 border-primary bg-primary/10 rounded-md" style={boxStyle}></div>}
    </div>
  );
};
