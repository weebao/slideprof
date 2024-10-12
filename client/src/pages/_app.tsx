import "../globals.css";
import "../styles/AnnotationLayer.css";
import "../styles/TextLayer.css";

import React from "react";
import type { AppProps } from "next/app";
import Head from "next/head";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { FileProvider } from "@/context/FileContext";

const App = ({ Component, pageProps }: AppProps) => {
  return (
    <>
      <Head>
        <title>SlidesProf</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
        {/* Link to favicon */}
        <link rel="icon" href="/favicon.ico" />
        {/* Optional: Add other favicon sizes */}
        <link rel="icon" type="image/png" sizes="32x32" href="/favicon-32x32.png" />
        <link rel="icon" type="image/png" sizes="16x16" href="/favicon-16x16.png" />
      </Head>
      <Navbar />
      <FileProvider>
        <Component {...pageProps} />
      </FileProvider>
      <Footer />
    </>
  );
};

export default App;
