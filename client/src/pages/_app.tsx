import "../globals.css";
import "../styles/AnnotationLayer.css";
import "../styles/TextLayer.css";

import React from "react";
import type { AppProps } from "next/app";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import Head from "next/head";
import Navbar from "@/components/navbar";
import Footer from "@/components/footer";
import { FileProvider } from "@/context/FileContext";

const App = ({ Component, pageProps }: AppProps) => {
  const queryClient = new QueryClient();
  
  return (
    <>
      <Head>
        <title>SlidesProf</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
      </Head>
      <Navbar />
      <QueryClientProvider client={queryClient}>
        <FileProvider>
          <Component {...pageProps} />
        </FileProvider>
      </QueryClientProvider>
      <Footer />
    </>
  );
};

export default App;
