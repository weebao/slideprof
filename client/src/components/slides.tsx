import React, { useState, useEffect, useCallback, useRef } from "react";
import Link from "next/link";
import { pdfjs, Document, Page } from "react-pdf";
import { ask } from "@/services/questionApi";
import { useMutation } from "@tanstack/react-query";
import { useResizeObserver } from "@wojtekmaj/react-hooks";
import { useFile } from "@/context/FileContext";
import { ChevronLeft, ChevronRight, Loader2, Frown } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Carousel, CarouselContent, CarouselItem, CarouselNext, CarouselPrevious, type CarouselApi } from "@/components/ui/carousel";
import TreeGraph from './tree';
import type { PDFDocumentProxy } from "pdfjs-dist";
import { DragBox } from "./dragbox";
import { useIsTouchDevice } from "@/hooks/useIsTouchDevice";

pdfjs.GlobalWorkerOptions.workerSrc = new URL("pdfjs-dist/build/pdf.worker.min.mjs", import.meta.url).toString();
const resizeObserverOptions = {};

const options = {
  cMapUrl: "/cmaps/",
  standardFontDataUrl: "/standard_fonts/",
};

const maxWidth = 800;

interface SlidesProps {
  file: File | null;
  isDragboxActive?: boolean;
  setSelectedPage: React.Dispatch<React.SetStateAction<number>>;
  setDragboxCoords: React.Dispatch<React.SetStateAction<number[]>>;
  setSlideCoords: React.Dispatch<React.SetStateAction<number[]>>;
}

const Slides: React.FC<SlidesProps> = ({ file, isDragboxActive, setSelectedPage, setDragboxCoords, setSlideCoords }) => {
  const { isTouchDevice } = useIsTouchDevice();
  const [carouselApi, setCarouselApi] = useState<CarouselApi>();
  const [numPages, setNumPages] = useState<number | null>(null);
  const [pageNumber, setPageNumber] = useState(1);
  const [inputValue, setInputValue] = useState("1"); // Input value for page number
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const slideRef = useRef<HTMLDivElement>(null);
  const [containerRef, setContainerRef] = useState<HTMLElement | null>(null);
  const [containerWidth, setContainerWidth] = useState<number>();

  const onResize = useCallback<ResizeObserverCallback>((entries) => {
    const [entry] = entries;

    if (entry) {
      setContainerWidth(entry.contentRect.width);
    }
  }, []);

  useResizeObserver(containerRef, resizeObserverOptions, onResize);

  // Callback when the document is successfully loaded
  const onDocumentLoadSuccess = ({ numPages }: { numPages: number }) => {
    setNumPages(numPages);
  };

  // Handlers for switching pages
  const goToPrevPage = () => setPageNumber((prev) => (prev > 1 ? prev - 1 : prev));
  const goToNextPage = () => setPageNumber((prev) => (prev < (numPages || 0) ? prev + 1 : prev));

  // Handle input change for page number
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;

    // Only allow numbers
    if (/^\d*$/.test(value)) {
      setInputValue(value); // Update the input value
    }
  };

  // Handle Enter key for slide input nagiagtion
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter" && inputValue) {
      navigateToPage();
    }
  };

  //Handle losing focus from input (onBlur event)
  const handleInputBlur = () => {
    if (inputValue) {
      navigateToPage();
    }
  };

  // Function to navigate to a specific page
  const navigateToPage = () => {
    const targetPage = parseInt(inputValue, 10);

    // Only navigate if the value is within the valid range
    if (targetPage >= 1 && targetPage <= (numPages || 1)) {
      setPageNumber(targetPage); // Nagivate to the target page
    } else {
      alert("Invalid page number. Please enter a valid page number.");
      setInputValue(pageNumber.toString()); // Reset the input
    }
  };
  
  // Effect to create an object URL for the uploaded file
  useEffect(() => {
    if (file) {
      const url = URL.createObjectURL(file);
      setPdfUrl(url);
      setLoading(false); // Mark as done loading
      return () => URL.revokeObjectURL(url);
    }
  }, [file]);

  // Syn the input value with the current page number whenver the page number changes
  useEffect(() => {
    setInputValue(pageNumber.toString());
  }, [pageNumber]);

  useEffect(() => {
    if (!carouselApi) {
      return;
    }
    setPageNumber(carouselApi.selectedScrollSnap() + 1);

    carouselApi.on("scroll", () => {
      setPageNumber(carouselApi.selectedScrollSnap() + 1);
      setSelectedPage(carouselApi.selectedScrollSnap() + 1);
    });
  }, [carouselApi]);

  useEffect(() => {
    carouselApi?.scrollTo(pageNumber - 1);
  }, [pageNumber]);

  useEffect(() => {
    if (slideRef.current) {
      const { offsetLeft, offsetTop } = slideRef.current;
      const { width, height } = slideRef.current.getBoundingClientRect();
      setSlideCoords([offsetLeft, offsetTop, width, height]);
    }
  }, [slideRef.current]);

  return (
    <div className="w-full h-full flex-1 bg-gray-100 p-4">
      {file ? (
        loading ? (
          <div>
            <Loader2 className="h-16 w-16 animate-spin text-primary" />
            <h2 className="mt-4 text-xl font-semibold text-gray-700">Loading...</h2>
            <p className="mt-2 text-sm text-gray-500">Please wait while we prepare your slides.</p>
          </div>
        ) : (
          <div className="w-full h-full">
            <DragBox isActive={isDragboxActive} setCoords={setDragboxCoords}>
              <div ref={setContainerRef}>
                <Document
                  file={file}
                  onLoadSuccess={onDocumentLoadSuccess}
                  onLoadError={console.error} // Log errors if loading fails
                  className="w-full h-full"
                  options={options}
                >
                  <Carousel setApi={setCarouselApi} opts={{ watchDrag: isTouchDevice && !isDragboxActive }}>
                    <CarouselContent>
                      {Array.from(new Array(numPages), (_el, index) => (
                        <CarouselItem key={index}>
                          <Page
                            inputRef={index === 0 ? slideRef : null}
                            key={`page_${index + 1}`}
                            pageNumber={index + 1}
                            width={containerWidth ? Math.min(containerWidth, maxWidth) : maxWidth}
                            className={`mx-auto max-w-[800px]`}
                          />
                        </CarouselItem>
                      ))}
                    </CarouselContent>
                  </Carousel>
                </Document>
              </div>
            </DragBox>

            {/* Navigation Buttons */}
            <div className="relative mt-6 flex justify-center items-center space-x-4">
              <Button onClick={goToPrevPage} disabled={pageNumber <= 1} variant="outline" size="icon" className="rounded-full bg-white shadow-md">
                <ChevronLeft className="h-6 w-6" />
                <span className="sr-only">Previous slide</span>
              </Button>

              {/* Page input and total page display */}
              <div className="flex items-center space-x-2">
                <input
                  type="text"
                  value={inputValue}
                  onChange={handleInputChange}
                  onKeyDown={handleInputKeyDown}
                  onBlur={handleInputBlur}
                  className="w-12 text-center border rounded-md p-1"
                />
                <span className="text-gray-600">/ {numPages}</span>
              </div>

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
        )
      ) : (
        <div className="w-full h-[calc(100dvh-200px)] flex flex-col items-center justify-center">
          <Frown className="w-12 h-12 mb-2" />
          <p className="text-xl text-center text-gray-600">
            No file uploaded. Please upload a PDF file{" "}
            <Link href="/">
              <span className="text-primary underline">here</span>
            </Link>
            .
          </p>
        </div>
      )}
    </div>
  );
};

export default Slides;
