import { useState, useEffect } from "react";
import { Chat } from "@/components/chat";
import { NextPage } from "next";
import dynamic from "next/dynamic";
import { useMutation } from "@tanstack/react-query";
import { ask } from "@/services/questionApi";
import { useFile } from "@/context/FileContext";
import TreeGraph from "@/components/tree";
import { syncFuncWithMessages } from "@/utils/format.js";
import { LatexText } from "@/components/latex";
import { sync } from "framer-motion";
import { Arrow, SmallNextLineArrow, BigNextLineArrow } from "@/components/icons";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const arrowList: any = {
  "arrow-right": () => <Arrow />,
  "arrow-left": () => <Arrow className="transform rotate-180" />,
  "next-line-arrow-right": () => <SmallNextLineArrow />,
  "next-line-arrow-left": () => <SmallNextLineArrow className="transform rotate-180" />,
}

const Slides: NextPage = () => {
  const { file } = useFile();
  const [selectedPage, setSelectedPage] = useState(1);
  const [isDragboxActive, setIsDragboxActive] = useState(false);
  const [dragboxCoords, setDragboxCoords] = useState([0, 0, 0, 0]);
  const [slideCoords, setSlideCoords] = useState([0, 0]);
  const [latexList, setLatexList] = useState<any>([]);
  const [treeData, setTreeData] = useState<any>(null);

  const chatMutation = useMutation({
    mutationFn: (question: string) =>
      ask(
        file?.name ?? "lecture7.pdf",
        selectedPage,
        question,
        dragboxCoords.map((coord, i) => (coord - slideCoords[i % 2]) / slideCoords[(i % 2) + 2])
      ),
    onSuccess: (data) => {
      if (data.message.type === "text") {
        syncFuncWithMessages(
          data.message.steps.map((step: any) => step.explanation),
          (x: any, i: number) => {
            const step = data.message.steps[i];
            syncFuncWithMessages(
              step.items.map((item: any) => item.item),
              (x: any, i: number) => {
                setLatexList((prev: any) => [...prev, [x, step.items[i].coords]]);
              }
            );
          }
        );
      } else if (data.message.type === "tree") {
        syncFuncWithMessages(
          data.message.steps.map((step: any) => step.explanation),
          (x: any, i: number) => {
            setTreeData([data, data.message.coords]);
          }
        );
      }
    },
  });

  useEffect(() => {
    setLatexList([]);
    setTreeData(null);
    setIsDragboxActive(false);
  }, [selectedPage]);

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
        <Chat isDragboxActive={isDragboxActive} setIsDragboxActive={setIsDragboxActive} chatMutation={chatMutation} />
      </div>
      {latexList && latexList.length !== 0
        ? latexList.map((latex: any, i: number) => {
          if (latex[0] === "erase") {
            return (
              <div key={i} className="absolute bg-white w-lg h-lg"></div>
            )
          } else if (arrowList[latex[0]]) {
            return (
              <div key={i} className="absolute">
                {arrowList[latex[0]]()}
              </div>
            )
          } else {
            return (<LatexText text={latex[0]} x={latex[1][0] * slideCoords[2] + slideCoords[0]} y={latex[1][1] * slideCoords[3] + slideCoords[1]} />);
          }
        })
        : null}
      {treeData ? (
        <TreeGraph data={treeData[0]} x={treeData[1][0] * slideCoords[2] + slideCoords[0]} y={treeData[1][1] * slideCoords[3] + slideCoords[1]} />
      ) : null}
    </div>
  );
};

export default Slides;
