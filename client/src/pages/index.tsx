import React, { createContext, useContext, useState } from "react";
import { NextPage } from "next";
import { useRouter } from "next/router";
import { Upload, CheckCircle, Loader2 } from "lucide-react";
import { useMutation } from "@tanstack/react-query";
import { upload } from "@/services/uploadApi";
import { Button } from "@/components/ui/button";
import { useFile } from "@/context/FileContext";
import { DragBox } from "@/components/dragbox";
import { LatexText } from "@/components/latex";


const Home: NextPage = () => {
  const router = useRouter();
  const [isDragging, setIsDragging] = useState(false);
  const [isUploaded, setIsUploaded] = useState(false);
  const a = useFile();
  const addFile = a.addFile

  const uploadMutation = useMutation({
    mutationFn: upload,
  });

  const handleDragOver = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  };
  
  const handleDragLeave = () => {
    setIsDragging(false);
  };

  const uploadFile = async (file: File) => {
    addFile(file);
    setIsUploaded(true);
    await uploadMutation.mutate(file);
    setTimeout(() => {
      router.push("/slides");
    }, 100);
  }
  
  const handleDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      console.log("File dropped", e.dataTransfer.files[0]);
      uploadFile(e.dataTransfer.files[0]);
      e.dataTransfer.clearData(); // Clear drag data
    }
  };

  return (
    <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 sm:py-24">
      <div className="text-center">
        <h1 className="text-4xl tracking-tight font-extrabold text-gray-900 sm:text-5xl md:text-6xl">
          Master Your Lecture Slides with AI-Powered
          <span className="text-primary"> Visualizations</span>
        </h1>
        <p className="mt-3 max-w-md mx-auto text-base text-gray-500 sm:text-lg md:mt-5 md:text-xl md:max-w-3xl">
          Say goodbye to poorly annotated slides. Upload your lecture slides and watch as our AI explains complex concepts while drawing directly on them.
        </p>
      </div>

      {/* Drag and drop area */}
      <div className={`mt-10 max-w-xl mx-auto border-4 border-dashed rounded-lg p-12 text-center ${
          isDragging ? "border-primary bg-primary/10" : "border-gray-300"
        } transition-colors duration-300 ease-in-out`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}>
        {uploadMutation.isPending ? (
          <div className="text-primary flex flex-col items-center">
            <Loader2 className="h-16 w-16 animate-spin" />
            <p className="text-xl font-semibold">Loading up your PDF...</p>
          </div>
        ) : isUploaded ? (
          <div className="text-primary flex flex-col items-center">
            <CheckCircle className="w-16 h-16 mb-4" />
            <p className="text-xl font-semibold">Upload Successful!</p>
            <p className="mt-2">Your lecture slides are being rendered.</p>
          </div>
        ) : (
          <>
            <Upload className="mx-auto h-12 w-12 text-gray-400" />
            <p className="mt-2 text-base text-gray-600">Drag and drop your lecture slides (PDF) here, or</p>
            <input
              type="file"
              accept=".pdf"
              className="hidden"
              id="file-upload"
              onChange={(e) => {
                if (e.target.files && e.target.files.length > 0) {
                  uploadFile(e.target.files[0]);
                }
              }}
            />
            <Button className="mt-2" variant="outline" asChild>
              <label htmlFor="file-upload">Select file</label>
            </Button>
          </>
        )}
      </div>

      {/* Features section */}
      <div className="mt-20">
        <h2 className="text-3xl font-bold text-gray-900 text-center">Why Students Love SlideProf</h2>
        <div className="mt-10 grid gap-10 md:grid-cols-3">
          {[
            { title: "AI-Powered Explanations", description: "Our advanced AI breaks down complex topics from your lecture slides with ease." },
            {
              title: "Interactive Visual Learning",
              description: "Watch as the AI draws explanations directly on your slides, enhancing understanding.",
            },
            { title: "Exam-Ready in Minutes", description: "Quickly grasp key concepts and prepare for exams more effectively." },
          ].map((feature, index) => (
            <div key={index} className="text-center">
              <h3 className="text-lg font-medium text-gray-900">{feature.title}</h3>
              <p className="mt-2 text-base text-gray-500">{feature.description}</p>
            </div>
          ))}
        </div>
      </div>

      {/* Testimonial section */}
      <div className="mt-20 bg-primary text-white rounded-lg p-8">
        <blockquote className="italic text-center text-lg">
          "SlideProf helped me visualize quantum multi-variable Count-Min Sketch BST CSS SPX works. The AI's explanations and
          drawings made everything click just before my final exam!"
        </blockquote>
        <p className="mt-4 text-center font-semibold">- Bao Dang, not the brightest student</p>
      </div>

      {/* Call to Action */}
      <div className="mt-20 text-center">
        <h2 className="text-3xl font-extrabold text-gray-900">Ready to Ace Your Exams?</h2>
        <p className="mt-4 text-xl text-gray-600">Upload your lecture slides now and start learning smarter!</p>
        <Button className="mt-8 text-lg px-8 py-3" size="lg">
          Get Started for Free
        </Button>
      </div>
    </main>
  );
};

export default Home;

