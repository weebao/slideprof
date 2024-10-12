import React, { useState, useEffect, useCallback } from "react";
import { NextPage } from "next";
import { useResizeObserver } from "@wojtekmaj/react-hooks";
import { useFile } from "@/context/FileContext"; // Assuming FileContext provides the uploaded file
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { pdfjs, Document, Page } from "react-pdf";

import type { PDFDocumentProxy } from "pdfjs-dist";
import { DragBox } from "./dragbox";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();
const resizeObserverOptions = {};

const options = {
  cMapUrl: "/cmaps/",
  standardFontDataUrl: "/standard_fonts/",
};


export default function Slides() {
  const { file } = useFile();
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [containerRef, setContainerRef] = useState<HTMLElement | null>(null);
  const [containerWidth, setContainerWidth] = useState<number>();

  const onResize = useCallback<ResizeObserverCallback>((entries) => {
    const [entry] = entries;

    if (entry) {
      setContainerWidth(entry.contentRect.width);
    }
  }, []);

  useResizeObserver(containerRef, resizeObserverOptions, onResize);

  // Effect to create an object URL for the uploaded file
  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
      setLoading(false); // Mark as done loading
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  if (loading) {
    return <p>Loading PDF...</p>;
  }

  // Callback when the document is successfully loaded
  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  // Handlers for switching pages
  const goToPrevPage = () => setPageNumber((prev) => (prev > 1 ? prev - 1 : prev));
  const goToNextPage = () => setPageNumber((prev) => (prev < (numPages || 0) ? prev + 1 : prev));

  // Handle when no file is uploaded
  if (!file) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-xl text-gray-600">No file uploaded. Please upload a PDF file.</p>
      </div>
    );
  }

  // Log the pdfUrl to verify it's correct
  console.log("PDF URL:", pdfUrl);

  return (
    <div className=" min-h-screen bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full h-full">
        <h1 className="text-2xl font-bold text-center mb-6">Slide Viewer</h1>

        {/* PDF Display */}
        <DragBox>
          <div ref={setContainerRef} className="w-full h-full">
            <Document
              file={file}
              onLoadSuccess={onDocumentLoadSuccess}
              onLoadError={console.error} // Log errors if loading fails
              className="flex justify-center items-center w-full h-full"
              options={options}
            >
              <Page pageNumber={pageNumber} width={containerWidth ? Math.min(containerWidth, 800) : 800} />
            </Document>
          </div>
        </DragBox>

        {/* Navigation Buttons */}
        <div className="relative mt-6">
          <div className="absolute top-1/2 left-0 transform -translate-y-1/2 -translate-x-1/2">
            <Button onClick={goToPrevPage} disabled={pageNumber <= 1} variant="outline" size="icon" className="rounded-full bg-white shadow-md">
              <ChevronLeft className="h-6 w-6" />
              <span className="sr-only">Previous slide</span>
            </Button>
          </div>
          <div className="absolute top-1/2 right-0 transform -translate-y-1/2 translate-x-1/2">
            <Button
              onClick={goToNextPage}
              disabled={pageNumber >= (numPages || 0)}
              variant="outline"
              size="icon"
              className="rounded-full bg-white shadow-md"
            >
              <ChevronRight className="h-6 w-6" />
              <span className="sr-only">Next slide</span>
            </Button>
          </div>
        </div>

        {/* Page number navigation */}
        <div className="flex justify-center items-center mt-4 space-x-2">
          {Array.from({ length: numPages || 0 }, (_, i) => (
            <Button
              key={i}
              variant={pageNumber === i + 1 ? "default" : "outline"}
              size="sm"
              onClick={() => setPageNumber(i + 1)}
              className="w-8 h-8 p-0"
            >
              {i + 1}
            </Button>
          ))}
        </div>

        {/* Display current page */}
        <p className="text-center mt-4 text-sm text-gray-600">
          Page {pageNumber} of {numPages}
        </p>
      </div>
    </div>
  );
}
