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
  "arrow-right": (x: number, y: number) => <Arrow style={{ left: `${x + 5}px`, top: `${y + 15}px` }} className="absolute w-8 h-8" />,
  "arrow-left": (x: number, y: number) => <Arrow style={{ left: `${x + 5}px`, top: `${y + 15}px` }} className="absolute transform rotate-180 w-8 h-8" />,
  "new-line-arrow-right": (x: number, y: number) => <BigNextLineArrow style={{ left: `${x}px`, top: `${y + 5}px` }} className="absolute w-8 h-8" />,
  "new-line-arrow-left": (x: number, y: number) => (
    <BigNextLineArrow style={{ left: `${x}px`, top: `${y + 5}px` }} className="absolute transform rotate-180 w-8 h-8" />
  ),
};

// if (data.message.type === "text") {
//   syncFuncWithMessages(
//     data.message.steps.map((step: any) => step.explanation),
//     (x: any, i: number) => {
//       const step = data.message.steps[i];
//       syncFuncWithMessages(
//         step.items.map((item: any) => item.item),
//         (x: any, i: number) => {
//           setLatexList((prev: any) => [...prev, [x, step.items[i].coords]]);
//         }
//       );
//     }
//   );
// }

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
              step.items.map((item: any) => item.item + "     "),
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
            setTreeData([data.message.steps[i].tree, data.message.steps[i].coords]);
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
    <div className="h-full flex">
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
            const name = latex[0].trim();
            console.log(latex[0].trim(), name === "erase", name in arrowList);
            const x = Math.round(latex[1][0] * slideCoords[2] + slideCoords[0]);
            const y = Math.round(latex[1][1] * slideCoords[3] + slideCoords[1]);
            if (name === "erase") {
              return <div key={i} style={{ left: `${x}px`, top: `${y}px` }} className="absolute bg-white w-[700px] h-60" />;
            } else if (arrowList[name]) {
              return arrowList[name](x, y);
            } else {
              return <LatexText key={i} text={latex[0]} x={x} y={y} />;
            }
          })
        : null}
      {treeData ? (
        <div className="absolute" style={{ left: `${slideCoords[0]}px`, top: `${slideCoords[1]}px` }}>
          <TreeGraph
            data={treeData[0]}
            x={Math.round(treeData[1][0] * slideCoords[2] + slideCoords[0])}
            y={Math.round(treeData[1][1] * slideCoords[3] + slideCoords[1])}
          />
        </div>
      ) : null}
    </div>
  );
};

export default Slides;
