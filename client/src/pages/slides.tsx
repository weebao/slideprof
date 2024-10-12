import { Chat } from "@/components/chat";
import { NextPage } from "next";
import dynamic from "next/dynamic";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const Slides: NextPage = () => {
  return (
    <div className="h-[max(100%,calc(100dvh-200px)] flex">
      <SlidesComponent />
      <div className="fixed bottom-4 right-4 w-80 h-96 shadow-l">
        <Chat />
      </div>
    </div>
  );
};

export default Slides;