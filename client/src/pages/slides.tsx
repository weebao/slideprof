import { useState, useEffect } from "react";
import { Chat } from "@/components/chat";
import { NextPage } from "next";
import dynamic from "next/dynamic";
import { useMutation } from "@tanstack/react-query";
import { ask } from "@/services/questionApi";
import { useFile } from "@/context/FileContext";
import { syncFuncWithMessages } from "@/utils/format.js";
import { LatexText } from "@/components/latex";
import { sync } from "framer-motion";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const Slides: NextPage = () => {
  const { file } = useFile();
  const [selectedPage, setSelectedPage] = useState(1);
  const [isDragboxActive, setIsDragboxActive] = useState(false);
  const [dragboxCoords, setDragboxCoords] = useState([0, 0, 0, 0]);
  const [slideCoords, setSlideCoords] = useState([0, 0]);
  const [latexList, setLatexList] = useState<any>([]);

  const chatMutation = useMutation({
    mutationFn: (question: string) =>
      ask(
        file?.name ?? "lecture7.pdf",
        selectedPage,
        question,
        dragboxCoords.map((coord, i) => (coord - slideCoords[i % 2]) / slideCoords[(i % 2) + 2])
      ),
    onSuccess: (data) => {
      syncFuncWithMessages(
        data.message.steps.map((step: any) => step.explanation),
        (x: any, i: number) => {
          const step = data.message.steps[i];
          syncFuncWithMessages(step.items.map((item: any) => item.item), (x: any, i: number) => {
            setLatexList((prev: any) => [...prev, [x, step.items[i].coords]]);
          });
        }
      );
    },
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
      {latexList && latexList.length !== 0 ? (
        latexList.map((latex: any, i: number) => (
          <LatexText text={latex[0]} x={latex[1][0] * slideCoords[2] + slideCoords[0]} y={latex[1][1] * slideCoords[3] + slideCoords[1]} />
        ))
      ) : null}
    </div>
  );
};

export default Slides;
