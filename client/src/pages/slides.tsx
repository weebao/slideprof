import { useState } from "react";
import { Chat } from "@/components/chat";
import { NextPage } from "next";
import dynamic from "next/dynamic";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const Slides: NextPage = () => {
  const [isDragboxActive, setIsDragboxActive] = useState(false);
  const [dragboxCoords, setDragboxCoords] = useState([0, 0, 0, 0]);
  const [slideDimension, setSlideDimension] = useState([0, 0]);

  const toggleDragbox = () => setIsDragboxActive((prev) => !prev);
  return (
    <div className="h-[max(100%,calc(100dvh-200px)] flex">
      <SlidesComponent isDragboxActive={isDragboxActive} setDragboxCoords={setDragboxCoords} setSlideDimension={setSlideDimension} />
      <div className="fixed bottom-4 right-4 w-80 h-96 shadow-l">
        <Chat toggleFunction={toggleDragbox} />
      </div>
    </div>
  );
};

export default Slides;
