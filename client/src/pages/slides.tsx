import { useState } from "react";
import { Chat } from "@/components/chat";
import { NextPage } from "next";
import dynamic from "next/dynamic";
import { useMutation } from "@tanstack/react-query";
import { ask } from "@/services/questionApi";
import { useFile } from "@/context/FileContext";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const Slides: NextPage = () => {
  const { file } = useFile();
  const [selectedPage, setSelectedPage] = useState(1);
  const [isDragboxActive, setIsDragboxActive] = useState(false);
  const [dragboxCoords, setDragboxCoords] = useState([0, 0, 0, 0]);
  const [slideCoords, setSlideCoords] = useState([0, 0]);

  const chatMutation = useMutation({
    mutationFn: (question: string) =>
      ask(
        file?.name ?? "lecture7.pdf",
        selectedPage,
        question,
        dragboxCoords.map((coord, i) => coord - slideCoords[i % 2])
      ),
  });

  const toggleDragbox = () => setIsDragboxActive((prev) => !prev);
  return (
    <div className="h-[calc(100dvh-200px)] flex">
      <SlidesComponent
        file={file}
        isDragboxActive={isDragboxActive}
        setSelectedPage={setSelectedPage}
        setDragboxCoords={setDragboxCoords}
        setSlideCoords={setSlideCoords}
      />
      <div className="fixed bottom-4 right-4 w-80 h-96 shadow-l">
        <Chat toggleFunction={toggleDragbox} chatMutation={chatMutation} />
      </div>
    </div>
  );
};

export default Slides;
