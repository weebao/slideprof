import "../globals.css";
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
