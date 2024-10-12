import React, { useState, useEffect } from "react";
import { NextPage } from "next";
import { useFile } from "@/context/FileContext";
import { ChevronLeft, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Document, Page } from "@react-pdf/renderer";

const Slides: NextPage = () => {
  const { file } = useFile();
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  function onDocumentLoadSuccess({ numPages }: { numPages: number }) {
    setNumPages(numPages);
  }

  const goToPrevPage = () => setPageNumber((prev) => (prev > 1 ? prev - 1 : prev));
  const goToNextPage = () => setPageNumber((prev) => (prev < (numPages || 0) ? prev + 1 : prev));

  if (!file) {
    return (
      <div className="flex items-center justify-center h-screen">
        <p className="text-xl text-gray-600">No file uploaded. Please upload a PDF file.</p>
      </div>
    );
  }

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-gray-100 p-4">
      <div className="bg-white rounded-lg shadow-lg p-6 w-full max-w-4xl">
        <h1 className="text-2xl font-bold text-center mb-6">Slide Viewer</h1>
        <div className="relative">
          // TODO
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
        <p className="text-center mt-4 text-sm text-gray-600">
          Page {pageNumber} of {numPages}
        </p>
      </div>
    </div>
  );
}
