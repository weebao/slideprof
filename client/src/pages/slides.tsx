import { NextPage } from "next";
import dynamic from "next/dynamic";
const SlidesComponent = dynamic(() => import("../components/slides.js"), { ssr: false });

const Slides: NextPage = () => {
  return <SlidesComponent />;
};

export default Slides;