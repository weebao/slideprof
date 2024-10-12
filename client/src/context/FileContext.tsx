import React, { createContext, useState, ReactNode, useContext, useMemo } from "react";

interface FileContextType {
  file: File | null;
  addFile: (file: File) => void;
  clearFile: () => void;
}

const FileContext = createContext<FileContextType | undefined>(undefined);

export const FileProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [file, setFile] = useState<File | null>(null);

  const addFile = (newFile: File) => {
    console.log("File added to context:", newFile);
    setFile(newFile);
  };
  const clearFile = () => setFile(null); // Function to reset the file

  const value = useMemo(() => ({ file, addFile, clearFile }), [file]);

  return (
    <FileContext.Provider value={value}>
      {children}
    </FileContext.Provider>
  );
};

export const useFile = (): FileContextType => {
  const context = useContext(FileContext);
  if (context === undefined) {
    throw new Error("useFile must be used within a FileProvider");
  }
  return context;
};
